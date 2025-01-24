
tools_GearAssist = [
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            "name": "AutoGetLoggerUser",
            "description": "Realiza o rastreamento de problemas tecnicos no software do usuario usando so Ticket id, Retornando um dicionario json com o processo do usuario em um range de 1 dia antes da abertura do ticket ",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticketid": {
                        "type": "string",
                        "description": "Ticket id"
                    }
                },
                "required": ["ticketid"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "autosave",
            "description": "Salva um codigo python em um caminho",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "codigo"
                    },
                    "path": {
                        "type": "string",
                        "description": "Caminho do codigo"
                    }
                },
                "required": ["code","path"]
            }
        }
    }

    
]

