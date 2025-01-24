############# Update Software Repo trontechnicalanalysistool Everyday ############################

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

def Update(SoftwareRepoUrl, numberUpdate=5, timebetweenupdate=300, lang="pt"):
    for i in range(numberUpdate):
        byte_manager = AgentInitializer.get_agent('ByteManager') 
        if lang == "pt":
            mensagem = f"solicito uma atualização do repositorio {SoftwareRepoUrl}"
        elif lang == "en":
            mensagem = f"request a repository update {SoftwareRepoUrl}"
        owner_response = byte_manager.AI_1_ByteManager_Company_Owners(mensagem, appfb)
        print(owner_response)
        time.sleep(timebetweenupdate)

schedule.every().day.at("14:23").do(lambda: Update("https://github.com/SoftwareAI-Company/NordVpnAutoRotate", 4))
while True:
    schedule.run_pending()
    time.sleep(1)