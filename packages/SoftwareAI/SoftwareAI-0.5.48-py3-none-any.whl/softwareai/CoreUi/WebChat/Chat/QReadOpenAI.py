
import sys
import os


import struct
import re
import platform
import json
import ast
from firebase_admin import credentials, initialize_app, storage, db, delete_app
from datetime import datetime




from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


from typing import Optional, List, Union
from typing_extensions import override
class QReadOpenAi(QThread):
    def __init__(self, agent, appx, client):
        super().__init__()
        self.agent = agent
        self.appx = appx
        self.client = client
        self.result = None  # Armazenará o resultado final da execução

    def run(self):
        try:
            agent = self.agent
            appx = self.appx
            client = self.client

            # Buscar o assistant_id no Firebase
            refai_org_assistant_id = db.reference(f'ai_org_assistant_id/User_{agent}', app=appx)
            dataai_org_assistant_id = refai_org_assistant_id.get()
            if not dataai_org_assistant_id or 'assistant_id' not in dataai_org_assistant_id:
                raise ValueError("assistant_id não encontrado no Firebase.")
            assistant_id = str(dataai_org_assistant_id['assistant_id'])

            # Buscar o thread_id no Firebase
            refai_org_thread_Id = db.reference(f'ai_org_thread_Id/User_{agent}', app=appx)
            datarefai_org_thread_Id = refai_org_thread_Id.get()
            if not datarefai_org_thread_Id or 'thread_id' not in datarefai_org_thread_Id:
                raise ValueError("thread_id não encontrado no Firebase.")
            thread_id = datarefai_org_thread_Id['thread_id']

            # Obter o status da thread e carregar os dados
            run_status = client.beta.threads.runs.list(thread_id=thread_id)
            if not run_status:
                raise ValueError("Nenhum dado encontrado para a thread no cliente.")

            jsonmodel = run_status.model_dump_json()
            with open("Cache/model_dump_json.json", 'w', encoding='utf-8') as file:
                file.write(jsonmodel)

            with open("Cache/model_dump_json.json", "r", encoding='utf-8') as file:
                data = json.load(file)

            if 'data' not in data:
                raise ValueError("Formato inválido nos dados da thread.")

            total_tokens_list = []
            prompt_tokens_list = []
            completion_tokens_list = []
            for run in data['data']:
                total_tokens = run['usage']['total_tokens']
                total_tokens_list.append(total_tokens)
                prompt_tokens = run['usage']['prompt_tokens']
                completion_tokens = run['usage']['completion_tokens']

            total_tokens = sum(total_tokens_list)

            # Buscar mensagens associadas aos IDs
            contador_1 = 0
            messagesx = []
            ids = [item['id'] for item in data['data']]
            print(ids)
            for id in ids:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=id
                )

                messages = client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                for message in messages:
                    for mensagem_contexto in message.content:
                        valor_texto = mensagem_contexto.text.value
                        print(valor_texto)
                        messagesx.append(valor_texto)

            self.result = {
                "thread_id": thread_id,
                "total_tokens": total_tokens,
                "messages": messagesx,  # Retorna os primeiros 5 exemplos de mensagens
            }
        except Exception as e:
            self.result = {"error": str(e)}
