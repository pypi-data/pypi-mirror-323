# Description: This file contains the functions to build the query for the root cause analysis.

import pandas as pd
from datetime import datetime, timedelta

from . import data_ops
from ..titan.titan_api import TitanApi
from ..utils import MathOperations, get_current_function

def build_date_query(treatment_date, control_date, time_mode):
    date_query = ""
    date_filter = ""
    ret = 0
    if time_mode == "Day":
        date_query = f"EventDate = toDate('{treatment_date}')"
        date_filter = f"(EventDate = toDate('{treatment_date}') OR EventDate = toDate('{control_date}'))"
        return ret, date_query, date_filter
    
    elif time_mode == "R7":
        start_date_t = datetime.strptime(treatment_date, "%Y-%m-%d") - timedelta(days=6)
        start_date_c = datetime.strptime(control_date, "%Y-%m-%d") - timedelta(days=6)
        date_filter = f"""((EventDate >= toDate('{start_date_t}') AND EventDate <= toDate('{treatment_date}')) 
                        OR (EventDate >= toDate('{start_date_c}') AND EventDate <= toDate('{control_date}')))"""
        date_query = f"(EventDate >= toDate('{start_date_t}') AND EventDate <= toDate('{treatment_date}'))"
        return ret, date_query, date_filter
    
    elif time_mode == "R28":
        start_date_t = datetime.strptime(treatment_date, "%Y-%m-%d") - timedelta(days=27)
        start_date_c = datetime.strptime(control_date, "%Y-%m-%d") - timedelta(days=27)
        date_filter = f"""((EventDate >= toDate('{start_date_t}') AND EventDate <= toDate('{treatment_date}')) 
                        OR (EventDate >= toDate('{start_date_c}') AND EventDate <= toDate('{control_date}')))"""
        date_query = f"(EventDate >= toDate('{start_date_t}') AND EventDate <= toDate('{treatment_date}'))"
        return ret, date_query, date_filter
    else:
        return 1, date_query, date_filter
    

def build_titan_query(treatment_date, 
                      control_date, 
                      time_mode, 
                      metric_query_str, 
                      filter_str = "", 
                      group_by_cols = []):
    """
    Description: This function builds the basic titan query.
    Parameters:
        - treatment_date: The treatment date.
        - control_date: The control date.
        - time_mode: The time mode.
        - metric_query_str: The metric query string.
        - filter_str: The filter string.
        - group_by_cols: The group by columns.
    """
    ret, date_query, date_filter = build_date_query(treatment_date, control_date, time_mode)
    if ret:
        return None
    
    # only columns alias
    clean_group_by_cols = ','.join(list(map(lambda x: x.split("AS ")[-1].strip(), group_by_cols)))
    dimensions_str = ",".join(group_by_cols)

    clean_group_by_cols = f", {clean_group_by_cols}" if len(clean_group_by_cols.strip())>0 else ""
    dimensions_str = f", {dimensions_str}" if len(dimensions_str.strip())>0 else ""


    wrap_filter_str = f"AND ({filter_str})" if filter_str.strip() else ""
    sql = f"""
        SELECT IF({date_query}, 'Treatment', 'Control') AS Group, toDate(EventDate) AS Date {dimensions_str},
               {metric_query_str}
        FROM MSNAnalytics_Sample
        WHERE {date_filter} 
              AND IsNotExcludedStandard_FY24 = 1 {wrap_filter_str}
        GROUP BY Group, Date {clean_group_by_cols} 
    """
    #  settings distributed_group_by_no_merge=1) 
    return sql


def build_advanced_titan_query(treatment_date, 
                      control_date, 
                      time_mode, 
                      metric_query_map = {},
                      combine_metric_query_map = {}, 
                      filter_str = "", 
                      group_by_cols = []):
    """
    Description: This function builds the advanced titan query with performance optimization.
    set timeout 3 mins for titan query
    """
    ret, date_query, date_filter = build_date_query(treatment_date, control_date, time_mode)
    if ret:
        return None
    
    # only columns alias
    clean_group_by_cols = ','.join(list(map(lambda x: x.split("AS ")[-1].strip(), group_by_cols)))
    dimensions_str = ",".join(group_by_cols)

    clean_group_by_cols = f", {clean_group_by_cols}" if len(clean_group_by_cols.strip())>0 else ""
    dimensions_str = f", {dimensions_str}" if len(dimensions_str.strip())>0 else ""

    # build filter string
    wrap_filter_str = f"AND ({filter_str})" if filter_str.strip() else ""

    # build metric query string
    # metric_query_str = "\n, ".join([f" {v} AS `{k}`" for k, v in metric_query_map.items()])
    metric_query_list = []
    wrap_metric_query_list = []
    combine_metric_query_list = []
    
    for metric_name, metric_query in metric_query_map.items():
        if "/" in metric_name:
            # print(f"Warning: metric name {metric_name} contains illegal character '/', please check your input!")
            a = metric_name.split("/")[0]
            b = "/".join(metric_name.split("/")[1:])
            combine_metric_query_map[metric_name] = f"{a} / {b}"
            continue
        metric_query_list.append(f" {metric_query} AS `{metric_name}`")
        wrap_metric_query_list.append(f" SUM({metric_name}) AS `{metric_name}`")

    metric_query_str = "\n, ".join(metric_query_list)
    wrap_metric_query_str = "\n, ".join(wrap_metric_query_list)

    for metric_name, metric_query in combine_metric_query_map.items():
        combine_metric_query_list.append(f" {metric_query} AS `{metric_name}`")
    combine_metric_query_str = "\n," + ", ".join(combine_metric_query_list) if len(combine_metric_query_list) > 0 else ""

    sql = f"""SELECT Group, Date {clean_group_by_cols}, 
    {wrap_metric_query_str}
    {combine_metric_query_str}
    FROM
    (SELECT IF({date_query}, 'Treatment', 'Control') AS Group, toDate(EventDate) AS Date {dimensions_str},
    {metric_query_str}
    FROM MSNAnalytics_Sample
    WHERE {date_filter} 
        AND IsNotExcludedStandard_FY24 = 1 {wrap_filter_str}
    GROUP BY Group, Date {clean_group_by_cols}  
    settings distributed_group_by_no_merge=1, max_execution_time = 180
    ) GROUP BY Group, Date {clean_group_by_cols} """

    return sql


def merge_filter_query(filter_str="", market_list=[]):

    res = ""
    if filter_str and len(filter_str.strip()) > 0:
        res = filter_str
    if market_list and len(market_list) > 0:
        market_str = ",".join([f"'{m}'" for m in market_list])
        if res:
            res = f"({res}) AND lower(Market) IN ({market_str})"
        else:
            res = f"lower(Market) IN ({market_str})"

    return res


def build_combined_metric_query(formula = [], op_type = MathOperations.ADDITION, coefficient = []):
    """
    build combined metric query
    """
    query_str = ""
    if len(formula) != len(coefficient) or len(formula) < 1:
        return query_str
    # if coefficient = 1， then ignore it
    new_formula = [f"{formula[i]}" if coefficient[i] == 1 else f"({formula[i]} * {coefficient[i]})" for i in range(len(formula))]
    if op_type == MathOperations.ADDITION:
        query_str = " + ".join(new_formula)
    elif op_type == MathOperations.MULTIPLICATION:
        query_str = " * ".join(new_formula)
    elif op_type == MathOperations.DIVISION:
        query_str = " / ".join(new_formula)
    return query_str


def get_df_metric_comparison(titan_api:TitanApi, 
                             metric:str, 
                             treatment_date:str, control_date:str, time_mode:str, 
                             filter_str:str, 
                             metric_query_str:str,
                             metric_query_map:dict, 
                             combine_metric_query_map:dict,
                             metric_set:list):
    """
    Description: Get metric comparison data based on the given treatment date, control date, time mode, and filter string.
    """
    FUNC_NAME = f"{get_current_function()}|"

    # TODO: remove the hard code
    if metric in ['FVR']:
        sql = build_titan_query(treatment_date, control_date, time_mode, metric_query_str, filter_str)
    else:
        sql = build_advanced_titan_query(treatment_date, control_date, time_mode, 
                                                    metric_query_map=metric_query_map, 
                                                    combine_metric_query_map=combine_metric_query_map, 
                                                    filter_str=filter_str)
    if sql is None:
        print(f"{FUNC_NAME} Error: Invalid Titan query.")
        return pd.DataFrame()
    
    print(f"{FUNC_NAME}\n=================sql:====================\n{sql}\n========================================")
    data = titan_api.query_clickhouse(sql, "MSNAnalytics_Sample")
    if not data:
        print(f"{FUNC_NAME}Error:No data returned. Please check the Titan query or the Titan API:{titan_api.endpoint}.")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if df.empty or not df["Group"].isin(["Treatment", "Control"]).all():
        print(f"{FUNC_NAME}Error:No data returned. Please check the Titan query or the Titan API:{titan_api.endpoint}.")
        return pd.DataFrame()
    
    # merge two dataframes
    data_ops.cast_metric_dtype(df, metric_set)
    df = df.groupby(["Group"])[list(metric_set)].mean().reset_index(drop=False)
    df["key"] = 1
    df_treat = df[df["Group"] == "Treatment"]
    df_ctrl = df[df["Group"] == "Control"]
    df_metric_comp = pd.merge(df_treat, df_ctrl, on=['key'], suffixes=('_t', '_c')).fillna(0)
    return df_metric_comp


def get_metric_comparison_by_customized_dimension(
        titan_api:TitanApi, 
        metric:str, 
        treatment_date:str, control_date:str, time_mode:str, 
        filter_str:str, 
        metric_query_str:str,
        metric_query_map:dict, 
        combine_metric_query_map:dict,
        metric_set:list,
        dimension_list:list, 
        clean_dimension_list:list):        
    """
    Description: Get metric comparison data group by customized dimensions.
    Parameters:
        - filter_str: The filter string.
        - dimension_list: The list of dimensions. ["COL AS Alias"]
    """
    FUNC_NAME = f"{get_current_function()}|"
    # TODO: remove the hard code
    if metric in ['FVR']:
        sql = build_titan_query(treatment_date, 
                                control_date, 
                                time_mode,
                                metric_query_str, 
                                filter_str, 
                                dimension_list)
    else:
        sql = build_advanced_titan_query(treatment_date, control_date, time_mode, 
                                        metric_query_map = metric_query_map, 
                                        combine_metric_query_map = combine_metric_query_map, 
                                        filter_str=filter_str,
                                        group_by_cols=dimension_list)
    if sql is None:
        print(f"{FUNC_NAME} Error: Invalid Titan query.")
        return pd.DataFrame()
    
    print(f"{FUNC_NAME}\n=================sql:====================\n{sql}\n========================================")
    data = titan_api.query_clickhouse(sql, "MSNAnalytics_Sample")
    if not data:
        print(f"{FUNC_NAME}Error:No data returned. Please check the Titan query or the Titan API:{titan_api.endpoint}.")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if df.empty or not df["Group"].isin(["Treatment", "Control"]).all():
        print(f"{FUNC_NAME}Error:No data returned. Please check the Titan query or the Titan API:{titan_api.endpoint}.")
        return pd.DataFrame()
    
    # merge two dataframes
    data_ops.cast_metric_dtype(df, metric_set)
    df = df.groupby(["Group"] + clean_dimension_list)[list(metric_set)].mean().reset_index(drop=False)
    df_treat = df[df["Group"] == "Treatment"]
    df_ctrl = df[df["Group"] == "Control"]
    df = pd.merge(df_treat, df_ctrl, on = clean_dimension_list, how="outer", suffixes=["_t", "_c"]).fillna(0)
    return df


if __name__ == "__main__":
    # test build_date_query
    treatment_date = "2024-12-22"
    control_date = "2024-12-15"
    time_mode = "R7"
    metric_query_str = "SUM(Count) AS Count"
    filter_str = "IsNotExcludedStandard_FY24 = 1"
    group_by_cols = ["Market", "Browser"]

    sql = build_advanced_titan_query(treatment_date, control_date, time_mode, 
                                     metric_query_map = {"CSDAU": "COUNT(DISTINCT IF(IsCSDAU_FY25 = 1 OR (Product like '%windows%' AND Product <> 'windows'AND EventDate >= toDateTime('2024-09-27') AND EventTimeElapsed>7000 AND EventTimeElapsed <= 1000 * 60 * 3 AND IsCorePV = 1 AND EventName <> 'app_error'AND IsMUIDStable = 1), (UserMUIDHash, EventDate), (NULL,NULL)))",
                                                         "Visitor": "COUNT(DISTINCT IF(IsMUIDStable = 1 OR Canvas in ('Distribution'), (UserMUIDHash, EventDate), (NULL,NULL)))",
                                                         "CSDAU/Visitor": "test"},     
                                     combine_metric_query_map = {}, 
                                     filter_str = "lower(Market) IN ('zh-cn') AND Product IN ('entnews')", group_by_cols = ["Market"])
    print(sql)