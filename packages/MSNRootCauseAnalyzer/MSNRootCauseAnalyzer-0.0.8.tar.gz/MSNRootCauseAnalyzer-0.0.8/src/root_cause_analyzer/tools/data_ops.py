# data_ops.py
# Description: This module contains functions for data operations.

import json
import pandas as pd

from ..config.msn_metrics import MSNMetricTreeNode
from ..utils import MathOperations

def merge_treatment_control(df, metric):
    if df.empty or not {"Treatment", "Control"}.issubset(df["Group"].unique()):
        raise ValueError("Data is incomplete or missing required groups.")
    
    df = df.copy()
    df_treatment = df[df["Group"] == "Treatment"]
    df_control = df[df["Group"] == "Control"]
    merged_df = pd.merge(df_control, df_treatment, how="outer", suffixes=("_control", "_treatment"))
    
    # Add additional calculated columns
    merged_df[f"{metric}_Delta"] = merged_df[f"{metric}_treatment"] - merged_df[f"{metric}_control"]
    return merged_df


def cast_metric_dtype(df, metric_set):
    for col in df.columns:
        if col in metric_set:
            df[col] = df[col].astype(float)
        else:
            df[col] = df[col].astype(str)


def parse_formula(m_config: MSNMetricTreeNode) -> str:
    """
    parse formula to string
    e.g. mCFV = mCFV/CPV * CPV/UU * UU
    """
    formula = ""
    if m_config.formula is None or len(m_config.formula) <= 0 or len(m_config.formula) != len(m_config.coefficient):
        return formula
    mc = m_config.coefficient
    if m_config.op_type == MathOperations.ADDITION:    
        formula = " + ".join([f"{mc[i]}*{m_config.formula[i]}" for i in range(len(m_config.formula))])
    elif m_config.op_type == MathOperations.MULTIPLICATION:
        formula = " * ".join([f"({mc[i]}*{m_config.formula[i]})" for i in range(len(m_config.formula))])
    elif m_config.op_type == MathOperations.DIVISION:
        formula = " / ".join([f"({mc[i]}*{m_config.formula[i]})" for i in range(len(m_config.formula))])
    # remove "1*" in formula
    formula = formula.replace("1*", "")
    return formula


def parse_contribution_to_json(m_config: MSNMetricTreeNode, record: pd.Series) -> str:
    """
    cast to json, {factor1: contribution1, factor2: contribution2}
    """
    if m_config.formula is None or len(m_config.formula) <= 0 or len(m_config.formula) != len(m_config.coefficient):
        return ""        
    factors = m_config.formula
    data = {}
    for factor in factors:
        if f"{factor}_Contribution%" not in record.index:
            print(f"Error: {factor}_Contribution% not in record.{record.index}")
        contrib = record[f"{factor}_Contribution%"] if f"{factor}_Contribution%" in record else 0
        data[factor] = f"{contrib:.2%}"
    return json.dumps(data)  