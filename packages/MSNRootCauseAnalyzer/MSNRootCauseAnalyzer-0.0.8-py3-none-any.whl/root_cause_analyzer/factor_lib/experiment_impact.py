# experiment_impact.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .base_impact_analyzer import BaseImpactAnalyzer
from ..tools import query_utils
from ..tools.constants import *
from ..utils import get_current_function, print_df_as_table

class ExperimentImpactAnalyzer(BaseImpactAnalyzer):
    def __init__(self, azure_db_api, metric, 
                 treatment_date = None, 
                 control_date = None, 
                 time_mode = "Day",
                 global_delta = None,
                 verbose = 0):
        
        super().__init__(metric, treatment_date, control_date, time_mode, verbose)
        
        # initialize the data fetcher
        self.azure_db_api = azure_db_api
        self.global_delta = global_delta *20  # TODO: ensure the global_delta is upscaled.

        if self.global_delta is None or abs(self.global_delta) < 1e-6:
            raise ValueError("Error: global_delta is None or too small.")
        
        print(f"Init ExperimentImpactAnalyzer: delta of {self.metric} :{self.global_delta:.2f}")

    # ======================== public methods ========================
    def run_experiment_impact_analysis(self, filter_str, filter_markets_list = []):
        """
        run_experiment_attribution
        self.treatment_date = treatment_date
        self.control_date = control_date
        self.time_mode = time_mode
        """
        FUNC_NAME = f"{get_current_function()}|"

        # check if the db connection is valid
        if not self.azure_db_api.connection:
            print(f"{FUNC_NAME}Error: No database connection found.")
            return

        # transform the metric name to internal metric name
        if self.metric not in EXP_METRIC_NAME_MAP:
            print(f"{FUNC_NAME} Error: {self.metric} is not supported.")
            return
        InternalMetricName = EXP_METRIC_NAME_MAP[self.metric]

        # get the time range for the experiment
        TreatmentStartDateTime = self.treatment_date + " 00:00:00"
        ControlStartDateTime = self.control_date + " 00:00:00"
        TreatmentEndDateTime = self.treatment_date + " 23:59:59"
        ControlEndDateTime = self.control_date + " 23:59:59"

        # Fetch the experiments that have a negative impact on the metric and are running within the specified time range.
        market_filter = "" if len(filter_markets_list) == 0 else "," + ",".join([f"'{m.lower()}'" for m in filter_markets_list])
        sql = f"""
            SELECT ExperimentName, Owners, ManagementGroup, ExperimentStepLink, lower(Market)AS Market
            , AnalysisStartDateTime, AnalysisEndDateTime, ExperimentState
            , InternalMetricName, DeltaRelative, ImpactValue, IsRegression
            , ControlTrafficSize, TreatmentTrafficSize, LastModifyTimeUTC
            FROM [dbo].[ArenaNegativeMetricRecord]
            WHERE 
            AnalysisStartDateTime >= '{ControlEndDateTime}' 
            AND AnalysisStartDateTime < '{TreatmentStartDateTime}'
            AND (
                AnalysisEndDateTime >= '{TreatmentEndDateTime}'
                OR LastModifyTimeUTC >= '{TreatmentEndDateTime}'
                )
            AND InternalMetricName = '{InternalMetricName}' 
            AND DeltaRelative < 0 AND ImpactValue < 0
            AND lower(Market) IN ('aggregate' {market_filter})
        """
        print(f"=================sql:====================\n{sql}\n========================================")

        df = pd.DataFrame()
        try:
            df = pd.read_sql(sql, self.azure_db_api.connection)
            if self.verbose:
                print(f"{FUNC_NAME} [dbo].[ArenaNegativeMetricRecord] returns:{df.shape[0]}, columns:{df.columns}")
        except Exception as e:
            print(f"{FUNC_NAME} {e}")
            return

        if df.empty:
            print(f"{FUNC_NAME} Error: No data found in [dbo].[ArenaNegativeMetricRecord].")
            return

        # estimate the impact of each experiment, using df["ImpactValue"] / global_delta, ImpactValue is a daily value.
        df["ExpContribution%"] = df["ImpactValue"] / self.global_delta

        # calculate the relevance of each experiment, using knowledge_mapping
        df = self._match_exp_filter(df, filter_str)

        # update the result_dict
        self.result_dict["mid_result"] = df
        self.result_dict["report"] = df[df["ExpContribution%"] >= EXP_MIN_SIG_EXP_CONTRIBUTION]\
            .sort_values(by="ExpContribution%", ascending=False)\
            .drop_duplicates(subset=["ExperimentName","ExperimentStepLink"], keep='first')

        # Display the experiments that have a significant impact on the metric movement
        self._format_exp_impact_report(df)
    
        return


    # ======================== private methods ========================
    def _match_exp_filter(self, df_input, filter):
        """
        Description: match the filter string with the experiment information, and calculate the cosine similarity between them.
        """
        df = df_input.copy()
        
        # extract the bracket content from the "ExperimentName", and map it to the knowledge_mapping
        df["bracket_content"] = df["ExperimentName"].str.extract(r'\[(.*?)\]')
        df["bracket_content"] = df["bracket_content"].str.lower().str.replace(r'[^a-zA-Z0-9]', '', regex=True)
        df["knowledge"] = df["bracket_content"].map(KNOWLEDGE_MAPPING)
        
        # clean up the confusing characters in the "ManagementGroup"
        df["ManagementGroup2"] = df["ManagementGroup"].replace("/MSN/", "").replace("ICE-AnaheimEdgeId", "")
        df["exp_info"] = df["ExperimentName"].fillna("") + " " + df["knowledge"].fillna("") + " " + df["ManagementGroup2"].fillna("")
        
        # create a TfidfVectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([filter] + df["exp_info"].tolist())

        # add a new column to df, which is the cosine similarity between filter and ExperimentName
        df["cosine_similarity"] = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]

        # sort by cosine_similarity
        df = df.sort_values(by="cosine_similarity", ascending=False).reset_index(drop=True)
        return df
    

    def _format_exp_impact_report(self, df):
        """
        Description: format the experiment impact report and divide it into two parts:
        1. Experiments Relevant to the Metric Movement Under Filter Condition: df_relevent
        2. Experiments with Significant Impact: df_sig
        """
        fmt_df = df.copy()

        fmt_df["abs_ImpactValue"] = fmt_df["ImpactValue"].abs()
        fmt_df["r_ExpContribution%"] = fmt_df["ExpContribution%"].apply(lambda x: f">95%" if x > 0.95 else f"{x*100:.2f}%")
        fmt_df["r_DeltaRelative"] = fmt_df["DeltaRelative"].apply(lambda x: f"{x*100:.2f}%")
        fmt_df["r_ImpactValue"] = fmt_df["ImpactValue"].apply(lambda x: f"{x:.2f}")
        fmt_df["r_AnalysisStartDateTime"] = pd.to_datetime(fmt_df["AnalysisStartDateTime"]).dt.strftime("%Y/%m/%d")
        fmt_df["r_AnalysisEndDateTime"] = pd.to_datetime(fmt_df["AnalysisEndDateTime"]).dt.strftime("%Y/%m/%d")
        fmt_df["r_LastModifyTimeUTC"] = pd.to_datetime(fmt_df["LastModifyTimeUTC"]).dt.strftime("%Y/%m/%d")

        fmt_df = fmt_df[["ExperimentName", "Owners", "ManagementGroup", "ExperimentStepLink", \
                        "Market", "r_AnalysisStartDateTime", "r_AnalysisEndDateTime", "r_LastModifyTimeUTC", "ExperimentState", \
                        "InternalMetricName", "r_DeltaRelative", "r_ImpactValue", "r_ExpContribution%", \
                        "IsRegression", "ControlTrafficSize", "TreatmentTrafficSize", "cosine_similarity", "knowledge",\
                        "abs_ImpactValue"]]
        
        # rename columns with r_ prefix
        fmt_df.columns = [col[2:] if col.startswith("r_") else col for col in fmt_df.columns]
        
        # TODO: the threshold of the cosine_similarity and ExpContribution% should be adjusted
        # Since there's no numerical data in the fmt_df, so we use the df to filter the data
        df_relevent = fmt_df[(df["cosine_similarity"] >= EXP_MIN_COSINE_SIMILARITY) & (df["ExpContribution%"] >= EXP_MIN_RELATED_EXP_CONTRIBUTION)]
        df_sig = fmt_df[(df['IsRegression']) & (df["cosine_similarity"] < EXP_MIN_COSINE_SIMILARITY) & (df["ExpContribution%"] >= EXP_MIN_SIG_EXP_CONTRIBUTION)]
        
        # drop duplicates and sort by abs_ImpactValue
        df_relevent = df_relevent.sort_values(by="abs_ImpactValue", ascending=False)\
            .drop_duplicates(subset=["ExperimentName","ExperimentStepLink"], keep='first')\
            .reset_index(drop=True)
        
        df_sig = df_sig.sort_values(by="abs_ImpactValue", ascending=False)\
            .drop_duplicates(subset=["ExperimentName","ExperimentStepLink"], keep='first')\
            .reset_index(drop=True)

        report_columns = ["ExperimentName", "DeltaRelative", "ImpactValue", "IsRegression", \
                          "ExpContribution%", "Owners", "ManagementGroup", "ExperimentStepLink", \
                          "Market", "AnalysisStartDateTime", "LastModifyTimeUTC", "ExperimentState", \
                          "ControlTrafficSize", "TreatmentTrafficSize"]
        print_df_as_table(
            df_relevent[report_columns],
            title="Experiments Relevant to the Metric Movement Under Filter Condition",
            console_width=200,
            column_widths={"ExperimentName": 15, "ExperimentStepLink": 20}
        )

        print_df_as_table(
            df_sig[report_columns],
            title="Experiments with Significant Impact",
            console_width=200,
            column_widths={"ExperimentName": 15, "ExperimentStepLink": 20}
        )
        return
