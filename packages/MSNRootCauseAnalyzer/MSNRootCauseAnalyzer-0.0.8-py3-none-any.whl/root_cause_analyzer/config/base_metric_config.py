import warnings
from abc import ABC, abstractmethod
from numbers import Integral, Real

import numpy as np
import scipy.sparse as sp

class BaseMetricNode:
    """
    base class for metric config tree
    """
    def __init__(self):
        self.metric_name = ""
        self.value = None
        self.formula = []
        self.op_type = None
        self.coefficient = []  # the length should be the same as the formula