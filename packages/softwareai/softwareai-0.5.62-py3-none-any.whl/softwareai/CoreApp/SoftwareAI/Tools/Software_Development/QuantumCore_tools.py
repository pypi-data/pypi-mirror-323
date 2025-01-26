    # {
    #     "type": "function",
    #     "function": {
    #         "name": "execute_py",
    #         "description": "Execute o código Python de um caminho",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "filepath": {
    #                     "type": "string",
    #                     "description": "caminho do codigo"
    #                 }
    #             },
    #             "required": ["filepath"]
    #         }
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "upload_project_py",
    #         "description": "Realiza o upload do projeto Python.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "repo_name": {
    #                     "type": "string",
    #                     "description": "Nome do repositório a ser criado no GitHub."
    #                 },
    #                 "setup_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo .md (README) a ser carregado no repositório."
    #                 },
    #                 "requirements_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo requirements.txt a ser carregado no repositório."
    #                 },
    #                 "LICENSE_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo LICENSE.txt a ser carregado no repositório."
    #                 },
    #                 "pyproject_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo pyproject.toml a ser carregado no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_init_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do _init_.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_PY_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do main.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_config_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do config.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_utils___init___ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do utils___init___.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_utils_file_utils_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do utils_file_utils.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_modules___init___ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do modules ___init___.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_modules_module1_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do modules_module1.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_modules_module2_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do modules_module2.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_services___init___ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do services_init.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_services_service1_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do services_service1.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_services_service2_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do services_service2.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_tests___init___ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do tests init.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_tests_test_module1_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do test_module1.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_tests_test_module2_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do test_module2.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_tests_test_service1_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do test_service1.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_tests_test_service2_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do test_service2.py a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_Example_ENV": {
    #                     "type": "string",
    #                     "description": "Caminho do Example.py a serem carregados no repositório."
    #                 },
    #                 "PATH_Changelog": {
    #                     "type": "string",
    #                     "description": "Caminho do Changelog a serem carregados no repositório."
    #                 },
    #                 "PATH_SOFTWARE_DEVELOPMENT_SendToPip": {
    #                     "type": "string",
    #                     "description": "Caminho do SendToPip.py a serem carregados no repositório."
    #                 },
                    
    #                 "token": {
    #                     "type": "string",
    #                     "description": "Token de autenticação do GitHub para realizar operações na API."
    #                 }
    #             },
    #             "required": ["repo_name",
    #                         "setup_file_path",
    #                         "requirements_file_path", 
    #                         "LICENSE_file_path",
    #                         "pyproject_file_path",
    #                         "PATH_SOFTWARE_DEVELOPMENT_init_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_PY_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_config_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_utils___init___ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_utils_file_utils_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_modules___init___ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_modules_module1_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_modules_module2_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_services___init___ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_services_service1_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_services_service2_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_tests___init___ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_tests_test_module1_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_tests_test_module2_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_tests_test_service1_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_tests_test_service2_ENV", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_Example_ENV", 
    #                         "PATH_Changelog", 
    #                         "PATH_SOFTWARE_DEVELOPMENT_SendToPip",
    #                         "token"]
    #         }
    #     }
    # },
    
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "add_projectmap_to_github",
    #         "description": "Realiza o upload dos arquivos do projeto, incluindo documentação, timeline, roadmap e análises.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "repo_name": {
    #                     "type": "string",
    #                     "description": "Nome do repositório no GitHub."
    #                 },
    #                 "timeline_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo de timeline do projeto."
    #                 },
    #                 "spreadsheet_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho da planilha do projeto."
    #                 },
    #                 "pre_project_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo de pré-projeto."
    #                 },
    #                 "Roadmap_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo de Roadmap do projeto."
    #                 },
    #                 "analise_file_path": {
    #                     "type": "string",
    #                     "description": "Caminho do arquivo de análise do projeto."
    #                 },
    #                 "token": {
    #                     "type": "string",
    #                     "description": "Token de autenticação do GitHub para realizar operações na API."
    #                 }
    #             },
    #             "required": [
    #                 "repo_name",
    #                 "timeline_file_path",
    #                 "spreadsheet_file_path",
    #                 "pre_project_file_path",
    #                 "Roadmap_file_path",
    #                 "analise_file_path",
    #                 "token"
    #             ]
    #         }
    #     }
    # }
    
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "autosave",
    #         "description": "Salva um codigo python em um caminho",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "code": {
    #                     "type": "string",
    #                     "description": "codigo"
    #                 },
    #                 "path": {
    #                     "type": "string",
    #                     "description": "Caminho do codigo"
    #                 }
    #             },
    #             "required": ["code","path"]
    #         }
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "autoupload",
    #         "description": "Realiza o upload ou update de um arquivo",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "softwarepypath": {
    #                     "type": "string",
    #                     "description": "caminho do arquivo"
    #                 },
    #                 "repo_name": {
    #                     "type": "string",
    #                     "description": "Nome do repositorio "
    #                 },
    #                 "token": {
    #                     "type": "string",
    #                     "description": "Token do github de que realiza o upload ou update"
    #                 }
    #             },
    #             "required": ["softwarepypath","repo_name","token"]
    #         }
    #     }
    # },
        
tools_QuantumCore = [
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            "name": "autopullrequest",
            "description": "cria um pull request no repositório GitHub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_owner": {
                        "type": "string",
                        "description": "Nome do dono do repositório no GitHub."
                    },
                    "repo_name": {
                        "type": "string",
                        "description": "Nome do repositório no GitHub."
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Nome da branch onde o código será atualizado."
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Caminho do arquivo no repositório."
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "Mensagem de commit descrevendo as melhorias."
                    },
                    "improvements": {
                        "type": "string",
                        "description": "Novo código melhorado."
                    },
                    "pr_title": {
                        "type": "string",
                        "description": "Titulo do Pull request."
                    },
                    "token": {
                        "type": "string",
                        "description": "Token de autenticação do GitHub."
                    }
                },
                "required": ["repo_owner", "repo_name", "branch_name", "file_path", "commit_message", "improvements", "pr_title",  "token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_repo_structure",
            "description": "Obtem o a estrutura do repositório GitHub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Nome do repositório no GitHub."
                    },
                    "repo_owner": {
                        "type": "string",
                        "description": "Nome do dono do repositório no GitHub."
                    },
                    "github_token": {
                        "type": "string",
                        "description": "Token de autenticacao "
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Nome da branch principal geralmente main."
                    }
                },
                "required": ["repo_name", "repo_owner", "github_token", "branch_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "autogetfilecontent",
            "description": "Obtem o conteudo do arquivo em um repositório GitHub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Nome do repositório no GitHub."
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Caminho relativo junto ao arquivo"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Nome da branch principal geralmente main."
                    },
                    "companyname": {
                        "type": "string",
                        "description": "Nome da organizacao/compania"
                    },
                    "github_token": {
                        "type": "string",
                        "description": "Token de autenticacao "
                    }
                },
                "required": ["repo_name", "file_path", "branch_name", "companyname", "github_token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "autocheckcommentspr",
            "description": "Verifica Comentarios humanos no pull request",
            "parameters": {
                "type": "object",
                "properties": {
                    "OWNER": {
                        "type": "string",
                        "description": "Nome do dono repositório no GitHub."
                    },
                    "REPO": {
                        "type": "string",
                        "description": "Nome do repositorio no GitHub."
                    },
                    "PR_NUMBER": {
                        "type": "string",
                        "description": "Numero do pull request "
                    },
                    "github_token": {
                        "type": "string",
                        "description": "Token de autenticacao"
                    }
                },
                "required": ["OWNER", "REPO", "PR_NUMBER", "github_token"]
            }
        }
    }



]