# MSNRootCauseAnalyzer

MSNRootCauseAnalyzer is a Python library for performing root cause analysis.

## Installation

```bash
pip install MSNRootCauseAnalyzer
```

## Usage

```python
from root_cause_analyzer.algorithms.adtributor import Adtributor, RecursiveAdtributor

analyzer = Adtributor(top_n_factors=5,
                        max_item_num=3,
                        TEEP=0.05, 
                        TEP=1,
                        min_surprise=5e-04, 
                        need_negative_ep_factor=False,
                        verbose=1)
"""

TEEP: Minimum detectable EP value
TEP: EP cumulative threshold
dimension_cols must be found in data
treatment_col and control_col must be found in data
"""
res = analyzer.analyze(data=df, dimension_cols=["Canvas", "Browser","PageName", "PageVertical"], treatment_col="real", control_col="predict")
print(res)


analyzer = RecursiveAdtributor(top_n_factors=5,
                        max_item_num=3,
                        max_dimension_num=3,
                        max_depth=3,
                        TEEP=0.08, 
                        TEP=1,
                        min_surprise=5e-04, 
                        need_negative_ep_factor=False,
                        need_prune = True,
                        verbose=0)
"""
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
res = analyzer.analyze(data=df, dimension_cols=["Canvas", "Browser", "Product", "PageName", "PageVertical"], treatment_col="real", control_col="predict")
print(res)

``` 