# base 

import numpy as np
import pandas as pd

class BaseImpactAnalyzer:
    """
    base class for impact analyzer
    """
    def __init__(self, metric, 
                 treatment_date = None, 
                 control_date = None, 
                 time_mode = "Day",
                 verbose=0):

        self.metric = metric
        self.treatment_date = treatment_date
        self.control_date = control_date
        self.time_mode = time_mode
        self.verbose = verbose

        self.result_dict = {
            "mid_result": pd.DataFrame(),  # save the mid result
            "report": pd.DataFrame()  # save the final result
        }