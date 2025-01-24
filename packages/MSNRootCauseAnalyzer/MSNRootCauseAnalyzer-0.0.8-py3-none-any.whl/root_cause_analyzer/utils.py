import inspect
import math
import numpy as np
import pycountry
import scipy.stats as stats

from enum import Enum
from rich.console import Console
from rich.table import Table
from rich import box

class MathOperations(Enum):
    ADDITION = "+"
    MULTIPLICATION = "*"
    DIVISION = "/"

def get_enum_member(enum_class, value):
    for member in enum_class:
        if member.value == value:
            return member
    return None

def safe_div(a, b):
    if a == 0 and b == 0:
        return 0
    if b == 0:
        return 1
    return a / b


def get_pvalue( mean1, mean2, std1, std2, n1, n2):
    """z-test"""
    se = np.sqrt((std1/np.sqrt(n1))**2 + (std2/np.sqrt(n2))**2)
    z = (mean1 - mean2) / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return p


def get_current_line():
    return inspect.currentframe().f_back.f_lineno


def get_current_function():
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_name = caller_frame.f_code.co_name
    return caller_name


def print_verbose_info(message, verbose=1, level=1):
    if verbose >= level:
        print(message)
    

# Function to extract country code from market name
def get_country_code_with_pycountry(market_name):
    try:
        language, territory = market_name.split('-')
        country = pycountry.countries.get(alpha_2=territory.upper())
        return country.alpha_2 if country else None
    except Exception as e:
        print(f"Error processing market name '{market_name}': {e}")
        return None


def print_df_as_table(df, title, console_width=None, column_widths={}, column_styles={}):

    console = Console() if console_width is None else Console(width = console_width)
    # show_lines=True: add all borders
    table = Table(title=title, title_style="bold", box=box.HEAVY_HEAD, show_lines=True, expand=True)
    for col in df.columns:
        table.add_column(col, justify="left", overflow = 'fold', no_wrap=False, 
                         width=column_widths.get(col, None), 
                         style=column_styles.get(col, ""))
            
    for _, row in df.iterrows():
        table.add_row(*map(str, row))

    console.print(table)