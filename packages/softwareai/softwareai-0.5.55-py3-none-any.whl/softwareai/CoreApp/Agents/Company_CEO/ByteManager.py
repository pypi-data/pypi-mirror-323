

#########################################
# IMPORT SoftwareAI Core
from softwareai.CoreApp._init_core_ import * 
#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################
# IMPORT SoftwareAI All Paths 
from softwareai.CoreApp._init_paths_ import *
#########################################
# IMPORT SoftwareAI Instructions
from softwareai.CoreApp._init_Instructions_ import *
#########################################
# IMPORT SoftwareAI Tools
from softwareai.CoreApp._init_tools_ import *
#########################################
# IMPORT SoftwareAI keys
from softwareai.CoreApp._init_keys_ import *
#########################################
# IMPORT SoftwareAI _init_environment_
from softwareai.CoreApp._init_environment_ import init_env


class ByteManager:
    def __init__(self, 
                Company_Managers,
                Pre_Project_Document,
                Gerente_de_projeto,
                Equipe_De_Solucoes,
                Softwareanaysis,
                SoftwareDevelopment,
                Software_Documentation
                ):
        
        self.Company_Managers = Company_Managers
        self.Pre_Project_Document = Pre_Project_Document
        self.Gerente_de_projeto = Gerente_de_projeto
        self.Equipe_De_Solucoes = Equipe_De_Solucoes
        self.Softwareanaysis = Softwareanaysis
        self.SoftwareDevelopment = SoftwareDevelopment
        self.Software_Documentation = Software_Documentation




    
    def AI_1_ByteManager_Company_Owners(self, 
                                        mensagem,
                                        appfb,
                                        vectorstore_in_assistant = None,
                                        vectorstore_in_Thread = None,
                                        Upload_1_file_in_thread = None,
                                        Upload_1_file_in_message = None,
                                        Upload_1_image_for_vision_in_thread = None,
                                        Upload_list_for_code_interpreter_in_thread = None
                                        
                                        ):

        key = "AI_ByteManager_Company_CEO"
        nameassistant = "AI ByteManager CEO da Empresa SoftwareAI Company"
        model_select = "gpt-4o-mini-2024-07-18"

        key_openai = OpenAIKeysteste.keys()
        client = OpenAIKeysinit._init_client_(key_openai)

        github_username, github_token = GithubKeys.ByteManagerCompanyOwner_github_keys()

        AI_ByteManager, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(appfb, client, key, instructionByteManager, nameassistant, model_select, tools_ByteManager, vectorstore_in_assistant)

        mensaxgem = """decida oque o usuario esta solicitando com base na mensagem  
        Regra 1 - Caso seja solicitado alguma atualização de repositorio use a function (autoupdaterepo)
        Regra 2 - Caso seja solicitado alguma criação de repositorio use a function (create_repo) 
        """  
        mensaxgemfinal = mensaxgem + f"mensagem:\n{mensagem}"
        
        response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensaxgemfinal,
                                                                agent_id=AI_ByteManager, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_ByteManager,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_ByteManager
                                                                )
                                                
                
        print(response)
        try:
            teste_dict = json.loads(response)
        except:
            teste_dict = response


        if 'resposta' in teste_dict:
            resposta_AI_ByteManager = teste_dict['resposta']
            return resposta_AI_ByteManager
        

        # CloudArchitectUpdateReadme = self.Software_Documentation.CloudArchitectUpdateReadme(
        #     appfb, client, repo_name, Melhorias
        # )

        if 'solicitadoalgumcodigo' in teste_dict:


            mensaxgem = f"crie uma descricao completa de {mensagem}  "
            format = 'Responda no formato JSON Exemplo: {"descricao": "..."}'
            
            mensagemz = mensaxgem + format

            AI_ByteManager_response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensagemz,
                                                                agent_id=AI_ByteManager, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_ByteManager,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_ByteManager
                                                                )
                                                
            

            try:
                teste_dict = json.loads(AI_ByteManager_response)
                pergunta_ao_tigrao = teste_dict['solicitadoalgumcodigo']    
            except Exception as e2:
                pergunta_ao_tigrao = AI_ByteManager_response
                              

            mensaxgem = f"""crie um nome do repositorio desse software no github com base na descricao:\n
            {pergunta_ao_tigrao}
            """
            format = 'Responda no formato JSON Exemplo: {"nome": "nome..."}'
            mensagem = mensaxgem + format
            response = ResponseAgent.ResponseAgent_message_completions(mensagem, key_openai, "", True, True)
            try:
                repo_name = response["nome"]
                print(repo_name)
                repo_name_str = f"{repo_name}"
                repo_name_replace = repo_name_str.replace("-", "").replace("A-I-O-R-G-", "").replace("A-I-O-R-G", "").replace("A-I-O-R-G/", "")
                print(repo_name_replace)
                repo_name = repo_name_replace
            except Exception as errror2:
                print(errror2)
                print(response)
            
            ##Agent Destilation##                   
            Agent_destilation.DestilationResponseAgent(mensagem, response, instructionsassistant, nameassistant)
            
            mensaxgem = f"""crie uma descricao de 250 caracteres para o repositorio no github com base na descricao:\n
            {pergunta_ao_tigrao}
            """
            format = 'Responda no formato JSON Exemplo: {"descricao": "descricao..."}'
            mensagem = mensaxgem + format
            response = ResponseAgent.ResponseAgent_message_completions(mensagem, key_openai, "regra descricao não execeder 250 caracteres", True, True)
            repo_description = response["descricao"]

            ##Agent Destilation##                   
            Agent_destilation.DestilationResponseAgent(mensagem, response, instructionsassistant, nameassistant)

                                                
            mensaxgemrepositorio = f"Realize a criacao do repositorio no github usando (create_repo)\n repo_name:\n {repo_name}\ndescription:\n {repo_description}\n token:\n {github_token}\n"
            response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensaxgemrepositorio,
                                                                agent_id=AI_ByteManager, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_ByteManager,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_ByteManager
                                                                )

            ##Agent Destilation##                   
            Agent_destilation.DestilationResponseAgent(mensaxgemrepositorio, response, instructionsassistant, nameassistant)
            
            init_env(repo_name)

            resposta_do_tigrao_com_doc_pre_projeto = self.Pre_Project_Document.AI_1_Pre_Project_Document_Writer(appfb, client, pergunta_ao_tigrao, repo_name)#invoke_tigrao(pergunta_ao_tigrao)

            print(resposta_do_tigrao_com_doc_pre_projeto)

            Uploadfile = resposta_do_tigrao_com_doc_pre_projeto

            path_planilha_Projeto, path_nome_do_cronograma, path_name_doc_Pre_Projeto = self.Gerente_de_projeto.Bob_Gerente_de_projeto(appfb, client, Uploadfile, repo_name)
            
            path_Roadmap, cronograma_do_projeto, planilha, doc_Pre_Projeto = self.Equipe_De_Solucoes.Dallas_Equipe_De_Solucoes_Roadmap(appfb, client, path_nome_do_cronograma, path_planilha_Projeto, path_name_doc_Pre_Projeto, repo_name)
            
            # file_paths_to_project = [f"{path_Roadmap}", f"{cronograma_do_projeto}", f"{planilha}", f"{doc_Pre_Projeto}"]
            # print(file_paths_to_project)
            # vectorstore_id = Agent_files.auth_or_create_vectorstore("project_", file_paths_to_project)
            # print(vectorstore_id)

            anaysis_in_txt_path = self.Softwareanaysis.AI_SynthOperator(appfb, client, path_Roadmap, cronograma_do_projeto, planilha, doc_Pre_Projeto, repo_name)

            script_version_1_path = self.SoftwareDevelopment.AI_QuantumCore(
                    appfb, client, repo_name,
                    os.getenv("PATH_NOME_DO_CRONOGRAMA_ENV"),
                    os.getenv("PATH_PLANILHA_PROJETO_ENV"),
                    os.getenv("PATH_NAME_DOC_PRE_PROJETO_ENV"),
                    os.getenv("PATH_ROADMAP_ENV"),
                    os.getenv("PATH_ANALISE_ENV"),
                )


            #resposta_AI_ByteManager_dict = json.loads(passando_resposta_do_tigrao_para_AI_ByteManager)
        
            #resposta_AI_ByteManager = resposta_AI_ByteManager_dict['resposta']

            return script_version_1_path
