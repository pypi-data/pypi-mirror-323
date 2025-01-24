# constants.py
# -*- coding: utf-8 -*-
"""
This module defines common constants, such as:
1. titan query string
2. metric definition
"""

# Titan Query: PageContentLayout Filter String 
CONTENTOFF_LAYOUT_FILTER = " PageContentLayout in ('Custom - Content off', 'Custom - Headings Only', 'Focus', 'Custom - Content visible on scroll') "
FULL_LAYOUT_FILTER = " PageContentLayout in ('Informational', 'Custom - Content visible') "
PEEK_LAYOUT_FILTER = " PageContentLayout in ('Inspirational Peek', 'Custom - Content Feed Peek', 'Inspirational') "


MeaningfulActionCondition = """
IsMUIDStable = 1 
AND EngagementValue = 1 
AND multiSearchAnyCaseInsensitive(ContentModuleLineage, ['topsite', 'headersearch','recentsearch', 'managehistory', 'recommendedsites','coachmark', 'notificationcardreceived', 'notificationcardview'] ) = 0 
AND NOT (Behavior IN ('Close', 'Hide') AND UserAction in ('NonNavClick', 'Close'))
"""

DwellTimeCondition = """ IsMUIDStable = 1 AND 
( 
    ((EventTimeElapsed > 10000 AND Canvas = 'Lockscreen' AND PageType IN ('ntp','dhp'))
    OR ( (Product LIKE '%windows%' AND Product <> 'windows')
            AND (EventTimeElapsed > 10000 OR (EventDate >= toDateTime('2024-09-27') AND EventTimeElapsed>7000)) 
        ) 
    )
    AND EventTimeElapsed <= 1000 * 60 * 3
    AND IsCorePV = 1
    AND EventName <> 'app_error' 
)"""

CPVDAUCondition = """IsMUIDStable = 1 AND 
(UserAction = 'View'
    AND IsCorePV = 1
    AND PageVertical NOT IN('homepage', '')
    AND NOT (PageVertical == 'gaming' AND PageFeedID NOT like'%/manual' AND Product != 'startgg')
    AND PageType NOT IN ('dhp', 'ntp', 'hp') 
)"""

AppDAUByCondition = """IsMUIDStable = 1 AND (UserAction = 'View' AND Canvas LIKE '%App%' )"""

# Metric Definition
TQUERY_DAUBYSCROLL = f"""COUNT(DISTINCT IF({MeaningfulActionCondition} AND Action IN ('Scroll') , (UserMUIDHash, EventDate), (NULL,NULL)))  """
TQUERY_DAUBYONSITENAVCLICKS = f"""COUNT(DISTINCT IF({MeaningfulActionCondition} AND UserAction IN ('OnsiteNavClick') , (UserMUIDHash, EventDate), (NULL,NULL)))  """
TQUERY_DAUBYOFFSITENAVCLICKS = f"""COUNT(DISTINCT IF({MeaningfulActionCondition} AND UserAction IN ('OffsiteNavClick') , (UserMUIDHash, EventDate), (NULL,NULL)))  """
TQUERY_DAUBYDWELLTIME = f"""COUNT(DISTINCT IF({DwellTimeCondition} , (UserMUIDHash, EventDate), (NULL,NULL)))  """
TQUERY_DAUBYCPV = f"""COUNT(DISTINCT IF({CPVDAUCondition} , (UserMUIDHash, EventDate), (NULL,NULL)))  """
TQUERY_DAUBYAPP = f"""COUNT(DISTINCT IF({AppDAUByCondition} , (UserMUIDHash, EventDate), (NULL,NULL)))  """
TQUERY_VISITOR = "COUNT(DISTINCT IF(IsMUIDStable = 1 OR Canvas in ('Distribution'), (UserMUIDHash, EventDate), (NULL,NULL)))"
TQUERY_CSDAU = "COUNT(DISTINCT IF(IsCSDAU_FY25 = 1 OR (Product like '%windows%' AND Product <> 'windows'AND EventDate >= toDateTime('2024-09-27') AND EventTimeElapsed>7000 AND EventTimeElapsed <= 1000 * 60 * 3 AND IsCorePV = 1 AND EventName <> 'app_error'AND IsMUIDStable = 1), (UserMUIDHash, EventDate), (NULL,NULL)))"
TQUERY_VISITOR2DAU = f"""({TQUERY_CSDAU})/({TQUERY_VISITOR})"""