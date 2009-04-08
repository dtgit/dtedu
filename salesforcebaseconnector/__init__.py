import sys
from Products.CMFCore import utils as cmf_utils

this_module = sys.modules[ __name__ ]
 
product_globals = globals()
 
import salesforcebaseconnector
tools = ( salesforcebaseconnector.SalesforceBaseConnector,
          )

def initialize(context):
    cmf_utils.ToolInit('Salesforce Base Connector',
                    tools = tools,
                    icon='www/salesforce.png'
                    ).initialize( context )
