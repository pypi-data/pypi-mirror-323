# IMPORT SoftwareAI Core
from softwareai.CoreApp._init_core_ import * 
#########################################
from softwareai.CoreApp.Agents.Software_Technical_Support.GearAssist import GearAssist



Ticketid = "4a48e"
name_app = "appx"
appfb = FirebaseKeysinit._init_app_(name_app)
name_app = "nordautorotate"
app_product = FirebaseKeysinit._init_app_(name_app)
GearAssistClass = GearAssist()
GearAssistClass.GearAssist_Technical_Support(Ticketid, appfb, app_product)


