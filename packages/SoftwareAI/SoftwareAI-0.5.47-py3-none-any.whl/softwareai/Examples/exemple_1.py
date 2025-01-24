#########################################
# IMPORT SoftwareAI Agents
from softwareai.CoreApp._init_agents_ import AgentInitializer
#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################
# IMPORT SoftwareAI Core
from softwareai.CoreApp._init_core_ import * 
#########################################

name_app = "appx"
appfb = FirebaseKeysinit._init_app_(name_app)

byte_manager = AgentInitializer.get_agent('ByteManager') 
mensagem = "solicito um script para Análise técnica da criptomoeda dogecoin"
owner_response = byte_manager.AI_1_ByteManager_Company_Owners(mensagem, appfb)
print(owner_response)
