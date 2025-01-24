import numpy as np
import pandas as pd
import json
import re
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path

from . import data_ops
from . import query_utils
from .constants import *
from ..algorithms.adtributor import Adtributor, RecursiveAdtributor
from ..core.contribution_calculator import calculate_contribution_by_addition, calculate_contribution_by_multiplication, calculate_contribution_by_division
from ..utils import MathOperations, safe_div, get_current_function, get_enum_member, print_df_as_table
from ..titan.titan_api import TitanApi
from ..db.azure_db_api import AzureDbApi
from ..config.msn_metrics import MSNMetricTree, MSNMetricTreeNode
from ..factor_lib.holiday_impact import HolidayImpactAnalyzer
from ..factor_lib.experiment_impact import ExperimentImpactAnalyzer


class MSNBusinessMetricsAnalyzer:
    def __init__(self, alias_account, titan_token="", metric="", verbose=0):
        """
        alias_account: string, alias account
        metric: string, metric name
        """
        self.alias_account = alias_account
        self.titan_api = TitanApi(alias_account, titan_token)
        self.azure_db_api = AzureDbApi()
        self.verbose = verbose
        self.time_mode = "Day"

        # init metric map
        msn_metric_tree = MSNMetricTree()
        self.metric_map = msn_metric_tree.get_metric_tree()

        # init metric query
        self.metric_query_str = ""
        self.metric_query_map = {}
        self.combine_metric_query_map = {}

        # init metric config and update metric query
        ret = self._initial_metric_config(metric)
        if ret:
            raise Exception(f"Error: metric {metric} is not supported.")
        
        self.metric = metric
        self.most_primary_metric = metric
        self.most_primary_metrics = [metric]
        self.metric_trend = ""
        self.metric_diff = None  # current_value - basic_value
        self.metric_change_rate = None  # (current_value - basic_value) / basic_value

        # init attribution algorithm map
        self.algorithms = {
            'adtributor': self._run_adtributor,
            'r_adtributor': self._run_r_adtributor
        }

        self.available_steps = ['metric_breakdown', 
                                'attribution_analysis', 
                                'batch_attribution_analysis', 
                                'holiday_impact', 
                                'experiment_impact'
                                ]
        
        # init dataframes
        self.df_metric_breakdown = pd.DataFrame()  # store the detailed metric breakdown
        self.df_dimension_breakdown = pd.DataFrame()  # store the detailed dimension breakdown

        # init report dataframes
        self.report_metric_breakdown = pd.DataFrame()  # report by metric breakdown
        self.report_attribution = pd.DataFrame()  # report by adtribution analysis
        self.report_attribution_dict = {}  # report by adtribution analysis, key: metric, value: dimension attribution
        self.report_holiday_impact = pd.DataFrame()  # report by holiday impact
        self.report_experiment_attribution = pd.DataFrame()  # report by experiment attribution
        print("AutoAnalysis initialized.")        


    # ======================== public methods ========================   
    # run analysis step by step
    def run_analysis(self, treatment_date, control_date, time_mode = "Day",
                     filter_str = "",
                     filter_markets_list = [],
                     steps = ['metric_breakdown', 'batch_attribution_analysis', 'holiday_impact', 'experiment_impact'],
                     attribution_dimensions = [], 
                     algorithm_name = "adtributor",
                     use_cache = False,
                     **attribution_args):
        
        FUNC_NAME = f"{get_current_function()}|"
        # set query parameters
        self.treatment_date = treatment_date
        self.control_date = control_date
        self.time_mode = time_mode
        # build filter query  merge_filter_query
        merge_filter_str = query_utils.merge_filter_query(filter_str, filter_markets_list)
        print(f"{FUNC_NAME} merge filter_str:{merge_filter_str}")

        for step in steps:
            if step == "metric_breakdown":
                self._run_metric_breakdown(merge_filter_str, use_cache)
                if self.most_primary_metric != self.metric:
                    self.most_primary_metrics = [self.metric, self.most_primary_metric]
                print(f"{FUNC_NAME} the most primary metrics:{self.most_primary_metrics}")
                print(f"{FUNC_NAME} you can get the result of '{step}': self.report_metric_breakdown")

            elif step == "attribution_analysis":
                self._run_attribution_analysis(self.metric,
                                            merge_filter_str, 
                                            attribution_dimensions, 
                                            algorithm_name,
                                            use_cache,
                                            **attribution_args) 
                self.report_attribution_dict = {self.metric: self.report_attribution}
                print(f"{FUNC_NAME} you can get the result of '{step}': self.report_attribution_dict[{self.metric}]")

            elif step == "batch_attribution_analysis":
                # self.report_attribution_dict will be updated, keys are self.most_primary_metrics
                self._run_batch_attribution_analysis(self.most_primary_metrics,
                                                merge_filter_str,
                                                use_cache,
                                                algorithm_name,
                                                attribution_dimensions,
                                                **attribution_args)
                print(f"{FUNC_NAME} you can get the result of '{step}': self.report_attribution_dict[metric]")    

            elif step == "holiday_impact":
                holiday_impact_analyzer = HolidayImpactAnalyzer(self.titan_api, 
                                                        metric = self.metric,
                                                        treatment_date = treatment_date,
                                                        control_date = control_date,
                                                        time_mode = time_mode,
                                                        metric_query_map = self.metric_query_map,
                                                        combine_metric_query_map = self.combine_metric_query_map,                                        
                                                        verbose=self.verbose)
                
                holiday_impact_analyzer.run_holiday_impact_analysis(filter_str, filter_markets_list, use_cache)
                self.report_holiday_impact = holiday_impact_analyzer.result_dict["report"]
                print(f"{FUNC_NAME} you can get the result of '{step}': self.report_holiday_impact")
            
            elif step == "experiment_impact":
                exp_impact_analyzer = ExperimentImpactAnalyzer(azure_db_api=self.azure_db_api, 
                                                            metric = self.metric,
                                                            treatment_date = treatment_date,
                                                            control_date = control_date,
                                                            time_mode = time_mode,
                                                            global_delta = self.metric_diff,
                                                            verbose = self.verbose)
                exp_impact_analyzer.run_experiment_impact_analysis(merge_filter_str, filter_markets_list)
                self.report_experiment_attribution = exp_impact_analyzer.result_dict["report"]
                print(f"{FUNC_NAME} you can get the result of '{step}': self.report_experiment_attribution")

            else:
                print(f"{FUNC_NAME} Error: Invalid step '{step}'. Only support: {', '.join(self.available_steps)}.")

            print(f"{FUNC_NAME} run step '{step}' done.")

        print(f"{FUNC_NAME} run all steps done. Now you can run self.download_report(report_name,file_path) to get the report.")
        return


    def download_report(self, report_name="report", file_path="./"):
        FUNC_NAME = f"{get_current_function()}|"
        
        file_name = f"{report_name}.xlsx" if "xlsx" not in report_name else report_name
        output_dir = Path(file_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / file_name
        print(f"{FUNC_NAME} will download report to {output_file}...")

        with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:  
            self.report_metric_breakdown.to_excel(writer, sheet_name='metric_breakdown', index=True, startrow=0, startcol=0)
            
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer: 
            for metric, v in self.report_attribution_dict.items():
                tab_name = re.sub(r'[^a-zA-Z0-9]', '_', metric)
                v.to_excel(writer, sheet_name=f'{tab_name}_dimension_breakdown', index=False, startrow=0, startcol=0)
            
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            self.report_holiday_impact.to_excel(writer, sheet_name='holiday_impact', index=False, startrow=0, startcol=0)

        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            self.report_experiment_attribution.to_excel(writer, sheet_name='experiment_impact', index=False, startrow=0, startcol=0)
        
        print(f"{FUNC_NAME} report saved to {output_file}.")
        return


    def set_metric(self, metric) -> int:
        ret = 0
        ret = self._initial_metric_config(metric)
        if ret:
            raise Exception(f"Error: metric {metric} is not supported.")
        self.metric = metric
        self.refresh_cache()
        return ret
    

    def set_customized_metric_tree(self, metric_config_json) -> int:
        # self.metric_map = {metric: [MSNMetricTreeNode()]}
        ret = 0
        replaced_metric_set = set()  # record the replaced metrics
        new_metric_tree = {}
        try:
            metric_tree = json.loads(metric_config_json)
            for m, m_config in metric_tree.items():
                if m in self.metric_map:
                    replaced_metric_set.add(m)
                    print(f"{__class__.__name__} Warning: {m} will be replaced.")
                if not m_config:
                    raise Exception(f"Error: metric config of {m} is empty.")
                # assert that if is_direct_query is True, titan_query is not empty
                if m_config.get("is_direct_query", True) and m_config.get("titan_query", "") == "":
                    raise Exception(f"Error: metric {m} is_direct_query is True, but titan_query is empty.")
                if (not m_config.get("is_direct_query", True)) and len(m_config.get("formula", [])) == 0:
                    raise Exception(f"Error: metric {m} formula is empty.")
                if len(m_config.get("formula", [])) != len(m_config.get("coefficient", [])):
                    raise Exception(f"Error: length of formula and coefficient are not matched. \
                        {len(m_config.get('formula', []))} != {len(m_config.get('coefficient', []))}")
                
                op_type = get_enum_member(MathOperations, m_config.get("op_type"))
                if len(m_config.get("formula", [])) > 0 and op_type is None:
                    raise Exception(f"Error: metric {m} op_type {m_config.get('op_type')} is not supported.")
                # insert into metric_map
                m_node = MSNMetricTreeNode(metric_name=m, 
                            formula=m_config.get("formula", []), 
                            op_type=op_type, 
                            coefficient=m_config.get("coefficient", []), 
                            titan_query=m_config.get("titan_query", ""), 
                            is_direct_query=m_config.get("is_direct_query", True))
                new_metric_tree[m] = [m_node]
        except json.JSONDecodeError as e:
            raise e
        
        # update metric_map
        self.metric_map.update(new_metric_tree)

        if replaced_metric_set:
            print(f"{__class__.__name__} Warning: replaced metrics: {replaced_metric_set}")
        
        # TODO: TEST
        print(f"{__class__.__name__} metric_map:{new_metric_tree}")
        print(f"{__class__.__name__} set_customized_metric_tree success.")
        return ret


    def get_metric_tree(self) -> dict:
        def _parse_MSNMetricTreeNode_to_dict(node:MSNMetricTreeNode) -> dict:
            ret = {}
            ret["metric_name"] = node.metric_name
            ret["formula"] = node.formula
            ret["op_type"] = node.op_type.value if node.op_type else None
            ret["coefficient"] = node.coefficient
            ret["titan_query"] = node.titan_query
            ret["is_direct_query"] = node.is_direct_query
            return ret
        
        ret = {}
        for metric, nodes in self.metric_map.items():
            ret[metric] = list(map(_parse_MSNMetricTreeNode_to_dict, nodes))
        return ret


    def refresh_token(self):
        self.titan_api = TitanApi(self.alias_account, "")
        self.azure_db_api = AzureDbApi()


    def refresh_cache(self):
        self.df_metric_breakdown = pd.DataFrame()
        self.df_dimension_breakdown = pd.DataFrame()
        self.report_metric_breakdown = pd.DataFrame()
        self.report_attribution_dict = {}
        self.report_holiday_impact = pd.DataFrame()
        self.report_experiment_attribution = pd.DataFrame()
        print("Cache refreshed.")

    # ======================== private methods ========================
    # init metric config
    def _initial_metric_config(self, metric):
        FUNC_NAME = f"{get_current_function()}|"
        ret = 0
        if metric not in self.metric_map:
            return 1
        metric_breakdown_choices = self.metric_map[metric]
        if len(metric_breakdown_choices) == 0:
            return 1
        # TODO: select the first one by default
        self.metric_config = metric_breakdown_choices[0]

        # start parse tree structure
        metric_set = set([metric])
        used_metric_set = set()
        metric_query_map = {}
        combine_metric_query_map = {}
        # build metric query map
        while metric_set:
            m = metric_set.pop()
            if m in used_metric_set:
                continue
            else:
                used_metric_set.add(m)

            ###### build metric query map ######
            metric_breakdown_choices = self.metric_map.get(m, [])
            if len(metric_breakdown_choices) == 0:
                raise Exception(f"Error: metric {m} is undefined.")
            # TODO: select the first one by default
            metric_config = metric_breakdown_choices[0]
            if self.verbose:
                print(f"{FUNC_NAME}metric:{m} has formula:{metric_config.formula}, query:{metric_config.titan_query}")
            
            if metric_config.is_direct_query:
                if metric_config.titan_query == "":
                    raise Exception(f"Error: metric {m}'s query is undefined.")
                else:
                    metric_query_map[m] = metric_config.titan_query
            else:
                combine_query_str = query_utils.build_combined_metric_query(
                    metric_config.formula, metric_config.op_type, metric_config.coefficient)
                if combine_metric_query_map == "":
                    raise Exception(f"Error: metric {m} failed to build query. Please check the configuration.")
                combine_metric_query_map[m] = combine_query_str
            
            # Get next level metrics
            if len(metric_config.formula) == 0:
                continue
            for sub_metric in metric_config.formula:
                if sub_metric in used_metric_set:
                    continue
                metric_set.add(sub_metric)
        
        # END while
        self.metric_query_map = metric_query_map 
        self.combine_metric_query_map = combine_metric_query_map
        self.metric_set = used_metric_set
        if self.verbose:
            print(f"{FUNC_NAME}metric_query_map:{self.metric_query_map.keys()}")
            print(f"{FUNC_NAME}combine_metric_query_map:{self.combine_metric_query_map.keys()}")
        self.metric_query_str = "\n, ".join([f" {v} AS `{k}`" for k, v in self.metric_query_map.items()])
        if self.combine_metric_query_map:
            self.metric_query_str += " \n, " + "\n, ".join([f" {v} AS `{k}`" for k, v in self.combine_metric_query_map.items()])
        return ret
    

    def _set_treatment_control_with_weights(self, df_input, metric):
        """
        merge the rows of treatment and control groups
        """
        FUNC_NAME = f"{get_current_function()}|"
        df = df_input.copy()
        df["Control"] = df[f"{metric}_c"].astype(float).fillna(0)
        df["Treatment"] = df[f"{metric}_t"].astype(float).fillna(0)
        
        # if the metric type is ratio, need to calculate the weighted value.
        metric_config = self.metric_map.get(metric, [MSNMetricTreeNode()])[0]
        if metric_config.op_type == MathOperations.DIVISION:
            if len(metric_config.formula) != 2:
                raise Exception(f"Error: the formula of {metric} is not correct.")
            try:
                # set the denominator epsilon to avoid division by zero
                epsilon = 1e-6
                df["Control_weight"] = df[metric_config.formula[1] + "_c"] / (df[metric_config.formula[1] + "_c"].sum() + epsilon)
                df["Treatment_weight"] = df[metric_config.formula[1] + "_t"] / (df[metric_config.formula[1] + "_t"].sum() + epsilon)
                df["Control"] = df["Control"].fillna(0) * df["Control_weight"].fillna(0)
                df["Treatment"] = df["Treatment"].fillna(0) * df["Treatment_weight"].fillna(0)
            except Exception as e:
                print(f"{FUNC_NAME} Error: {e}")
        
        return df
        

    def _level_traverse_calculate_contribution(self):
        """
        Perform a level-order traversal to calculate the contribution of each metric.
        This method initializes a queue with the root metric and traverses through each level of metrics,
        calculating the contribution of each metric based on its configuration. The results are stored in a report DataFrame.
        The method performs the following steps:
        1. Initialize a queue with the root metric.
        2. Traverse through each level of metrics.
        3. For each metric, calculate its contribution based on its configuration.
        4. Store the results in a report DataFrame.
        The report DataFrame contains the following columns:
        - metric: The name of the metric.
        - level: The level of the metric in the traversal.
        - parent: The parent metric.
        - treat: The treatment value of the metric.
        - ctrl: The control value of the metric.
        - delta: The difference between the treatment and control values.
        - delta%: The percentage difference between the treatment and control values.
        - formula: The formula used to calculate the metric.
        - contribution%: The contribution percentage of the metric.
        Returns:
            None
        """
        FUNC_NAME = f"{get_current_function()}|"
        # init queue: [(metric, level, parent_metric, need_breakdown)]
        queue = deque([(self.metric, 0, None, True)])
        used_metrics = set()
        report_columns = ["Metric", "Level", "Parent", "Treat", "Ctrl", "Delta", "Delta%", "Formula", "Contribution%"]
        report = []

        # level traverse
        while queue:
            m, level, parent, need_breakdown = queue.popleft()
            if self.verbose:
                print(f"{FUNC_NAME}metric:{m}, level:{level}, parent:{parent}")
            if m in used_metrics:
                continue
            used_metrics.add(m)
            record = pd.Series()

            # init record
            record["Metric"] = m
            record["Level"] = level
            record["Parent"] = parent

            raw_record = self.df_metric_breakdown.iloc[0]  # default: only 1 row for each comparison.
            record["Treat"] = raw_record[f'{m}_t']
            record["Ctrl"] = raw_record[f'{m}_c']
            record["Delta"] = record["Treat"] - record["Ctrl"]
            record["Delta%"] = safe_div(record["Delta"], record["Ctrl"])
            record["Formula"] = ""
            record["Contribution%"] = ""
            
            # get next level for m if m has NOT been used.
            if not need_breakdown:
                report.append(record)
                continue

            m_config_choices = self.metric_map.get(m, [])
            m_config = m_config_choices[0] if len(m_config_choices) > 0 else None
            if m_config is None or len(m_config.formula) <= 0:
                print(f"{FUNC_NAME}Warning: {m} has no m_config or formula.")
                report.append(record)
                continue
            # check if all factors in m_config.formula have been calculated
            elif all([f in used_metrics for f in m_config.formula]):
                print(f"{FUNC_NAME}Warning: {m_config.formula} have been calculated.")
                report.append(record)
                continue
            else:
                record["Formula"] = data_ops.parse_formula(m_config)
            
            # do calculation for m
            if m_config.op_type == MathOperations.ADDITION:
                calculate_contribution_by_addition(self.df_metric_breakdown, m, m_config.formula, m_config.coefficient)
            elif m_config.op_type == MathOperations.MULTIPLICATION:
                calculate_contribution_by_multiplication(self.df_metric_breakdown, m, m_config.formula, m_config.coefficient)
            elif m_config.op_type == MathOperations.DIVISION:
                calculate_contribution_by_division(self.df_metric_breakdown, m, m_config.formula, m_config.coefficient)
            else:
                print(f"Error: {m_config.op_type} is not supported.")
            
            raw_record = self.df_metric_breakdown.iloc[0]  # default: only 1 row for each comparison.
            # json: {factor1: contribution1, factor2: contribution2}
            record["Contribution%"] = data_ops.parse_contribution_to_json(m_config, raw_record)
            
            # add record to report
            report.append(record.copy())

            # add sub-metrics to queue
            for i, sub_metric in enumerate(m_config.formula):
                need_breakdown_flag = True if m_config.need_breakdown[i] != 0 else False
                queue.append((sub_metric, level+1, m, need_breakdown_flag)) 

        self.report_metric_breakdown = pd.DataFrame(report, columns=report_columns)
        if not self.report_metric_breakdown.empty \
            and "Parent" in self.report_metric_breakdown.columns \
            and "Level" in self.report_metric_breakdown.columns:
            self.report_metric_breakdown.set_index(["Level", "Parent"], inplace=True)

        return
        

    def _run_metric_breakdown(self, filter_str, use_cache = False):
        """
        Get metric comparison by metric breakdown.
        """
        FUNC_NAME = f"{get_current_function()}|"
        # get metric comparison raw data from cache or new query
        if use_cache \
            and not self.df_metric_breakdown.empty \
            and f"{self.metric}_t" in self.df_metric_breakdown.columns:
                print(f"{FUNC_NAME} metric:{self.metric} | get data from cache.")
                pass
        else:
            print(f"{FUNC_NAME} metric:{self.metric} | get data from new query.")
            # get metric comparison from Titan
            self.df_metric_breakdown = query_utils.get_df_metric_comparison(
                    self.titan_api,
                    self.metric,
                    self.treatment_date, self.control_date, self.time_mode,
                    filter_str,
                    metric_query_str = self.metric_query_str,
                    metric_query_map = self.metric_query_map,
                    combine_metric_query_map = self.combine_metric_query_map,
                    metric_set = self.metric_set
                    ) 
            if self.df_metric_breakdown.empty:
                print(f"{FUNC_NAME} returns nonthing.")
                return
        try:
            self.metric_change_rate = self.df_metric_breakdown[[f"{self.metric}_t", f"{self.metric}_c"]].apply(
                lambda x: safe_div((x[f"{self.metric}_t"] - x[f"{self.metric}_c"]), x[f"{self.metric}_c"]), axis=1).values[0]
            self.metric_diff = self.df_metric_breakdown[f"{self.metric}_t"].values[0] - self.df_metric_breakdown[f"{self.metric}_c"].values[0]
            if self.verbose:
                print(f"{FUNC_NAME} metric:{self.metric}, metric_diff:{self.metric_diff}, metric_change_rate:{self.metric_change_rate}")
        
        except Exception as e:
            print(f"{FUNC_NAME} Error: {e}")
            return

        # calculate contribution by factor, self.report_metric_breakdown will be updated.
        self._level_traverse_calculate_contribution()

        # get the most primary metric
        self._format_metric_attribution_report()
            
        return


    def _run_attribution_analysis(self,
                                  metric: str, 
                                  filter_str: str, 
                                  attribution_dimensions: list, 
                                  algorithm_name: str, 
                                  use_cache: bool = False,
                                  **kwargs):
        """
        Run attribution analysis on the given data.
        Parameters:
            metric (str): The metric to analyze.
            filter_str (str): The filter string to apply to the data.
            attribution_dimensions (list): List of dimensions to use for attribution analysis.
            algorithm_name (str): The name of the algorithm to use for attribution analysis.
            **kwargs: Additional keyword arguments to pass to the algorithm function.
        Returns:
            None, self.report_attribution will be updated.
        """
        FUNC_NAME = f"{get_current_function()}|"
        if algorithm_name not in self.algorithms:
            raise Exception(f"Algorithm {algorithm_name} is not supported. Now only support {list(self.algorithms.keys())}")

        if len(attribution_dimensions) == 0:
            raise Exception("Error: attribution_dimensions is at least one dimension.")

        clean_attribution_dimensions = list(map(lambda x: x.split("AS ")[-1].strip(), attribution_dimensions))
        if use_cache \
            and (not self.df_dimension_breakdown.empty) \
            and f"{metric}_t" in self.df_dimension_breakdown.columns \
            and all([d in self.df_dimension_breakdown.columns for d in clean_attribution_dimensions]):
                print(f"{FUNC_NAME} metric:{metric} | get data from cache.")
                df = self.df_dimension_breakdown.copy()
        else:
            print(f"{FUNC_NAME} metric:{metric} | get data from new query.")
            df = query_utils.get_metric_comparison_by_customized_dimension(
                self.titan_api,
                self.metric,
                self.treatment_date, self.control_date, self.time_mode,
                filter_str = filter_str,
                metric_query_str = self.metric_query_str,
                metric_query_map = self.metric_query_map,
                combine_metric_query_map = self.combine_metric_query_map,
                metric_set = self.metric_set,
                dimension_list = attribution_dimensions,
                clean_dimension_list = clean_attribution_dimensions
            )
            if df.empty:
                print(f"{FUNC_NAME} returns nonthing from Titan.")
                return
            
            self.df_dimension_breakdown = df.copy()
        
        if self.verbose:
            print(f"{FUNC_NAME} There are {df.shape[0]} rows in the self.df_dimension_breakdown.")
            print(f"{FUNC_NAME} Dimensions:{clean_attribution_dimensions} will be used for '{metric}' attribution analysis.")

        # 1. get metric comparison by customized dimension
        df = self._set_treatment_control_with_weights(df, metric)
        self.df_dimension_breakdown_merge = df.copy()

        # 2. Call the adtributor_analysis, and self.df_attribution_result will be updated here.
        algorithm_func = self.algorithms[algorithm_name]
        algorithm_func(df = df, 
                       dimension_cols = clean_attribution_dimensions, 
                       treatment_col="Treatment",
                       control_col="Control",
                       verbose = self.verbose,
                       **kwargs)

        # 3. report by adtribution result
        self.report_attribution = self.df_attribution_result

    
    def _run_adtributor(self, df: pd.DataFrame,
                        dimension_cols: list,
                        treatment_col: str,
                        control_col: str,
                        top_n_factors = 100,
                        TEEP = 0.05,
                        TEP = 20,
                        min_surprise = 0.0001,
                        max_item_num = 10,
                        need_negative_ep_factor = True,
                        use_auto_adjusted_min_suprise = False,
                        verbose = 0):
        """
        TEEP: Minimum detectable EP value
        TEP: EP cumulative threshold
        dimension_cols must be found in data
        treatment_col and control_col must be found in data
        """
        # check if the columns are in the dataframe
        if not set(dimension_cols + [treatment_col, control_col]).issubset(set(df.columns)):
            raise Exception(f"Columns:{dimension_cols + [treatment_col, control_col]} not found in the dataframe.")

        analyzer = Adtributor(top_n_factors = top_n_factors,
                        TEEP = TEEP, 
                        TEP = TEP,
                        min_surprise = min_surprise, 
                        max_item_num = max_item_num,
                        need_negative_ep_factor = need_negative_ep_factor,
                        use_auto_adjusted_min_suprise = use_auto_adjusted_min_suprise,
                        verbose = verbose)

        self.df_attribution_result = analyzer.analyze(
            data = df, 
            dimension_cols = dimension_cols, 
            treatment_col = treatment_col, 
            control_col = control_col)
        
        return


    def _run_r_adtributor(self, df: pd.DataFrame,
                        dimension_cols: list,
                        treatment_col: str,
                        control_col: str,
                        top_n_factors = 20,
                        TEEP = 0.05,
                        TEP = 20,
                        min_surprise = 0.0001,
                        max_item_num = 3,
                        max_dimension_num = 3,
                        max_depth = 3,
                        need_negative_ep_factor = True,
                        need_prune = True,
                        verbose = 0):
        """
        TEEP: Minimum detectable EP value
        TEP: EP cumulative threshold
        dimension_cols must be found in data
        treatment_col and control_col must be found in data
        """
        # check if the columns are in the dataframe
        if not set(dimension_cols + [treatment_col, control_col]).issubset(set(df.columns)):
            raise Exception(f"Columns:{dimension_cols + [treatment_col, control_col]} not found in the dataframe.")

        analyzer = RecursiveAdtributor(top_n_factors = top_n_factors,
                        TEEP = TEEP, 
                        TEP = TEP,
                        min_surprise = min_surprise, 
                        max_item_num = max_item_num,
                        max_dimension_num = max_dimension_num,
                        max_depth = max_depth,
                        need_negative_ep_factor = need_negative_ep_factor,
                        need_prune = need_prune,
                        verbose = verbose)

        self.df_attribution_result = analyzer.analyze(
            data = df, 
            dimension_cols = dimension_cols, 
            treatment_col = treatment_col, 
            control_col = control_col)
        
        return        
    

    def _run_batch_attribution_analysis(self,
                                        metrics_to_run: list,
                                        filter_str: str,
                                        use_cache: bool,
                                        algorithm_name: str,
                                        dimension_list: list,
                                        **attribution_args):
        """
        Run attribution analysis on the given data.
        """
        dimension_report_dict = {k : pd.DataFrame() for k in metrics_to_run}
        if dimension_list is None or len(dimension_list) == 0:
            dimension_list = [
                DEFAULT_DIMENSIONS_MAP["User"] + DEFAULT_DIMENSIONS_MAP["Location"] + DEFAULT_DIMENSIONS_MAP["Device"] + DEFAULT_DIMENSIONS_MAP["EntryPoint"],
                DEFAULT_DIMENSIONS_MAP["Page"]
            ]
        for dimensions in dimension_list:
            for m in metrics_to_run:
                self._run_attribution_analysis(m,
                                            filter_str, 
                                            dimensions,
                                            algorithm_name,
                                            use_cache,
                                            **attribution_args)
                dimension_report_dict[m] = pd.concat([dimension_report_dict[m], self.report_attribution], axis=0)

        self.report_attribution_dict = dimension_report_dict

        for m in metrics_to_run:
            self._format_dimension_attribution_report(m)

        return


    def _format_metric_attribution_report(self):
        """
        Description: Format the self.report_metric_breakdown and display the primary sub-metrics contributing to the movement. 
        self.most_primary_metric will be updated.
        """
        FUNC_NAME = f"{get_current_function()}|"

        report = self.report_metric_breakdown.copy()
        report.reset_index(inplace=True)
        report.set_index(keys="Metric", drop=False, inplace=True)
        report["TopContributingSubmetrics"] = [[] for _ in range(len(report))]
        
        d = report.to_dict()  # e.g.{column: {Metric: value}}

        most_primary_metric = self.metric
        queue = deque([(self.metric, 100)])
        used_metrics = set()

        while queue:
            m, _ = queue.popleft()
            if m in used_metrics:
                continue
            used_metrics.add(m) 
            
            contribution_json = d["Contribution%"][m]
            if contribution_json is None or contribution_json == "":
                continue
            try:
                contribution_json = json.loads(contribution_json)
            except json.JSONDecodeError as e:
                print(f"Error: {e}")
                continue
            contribution_data = [(key, float(value.replace("%", ""))/100 ) for key, value in contribution_json.items()]
            contribution_data.sort(key=lambda x: x[1], reverse=True)
            min_contribution = 1/len(contribution_data) * MIN_METRIC_CONTRIBUTION_FACTOR
            top_contributing_submetrics = [(k,v) for k, v in contribution_data if abs(v) >= min_contribution]
            if m == most_primary_metric:  # Only update the most primary metric's path
                most_primary_metric = top_contributing_submetrics[0][0] if top_contributing_submetrics else most_primary_metric
            for k, v in top_contributing_submetrics:
                report.loc[m, "TopContributingSubmetrics"].append((k,v))
                queue.append((k, v))  
        
        self.most_primary_metric = most_primary_metric
        report["Sub-metric"] = ""
        report["Contribution%"] = ""
        report["Sub-metric Delta%"] = ""
        try:
            report = report[report["TopContributingSubmetrics"].apply(len) > 0]
            report = report.explode("TopContributingSubmetrics")
            report[["Sub-metric", "Contribution%"]] = report["TopContributingSubmetrics"].apply(pd.Series)

            report_cols = ["Level", "Metric", "Delta%", "Sub-metric", "Contribution%", "Sub-metric Delta%", "Formula"]
            report.reset_index(drop=True, inplace=True)  # remove metric index
            report["Sub-metric Delta%"] = report["Sub-metric"].apply(lambda x: d["Delta%"].get(x, -1))

            # transform the number to percentage format
            report["Delta%"] = report["Delta%"].apply(lambda x: f"{x:.2%}")
            report["Sub-metric Delta%"] = report["Sub-metric Delta%"].apply(lambda x: f"{x:.2%}")
            report["Contribution%"] = report["Contribution%"].apply(lambda x: f"{x:.2%}")
        except Exception as e:
            print(f"{FUNC_NAME}Error: {e}")

        if report.shape[0] == 0:
            cmd = "auto_analysis.report_metric_breakdown.to_excel('your_report.xlsx')"
            print(f"""{FUNC_NAME}Warning: There's no sub-metric contributing to the movement.\nPlease run:\n{cmd} to get the detailed report.""")
        
        print_df_as_table(
                report[report_cols],
                title="The Primary Sub-metrics Contributing to the Movement.",
                console_width=150,
                column_widths={"Formula": 50},
                column_styles={
                    "Sub-metric": "black bold",
                    "Contribution%": "black bold",
                    "Sub-metric Delta%": "black bold","Formula": "dim"}
            )
        return 
    

    def _format_dimension_attribution_report(self, metric):
        """
        format the dimension attribution report for the given metric.
        Parameters:
            metric (str): The metric to analyze.
            Input from self.report_attribution_dict[metric]
        """
        FUNC_NAME = f"{get_current_function()}|"
        # will update self.report_attribution_dict[metric]
        report = self.report_attribution_dict.get(metric, pd.DataFrame())
        if report.empty:
            print(f"{FUNC_NAME}Warning: No data found for metric:{metric}.")
            return

        def _get_dimension_attribution_type(row, trend):
            """
            Get the attribution type of the dimension, comparing the metric trend with the explanatory variable.
            """
            p_t = row["P_t"]
            p_c = row["P_c"]
            explanatory = row["Explanatory"]

            if trend == "down":
                primary_condition = p_t < p_c and explanatory > 0
                inverse_condition = p_t > p_c and explanatory < 0
            elif trend == "up":
                primary_condition = p_t > p_c and explanatory > 0
                inverse_condition = p_t < p_c and explanatory < 0
            else:
                return "Other"

            if primary_condition:
                return "Primary"
            elif inverse_condition:
                return "Inverse"
            return "Other"

        try:
            # get the metric trend
            metric_trend = ""
            if not self.report_metric_breakdown.empty \
                and "Delta%" in self.report_metric_breakdown.columns:
                    delta = self.report_metric_breakdown[self.report_metric_breakdown["Metric"] == metric]["Delta%"].values[0]
                    metric_trend = "up" if delta > 0 else "down"         
            print(f"{FUNC_NAME}metric:{metric}, metric_delta:{delta:.2%}, metric_trend:{metric_trend}")
            # get attribution type
            report["AttributionType"] = report.apply(lambda row: _get_dimension_attribution_type(row, trend=metric_trend), axis=1)
        except Exception as e:
            print(f"{FUNC_NAME}Error occurred while calculating AttributionType: {str(e)}")
            return

        report.rename(columns={"Surprise": "Volatility", "DimensionSurprise": "DimensionVolatility"}, inplace=True)
        # Transform the number to percentage format
        report["Contribution%"] = report["Explanatory"].apply(lambda x: f"{x * 100:.2f}%")
        report["Share_t"] = report["P_t"].apply(lambda x: f"{x * 100:.2f}%")
        report["Share_c"] = report["P_c"].apply(lambda x: f"{x * 100:.2f}%")
        report["Metric_Delta%"] = report["Delta%"].apply(lambda x: f"{x * 100:.2f}%")

        # Split the report into primary and inverse trends
        report_primary = report[report["AttributionType"] == "Primary"].sort_values(by="Explanatory", ascending=False)
        report_inverse = report[report["AttributionType"] == "Inverse"].sort_values(by="Explanatory", ascending=True)

        report_columns = ["Dimension", "Value", "Contribution%", "Metric_Delta%", "Volatility", "Share_t", "Share_c" ]

        # Print the primary and inverse trend reports
        try:
            print_df_as_table(
                report_primary[report_columns],
                title=f"{metric}: Primary Dimensions Causing Metric Movement ",
                console_width=150,
                column_styles={
                    "Contribution%": "black bold"}
            )
        except Exception as e:
            print(f"{FUNC_NAME}Error occurred while printing primary report: {str(e)}")

        try:
            print_df_as_table(
                report_inverse[report_columns],
                title=f"{metric}: Dimensions That Display Inverse Trends in Line with Metric Movement",
                console_width=150,
                column_styles={
                    "Contribution%": "black bold"}
            )
        except Exception as e:
            print(f"{FUNC_NAME}Error occurred while printing inverse report: {str(e)}")

        self.report_attribution_dict[metric] = report.copy()
        
        return
