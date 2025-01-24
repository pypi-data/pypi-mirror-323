# constants.py
# -*- coding: utf-8 -*-
"""
This file defines common constants, such as:
1. Default Dimensions for Attribution Analysis
"""

# Default Dimensions for Attribution Analysis
DEFAULT_DIMENSIONS_MAP = {
    "User": ["IsMUIDStable",
             "CASE WHEN MUIDAge >=180 THEN '180+' WHEN MUIDAge >= 90 THEN '90-180' WHEN MUIDAge >= 30 THEN '30-90' ELSE '<30' END AS MUIDAgeBucket",
             "IF(LoginState IN ('MSA', 'AAD', 'AAD-AL'), LoginState, 'Non Signed') AS LoginState"],   
    "Location": [ "lower(Market)AS Market"],
    "Device": ["Browser"],  # Too much values: UserAgent?  BrowserVersion?  
    "EntryPoint": ["Canvas", "OCIDL2"],
    "Page": ["lower(PageType)AS PageType", "PageName", 
             """CASE WHEN Lower(PageType) IN ('article', 'gallery', 'video', 'watch') THEN 'content'
                WHEN Lower(PageVertical) IN ('homepage', 'sports', 'weather', 'traffic', 'finance', 'shopping', 'casualgames', 'gaming', 'channel') THEN Lower(PageVertical)
                ELSE 'other' END AS PageVertical""",
            "PageDepartment", "PageContentLayout", "ContentModule"],   
    # Too much values: PageDomain? ContentModuleLineage?  "domain(Referrer) AS ReferrerDomain"
}


# TODO: need mannually update the following mapping
# Key words for different query
KNOWLEDGE_MAPPING = {
    'ntp': "Edge/Anaheim(NTP/DHP) - Canvas IN ('Anaheim DHP','Anaheim NTP','EnterpriseNews NTP')",
    'prong2': "Prong2 - Product IN ('windowsdash'); Canvas IN ('WindowsP2Shell','Enterprise WindowsP2Shell')",
    'prong1': "Prong1 - Product IN ('windowsshell'); Canvas IN ('WindowsShell Taskbar','Enterprise WindowsShell Taskbar')",
    'prong12ntplanding': "Canvas IN ('WindowsShell Taskbar', 'WindowsP2Shell', 'Enterprise WindowsP2Shell')  ; PageType IN ('dhp', 'ntp', 'hp')",
    'ntpdhp': "Edge/Anaheim(NTP/DHP) - Canvas IN ('Anaheim DHP','Anaheim NTP','EnterpriseNews NTP')",
    'casualgames': "Vertical Page: PageType IN ('verthp') & PageVertical IN ( 'casualgames')",
    'msnhp': "msn.com - Product IN ('prime'); msn.com - Canvas IN ('Msn HP'); Landing Page/ Homepage - PageType IN ('hp')",
    'msn': "msn.com - Product IN ('prime'); Canvas IN ('Win 10 Prime', 'Downlevel Prime', 'Msn HP')",
    'msn.com': "msn.com - Product IN ('prime'); Canvas IN ('Win 10 Prime', 'Downlevel Prime', 'Msn HP')",
    'anaheim': "Edge/anaheim: Product IN ('anaheim', 'entnews');Edge/Anaheim(NTP/DHP) - Canvas IN ('Anaheim DHP','Anaheim NTP','EnterpriseNews NTP')",
    'edge': "Edge/Anaheim(NTP/DHP) - Canvas IN ('Anaheim DHP','Anaheim NTP','EnterpriseNews NTP')",
    'lockscreen': 'Canvas = Lockscreen',
    'watch': "Content Page/Consumption Page: PageType IN  ('watch', 'video')",
    'winhp': "WindowsAllUp: Canvas IN ('WinMSNews HP', 'WindowsShell Taskbar', 'Enterprise WindowsShell Taskbar', 'WindowsP2Shell', 'Enterprise WindowsP2Shell', 'Lockscreen')",
    'video': "Content Page/Consumption Page: PageType IN  ('watch', 'video')",
    'finance': "Vertical Page: PageType IN ('verthp') & PageVertical IN ('finance', 'money')",
    'weather': "Vertical Page: PageType IN ('verthp') & PageVertical IN ('weather')",
    'sports': "Vertical Page: PageType IN ('verthp') & PageVertical IN ('sports')",
    'consumption': "Content Page/Consumption Page: PageType IN ('article', 'gallery', 'watch', 'video')",
    'consumptionpages': "Content Page/Consumption Page: PageType IN ('article', 'gallery', 'watch', 'video')",
}


EXP_METRIC_NAME_MAP = {
    "CSDAU": "DaysEngaged",
    "mCFV": "MonetizationContentFeedViewsPerUU"
}

# TODO: remove the hardcode 
# set minimum detactable contribution = 1/N * FACTOR, N is the number of sub-metrics
MIN_METRIC_CONTRIBUTION_FACTOR = 1.3

# The threshold for the cosine similarity between experiments name and filter string
EXP_MIN_COSINE_SIMILARITY = 0.2
# The minimum contribution of the related experiment to the metric movement
EXP_MIN_RELATED_EXP_CONTRIBUTION = 0.05
# The minimum contribution of the weakly related but significant experiment to the metric movement
EXP_MIN_SIG_EXP_CONTRIBUTION = 0.001  # TODO: just for testing, need to adjust