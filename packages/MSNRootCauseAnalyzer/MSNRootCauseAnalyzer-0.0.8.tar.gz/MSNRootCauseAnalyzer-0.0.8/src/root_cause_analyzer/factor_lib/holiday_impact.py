import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from holidays import country_holidays

from .base_impact_analyzer import BaseImpactAnalyzer
from ..tools import query_utils
from ..utils import safe_div, get_current_function, print_df_as_table, get_country_code_with_pycountry

class HolidayImpactAnalyzer(BaseImpactAnalyzer):
    def __init__(self, titan_api, metric, 
                 treatment_date = None, 
                 control_date = None, 
                 time_mode = "Day",
                 metric_query_map = {},
                 combine_metric_query_map = {},
                 verbose = 0):
        
        super().__init__(metric, treatment_date, control_date, time_mode, verbose)
        
        # initialize the data fetcher
        self.titan_api = titan_api
        self.metric_query_map = metric_query_map
        self.combine_metric_query_map = combine_metric_query_map
        self._build_metric_query_str()
        
        # initialize the result dataframe
        self.report_holiday_impact = pd.DataFrame()  # report by holiday impact
        print(f"Init HolidayImpactAnalyzer.")


    # ======================== public methods ========================
    def run_holiday_impact_analysis(self, filter_str, market_values, use_cache = False):
        """
        Run holiday impact analysis on the given data.
        """
        FUNC_NAME = f"{get_current_function()}|"
        
        # TODO: if market_values is empty (means worldwide), set default value as ['en-us']
        market_values = market_values if market_values else ['en-us']
        print(f"{FUNC_NAME} market_values:{market_values}")

        if use_cache \
            and not self.report_holiday_impact.empty:
            print(f"{FUNC_NAME} metric:{self.metric} | get data from cache.")
            self.result_dict["report"] = self.report_holiday_impact.copy()
            pass
        else:
            self.report_holiday_impact = pd.DataFrame()
            for mkt in market_values:
                df_holiday_impact = self.run_holiday_impact_by_market(filter_str, mkt)
                if df_holiday_impact.empty:
                    print(f"{FUNC_NAME} Error: No holiday data found for market:{mkt}.")
                    continue
                self.report_holiday_impact = pd.concat([self.report_holiday_impact, df_holiday_impact], axis=0)

        if len(market_values) == 0 or self.report_holiday_impact.empty:
            print(f"{FUNC_NAME} Error: No holiday data found for market:{market_values}.")
            return 
        
        print_df_as_table(
            self.report_holiday_impact,
            title = f"Holiday Contribution on {self.treatment_date} in {','.join(market_values)}",
            console_width=150,
            column_styles={
                "HolidayContribution%": "black bold"}
        )

        # Update the result_dict
        self.result_dict["report"] = self.report_holiday_impact.copy()

        return 
    

    def run_holiday_impact_by_market(self, filter_str, market):
        """
        Decription: 
        Return the recent N days holiday impact analysis result for a given market.
        TODO: 
        1. cannot including non-public holiday, e.g. halloween
        2. haven't test for Adjusted Work Day
        """
        FUNC_NAME = f"{get_current_function()}|"
        print(f"{FUNC_NAME} Input: market:{market}, filter_str:{filter_str}")
        
        # get country code
        country_code = get_country_code_with_pycountry(market)
        # get holiday object
        treatment_date = datetime.strptime(self.treatment_date, "%Y-%m-%d")
        start_year = treatment_date.year if treatment_date.month == 12 and treatment_date.day >= 30 else treatment_date.year - 1
        end_year = start_year + 1
        print(f"{FUNC_NAME} start_year: {start_year}, end_year: {end_year}, country_code: {country_code}")
        holidays_obj = country_holidays(country_code, years=range(start_year, end_year), language='en_US', observed = True)
        
        # TODO: How long will the holiday impact the users' behavior, if it was set too short, impact will be hard to detacted. If it is set too long, there may be overlaps with upcoming holidays that are close to the date.
        # Get the holiday name for the past 4 days and the next 2 days. Assume the holiday impact will last for 7 days.
        days_diff = 0
        for i in range(4, -3, -1):
            holiday_date = treatment_date + timedelta(days=i)
            holiday_name = holidays_obj.get(holiday_date)
            if holiday_name:
                days_diff = i
                print(f"{FUNC_NAME} holiday_name: {holiday_name}, days_diff: {days_diff}")
                break
        if holiday_name is None:
            return pd.DataFrame()

        # get holiday date in last year
        lastyear_holiday_date = None
        for k, v in sorted(holidays_obj.items()):
            # when the holiday_name looks like "New Year's Day (observed)"
            # will return the first holiday date
            if holiday_name in v:
                if k.year == start_year:
                    lastyear_holiday_date = k
        
        if lastyear_holiday_date is None:
            return pd.DataFrame()

        print(f"{FUNC_NAME} lastyear_holiday_date: {lastyear_holiday_date}")
        delta_days = datetime.strptime(self.treatment_date, "%Y-%m-%d") - datetime.strptime(self.control_date, "%Y-%m-%d")
        lastyear_treatment_date = (lastyear_holiday_date + timedelta(days= -days_diff)).strftime("%Y-%m-%d")
        lastyear_control_date = (lastyear_holiday_date + timedelta(days= -days_diff) - delta_days).strftime("%Y-%m-%d")
        
        # build filter query
        market_filter = f" lower(Market) = '{market}'"
        if filter_str is not None and len(filter_str.strip()) > 0:
            filter_str = f" ({market_filter}) AND ({filter_str}) "
        else:
            filter_str = market_filter
        print(f"{FUNC_NAME} FINAL filter_str:{filter_str}")

        df_lastyear = query_utils.get_df_metric_comparison(
            self.titan_api, self.metric, 
            lastyear_treatment_date, lastyear_control_date, self.time_mode, filter_str,
            metric_query_str = self.metric_query_str,
            metric_query_map = self.metric_query_map,
            combine_metric_query_map = self.combine_metric_query_map,
            metric_set = [self.metric]
            )
        df_thisyear = query_utils.get_df_metric_comparison(
            self.titan_api, self.metric,
            self.treatment_date, self.control_date, self.time_mode, filter_str,
            metric_query_str = self.metric_query_str,
            metric_query_map = self.metric_query_map,
            combine_metric_query_map = self.combine_metric_query_map,
            metric_set = [self.metric]
            )
        if df_lastyear.empty or df_thisyear.empty:
            print(f"{FUNC_NAME} Error: No data found for market:{market}.")
            return pd.DataFrame()
        
        df_lastyear["Delta%"] = df_lastyear[[f"{self.metric}_t", f"{self.metric}_c"]].apply(
            lambda x: safe_div((x[f"{self.metric}_t"] - x[f"{self.metric}_c"]), x[f"{self.metric}_c"]), axis=1)        
        df_thisyear["Delta%"] = df_thisyear[[f"{self.metric}_t", f"{self.metric}_c"]].apply(
            lambda x: safe_div((x[f"{self.metric}_t"] - x[f"{self.metric}_c"]), x[f"{self.metric}_c"]), axis=1)
        
        # concatenate the result in one dataframe
        result = pd.DataFrame({
            "Country": [country_code, country_code],
            "HolidayName": [holiday_name, holiday_name],
            "TreatDate": [self.treatment_date, lastyear_treatment_date],
            "ControlDate": [self.control_date, lastyear_control_date],
            "Delta%": [df_thisyear["Delta%"].values[0], df_lastyear["Delta%"].values[0]]
        })

        # use delta in holiday_date / delta in treatment_date to calculate the impact contribution
        result["HolidayContribution%"] = result["Delta%"].shift(-1) / result["Delta%"]
        result["HolidayContribution%"] = result["HolidayContribution%"].apply(
            lambda x: ">95%" if x > 0.95 else "" if np.isnan(x) else f"{x:.2%}")
        # format the number to percentage format
        result["Delta%"] = result["Delta%"].apply(lambda x: f"{x:.2%}")
        
        return result
    

    # ======================== private methods ========================
    def _build_metric_query_str(self):
        """
        e.g. metric_query_str:SUM(mCFV_FY24), combine_metric_query_map:{'PV/UU': 'PV / UU'}
        """
        FUNC_NAME = f"{get_current_function()}|"
        # if metric is in the metric_query_map, use the direct query string
        if self.metric in self.metric_query_map:
            query = self.metric_query_map[self.metric]
            self.metric_query_str = f"{query} AS `{self.metric}` "  
            self.metric_query_map = {self.metric: query}
            self.combine_metric_query_map = {}
        else:
            self.metric_query_str = "\n, ".join([f" {v} AS `{k}`" for k, v in self.metric_query_map.items()])
            if self.combine_metric_query_map:
                self.metric_query_str += " \n, " + "\n, ".join([f" {v} AS `{k}`" for k, v in self.combine_metric_query_map.items()])
        
        if self.verbose:
            print(f"{FUNC_NAME} metric_query_str:{self.metric_query_str}")
            print(f"{FUNC_NAME} metric_query_map:{self.metric_query_map}")
            print(f"{FUNC_NAME} combine_metric_query_map:{self.combine_metric_query_map}")