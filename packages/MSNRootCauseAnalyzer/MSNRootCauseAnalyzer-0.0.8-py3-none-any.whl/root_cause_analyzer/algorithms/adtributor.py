# adtributor.py
# Adtributor: https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-bhagwan.pdf
# Revised Recursive Adtributor: https://odr.chalmers.se/server/api/core/bitstreams/1641e4bf-edec-4fe3-b1ed-0c281d538824/content

from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

from .base_analyzer import BaseAnalyzer
from ..utils import safe_div, get_current_function, print_verbose_info
from ..core.auto_parameter_tuning import get_adjusted_min_suprise


class Adtributor(BaseAnalyzer):
    """
    Adtributor 
    """
    def __init__(self, top_n_factors,
                 TEEP = 0.05,
                 TEP = 1,
                 min_surprise = 0.0005,
                 max_item_num = 10,
                 need_negative_ep_factor = False,
                 use_auto_adjusted_min_suprise = False,
                 verbose = 0):
        """
        TEEP: Minimum detectable EP value
        TEP: EP cumulative threshold
        min_surprise: Minimum detectable surprise value
        max_item_num: Maximum number of values for each dimension
        dimension_cols must be found in data, CANNOT be empty
        treatment_col and control_col must be found in data
        """
        super().__init__(top_n_factors, verbose=verbose)
        self.TEEP = TEEP
        self.TEP = TEP
        self.min_surprise = min_surprise
        self.max_item_num = max_item_num
        self.need_negative_ep_factor = need_negative_ep_factor
        self.use_auto_adjusted_min_suprise = use_auto_adjusted_min_suprise

        self.dimension_cols = []
        self.treatment_col = "Treatment"
        self.control_col = "Control"

        self.alpha = None  # the delta of metric movement
        

    def _kl_divergence(self, p, q):
        epsilon = 1e-10  # small constant to avoid division by zero
        p = np.array(p)
        q = np.array(q) + epsilon
        return np.sum(np.where(p != 0, p * np.log(p / q), 0))

    def _js_divergence(self, p, q):
        """
        Calculate JS Divergence
        p: Expectation Distribution
        q: Actual Distribution
        """
        m = (p + q) / 2
        return 0.5 * self._kl_divergence(p, m) + 0.5 * self._kl_divergence(q, m)
    

    def calculate_surprise_and_explanatory(self, df: pd.DataFrame):
        """
        df required columns are: 
        """
        df.columns = ["Control", "Treatment"]
        Control_Sum = df['Control'].sum()
        Treatment_Sum = df['Treatment'].sum()
        total_delta = Treatment_Sum - Control_Sum
        
        # Update the Surprise[i] and Explanatory[i] for the i_th dimension
        df["Surprise"] = df.apply(lambda x: self._js_divergence(x['Control']/Control_Sum, x['Treatment']/Treatment_Sum), axis=1)
        df["Explanatory"] = df.apply(lambda x: (x['Treatment']-x['Control'])/total_delta, axis=1)
        df["P_t"] = df["Treatment"]/Treatment_Sum  # add the probability of Treatment
        df["P_c"] = df["Control"]/Control_Sum  # add the probability of Control
        df["Delta%"] = df.apply(lambda x: safe_div(x['Treatment']-x['Control'], x['Control']), axis=1)
        
        return
    
    def get_dimension_candidates(self, dimen: str):
        FUNC_NAME = f"{__class__.__name__}|{get_current_function()}|"
        # sort the dimension by Surprise in descending order
        df_dimen = self.dimension_stats_map[dimen].sort_values(by="Surprise", ascending=False)
        df_dimen['Dimension'] = dimen
        df_dimen.reset_index(inplace=True)
        df_dimen.rename(columns={dimen: "Value"}, inplace=True)

        self.dimension_stats_map[dimen] = pd.DataFrame()
        
        # filter out the items with small Explanatory and Surprise
        if self.need_negative_ep_factor:
            df_dimen = df_dimen[(df_dimen["Explanatory"].abs() >= self.TEEP) & (df_dimen["Surprise"] >= self.min_surprise)]
        else:
            df_dimen = df_dimen[(df_dimen["Explanatory"] >= self.TEEP) & (df_dimen["Surprise"] >= self.min_surprise)]
        
        if df_dimen.shape[0] == 0:
            print(f"{FUNC_NAME}there is no root cause for dimension:{dimen}")
            return None
        
        # calculate the cumulative sum of Explanatory
        df_dimen['ExplainCumSum'] = df_dimen['Explanatory'].abs().cumsum()
        
        # filter for the top items: when ExplainCumSum > TEP or exceed the max_item_num, quit
        if df_dimen['ExplainCumSum'].head(1).values[0] >= self.TEP:
            df_dimen = df_dimen.head(1)  # ensure at least one item
        else:
            df_dimen = df_dimen[(df_dimen['ExplainCumSum'] < self.TEP)].head(self.max_item_num)
        
        if df_dimen.shape[0] == 0:
            print(f"{FUNC_NAME}there is no root cause for dimension:{dimen}")
            return None

        # get the SurpriseCumSum as the dimension's cumulative surprise
        df_dimen['DimensionSurprise'] = df_dimen['Surprise'].sum()
        return df_dimen

    def format_output(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        return a formatted result dataframe
        """
        df = df.copy()
        df.sort_values(['DimensionSurprise', 'Dimension', 'Explanatory'],
                        ascending=[False, True, False], inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df[['Dimension', 'Value', 'Surprise', 'P_t', 'P_c', 'Delta%', 'Explanatory', 'DimensionSurprise']].head(self.top_n_factors)
    
    def analyze(self, data: pd.DataFrame,                  
                dimension_cols = [], 
                treatment_col = "Treatment", 
                control_col= "Control") -> pd.DataFrame:
        """
        TODO: data: pandas DataFrame with columns:[*dimension_cols], treatment_col, control_col]
        dimension_cols must be found in data
        treatment_col_name and control_col_name must be found in data
        """
        FUNC_NAME = f"{__class__.__name__}|{get_current_function()}|"
        # check the input data
        if len(dimension_cols) == 0:
            raise Exception(f"dimension_cols CANNOT be empty.")
        if not set(dimension_cols + [treatment_col, control_col]).issubset(set(data.columns)):
            raise Exception(f"Columns:{dimension_cols + [treatment_col, control_col]} not found in the dataframe.")
                
        self.data = data.copy()
        self.dimension_cols = dimension_cols
        self.treatment_col = treatment_col
        self.control_col = control_col
        self.dimension_stats_map = {k: pd.DataFrame() for k in self.dimension_cols}
        self.alpha = safe_div(self.data[self.treatment_col].sum(), self.data[self.control_col].sum()) - 1
        
        if self.use_auto_adjusted_min_suprise:
            self.min_surprise = get_adjusted_min_suprise(self.alpha, pc=0.15)
            print(f"{FUNC_NAME}:use auto adjusted min_surprise:{self.min_surprise:.6f} with alpha:{self.alpha:.6f}")
        
        # traverse all dimension columns, calculate the surprise and explanatory
        for _, dimen in enumerate(self.dimension_cols):
            gb = self.data.groupby(dimen)
            joined_df = pd.concat([gb[self.control_col].sum(), gb[self.treatment_col].sum()], axis=1).fillna(0)
            self.calculate_surprise_and_explanatory(joined_df)
            self.dimension_stats_map[dimen] = joined_df.copy()

        # traverse each dimension and get the top root causes
        for _, dimen in enumerate(self.dimension_cols):
            df_candidate = self.get_dimension_candidates(dimen)  
            if df_candidate is None:
                del self.dimension_stats_map[dimen]
            else:
                self.dimension_stats_map[dimen] = df_candidate
                print_verbose_info(
                    message=f"{FUNC_NAME}Dimension:{dimen}, SurpriseCumSum:{df_candidate['Surprise'].sum():.4f}, has {df_candidate.shape[0]} root_causes.",
                    verbose=self.verbose, level=1) 

        print_verbose_info(f"{FUNC_NAME}:adtributor result counts: {[(k,v.shape[0]) for k,v in self.dimension_stats_map.items()]}", verbose=self.verbose, level=1)

        if len(self.dimension_stats_map) == 0:
            print(f"{FUNC_NAME}there is no root cause for all dimensions")
            return pd.DataFrame()

        # sort the dimension by cumulative surprise
        try:
            self.df_adtributor_top_factors = pd.concat([v for _, v in self.dimension_stats_map.items() if v.shape[0] > 0])
        except Exception as e: 
            print(f"{FUNC_NAME}{e}")
            return pd.DataFrame()
        
        res = self.format_output(self.df_adtributor_top_factors)
        print(f"{FUNC_NAME}:final result length: {res.shape[0]}")
        return res


class RecursiveAdtributor(BaseAnalyzer):
    """
    RecursiveAdtributor 
    """
    def __init__(self, top_n_factors,
                 TEEP = 0.05,
                 TEP = 1,
                 min_surprise = 0.0005,
                 max_item_num = 3,
                 max_dimension_num = 1,
                 max_depth = 3,
                 need_negative_ep_factor = False,
                 need_prune = True,
                 verbose = 0):
        """
        top_n_factors: the number of top factors to return
        TEEP: Minimum detectable EP value
        TEP: EP cumulative threshold
        min_surprise: Minimum detectable surprise value
        max_item_num: Maximum number of values for each dimension
        max_dimension_num: The maximum number of dimensions in the Explanatory Set that the Adtributor() will return.
        need_negative_ep_factor: Whether to consider negative Explanatory factors
        need_prune: Whether to prune the result
        dimension_cols must be found in data
        treatment_col and control_col must be found in data
        """
        super().__init__(top_n_factors, verbose=verbose)
        self.TEEP = TEEP
        self.TEP = TEP
        self.min_surprise = min_surprise
        self.max_item_num = max_item_num
        self.max_dimension_num = max_dimension_num
        self.max_depth = max_depth
        self.need_negative_ep_factor = need_negative_ep_factor
        self.need_prune = need_prune

        self.dimension_cols = []
        self.treatment_col = "Treatment"
        self.control_col = "Control"
        self.single_adtributor = Adtributor(
            top_n_factors=self.top_n_factors,
            TEEP=self.TEEP,
            TEP=self.TEP,
            min_surprise=self.min_surprise,
            max_item_num=self.max_item_num,
            need_negative_ep_factor=self.need_negative_ep_factor,
            verbose=self.verbose)
        
        print(f"""{__class__.__name__}:initialize a single_adtributor:{self.single_adtributor}(
            top_n_factors={self.top_n_factors},
            TEEP={self.TEEP},
            TEP={self.TEP},
            min_surprise={self.min_surprise},
            max_item_num={self.max_item_num},
            need_negative_ep_factor={self.need_negative_ep_factor},
            verbose={self.verbose})""")

        self.depth = 0
        self.df_adtributor_top_factors = pd.DataFrame()


    def recursive_analyze(self, data: pd.DataFrame, dimension_cols: list, depth: int, parent_dict={}) -> pd.DataFrame:
        """
        recursively analyze the subcubes, and return the root cause groups
        data: pandas DataFrame with columns:[*dimension_cols], treatment_col, control_col]
        dimension_cols must be found in data
        depth: the depth of the recursive tree
        """
        FUNC_NAME = f"{__class__.__name__}|{get_current_function()}|"
        if depth >= self.max_depth:
            print(f"{FUNC_NAME}Warning: the depth:{depth} exceeds the max_depth:{self.max_depth}")
            return pd.DataFrame()

        data = data.copy()
        dimension_cols = dimension_cols.copy()
        print_verbose_info(f"{FUNC_NAME}depth:{depth}, dimension_cols:{dimension_cols}, input df rows:{data.shape[0]}", verbose=self.verbose, level=1)
        
        # implement the single_adtributor
        explanatorySet = self.single_adtributor.analyze(data, dimension_cols, self.treatment_col, self.control_col)
        # explanatorySet be like:
        #   Dimension        Value  Surprise  Explanatory  DimensionSurprise
        #   PageName  WeatherMaps  0.006513     0.795854           0.006513
        
        if explanatorySet.shape[0] == 0:
            print(f"{FUNC_NAME}there is no result from single_adtributor.")
            return explanatorySet
        
        # record the group and depth
        explanatorySet["Group"] = explanatorySet["Dimension"] + ":" + explanatorySet["Value"]
        explanatorySet["Depth"] = depth

        # update the columns by parent dict
        explanatorySet["P_t"] = explanatorySet["P_t"] * parent_dict.get("P_t", 1.0)
        explanatorySet["P_c"] = explanatorySet["P_c"] * parent_dict.get("P_c", 1.0)

        # filter out the items with small Explanatory
        explanatorySet["Explanatory"] = explanatorySet["Explanatory"] * parent_dict.get("Explanatory", 1.0)
        explanatorySet["ParentExplanatory"] = parent_dict.get("Explanatory", 1.0)
        
        if self.need_negative_ep_factor:
            explanatorySet = explanatorySet[explanatorySet["Explanatory"].abs() >= self.TEEP]
        else:
            explanatorySet = explanatorySet[explanatorySet["Explanatory"] >= self.TEEP]
        
        if self.verbose:
            print(f"{FUNC_NAME}depth:{depth}, explanatorySet:{explanatorySet.shape[0]} after filter.")
            print(f"{FUNC_NAME}explanatorySet columns: {list(explanatorySet.columns)}")

        if explanatorySet.shape[0] == 0:
            print(f"{FUNC_NAME}there is no root cause after *parentExplanatory.")
            return explanatorySet
        
        res = explanatorySet
        # get explanatory set, using top max_dimension_num dimensions
        top_dimensions = explanatorySet.groupby("Dimension")["DimensionSurprise"].max().sort_values(ascending=False).head(self.max_dimension_num)
        if self.verbose:
            print(f"{FUNC_NAME}depth:{depth}, top_dimensions:{top_dimensions.index.to_list()}")

        # traverse all dimensions
        for d in top_dimensions.index:
            print(f"\t{FUNC_NAME}depth:{depth}, do dimension:{d}, dimension_cols:{dimension_cols}")
            if d not in dimension_cols:
                print_verbose_info(f"{FUNC_NAME}dimension:{d} not in dimension_cols:{dimension_cols}", verbose=self.verbose, level=2)
                continue
            dimension_cols.remove(d)
            # if the dimension is not leaf, recursively analyze the subcubes
            if len(dimension_cols) == 0:
                print_verbose_info(f"{FUNC_NAME}dimension_cols is empty, skip.", verbose=self.verbose, level=2)
                continue
            candidateSet = explanatorySet[explanatorySet['Dimension'] == d]["Value"].values
            if len(candidateSet) == 0:
                print_verbose_info(f"{FUNC_NAME}dimension:{d} has no candidateSet, skip.", verbose=self.verbose, level=2)
                continue
            # traverse all subcubes
            for subcube in candidateSet:
                print(f"\t\t{FUNC_NAME}depth:{depth}, do subcube:{d}={subcube}")
                sub_dict = {
                    "P_t": explanatorySet[(explanatorySet['Dimension'] == d) & (explanatorySet['Value'] == subcube)]["P_t"].values[0],
                    "P_c": explanatorySet[(explanatorySet['Dimension'] == d) & (explanatorySet['Value'] == subcube)]["P_c"].values[0],
                    "Explanatory": explanatorySet[(explanatorySet['Dimension'] == d) & (explanatorySet['Value'] == subcube)]["Explanatory"].values[0]
                }
                # sub_EP = explanatorySet[(explanatorySet['Dimension'] == d) & (explanatorySet['Value'] == subcube)]["Explanatory"].values[0]
                sub_data = data[data[d] == subcube][dimension_cols+[self.treatment_col, self.control_col]]
                sub_explanatorySet = self.recursive_analyze(sub_data, dimension_cols, depth+1, sub_dict)

                if sub_explanatorySet is not None and sub_explanatorySet.shape[0] > 0:
                    print(f"\t\t{FUNC_NAME}subcube:{d}={subcube}, get sub_explanatorySet:{sub_explanatorySet['Group'].values}")
                    sub_explanatorySet["Group"] = f"{d}:{subcube}>" + sub_explanatorySet["Group"]
                    res = pd.concat([res, sub_explanatorySet])
                else:
                    print(f"\t\t{FUNC_NAME}recursive_analyze(depth = {depth}), there is no root cause for subcube:{d}={subcube}")
                    
            # dimension_cols.append(d)  # drop "d" to avoid redundant group
        
        if self.need_prune:
            return self.prune(res)
        
        print_verbose_info(f"{FUNC_NAME}depth:{depth}, final result length: {res.shape[0]}", verbose=self.verbose, level=2)
        return res


    def prune(self, df: pd.DataFrame):
        """
        prune the dataframe, only keep the rows with the highest Explanatory and smallest Depth
        """
        df = df.copy()
        df.sort_values(by=["Depth", "Explanatory"], ascending=[True, False], inplace=True)
        df.drop_duplicates(subset=["Dimension", "Value"], keep="first", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df


    def format_output(self, df: pd.DataFrame):
        """
        return a formatted result dataframe
        """
        df = df.copy()
        df = df.sort_values(by=["Depth", "Explanatory", "Surprise"], ascending=[True, False, False]).reset_index(drop=True)
        # rename the columns like adtributor's result
        df["Dimension"] = "Group"
        df["Value"] = df["Group"]
        return df[['Depth', 'Dimension', 'Value', 'Surprise', 'P_t', 'P_c', 'Delta%', 'Explanatory', 'DimensionSurprise']].head(self.top_n_factors)
    

    def analyze(self, data: pd.DataFrame,                  
                dimension_cols = [], 
                treatment_col = "Treatment", 
                control_col= "Control") -> pd.DataFrame:
        """
        dimension_cols must be found in data
        treatment_col_name and control_col_name must be found in data
        """
        FUNC_NAME = f"{__class__.__name__}|{get_current_function()}|"
        # check the input data
        if len(dimension_cols) == 0:
            raise Exception(f"dimension_cols CANNOT be empty.")
        if not set(dimension_cols + [treatment_col, control_col]).issubset(set(data.columns)):
            raise Exception(f"Columns:{dimension_cols + [treatment_col, control_col]} not found in the dataframe.")
                
        self.data = data.copy()
        self.dimension_cols = dimension_cols
        self.treatment_col = treatment_col
        self.control_col = control_col
        self.dimension_stats_map = {k: pd.DataFrame() for k in self.dimension_cols}

        res = self.recursive_analyze(data, self.dimension_cols, depth=0)
        self.df_adtributor_top_factors = res

        if res.shape[0] == 0:
            print(f"{FUNC_NAME}there is no root cause for final result.")
            return pd.DataFrame()
        
        res = self.format_output(res)
        print(f"{FUNC_NAME}:final result length: {res.shape[0]}")
        return res
        