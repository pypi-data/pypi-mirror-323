

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




class Software_Documentation:
    def __init__(self):
        pass

    def CloudArchitect_Software_Documentation_Type_Create(self, appfb, client, path_python_software, path_Analysis, path_Roadmap, path_Spreadsheet, path_Timeline, path_Preproject, repo_name, UseVectorstoreToGenerateFiles = True):

        key = "AI_CloudArchitect_Software_Documentation"
        nameassistant = "AI CloudArchitect Software Documentation"
        model_select = "gpt-4o-mini-2024-07-18"
        
        Upload_1_file_in_thread = None
        Upload_1_file_in_message = None
        Upload_1_image_for_vision_in_thread = None
        Upload_list_for_code_interpreter_in_thread = None
        vectorstore_in_assistant = None
        vectorstore_in_Thread = None



        key_openai = OpenAIKeysteste.keys()
        # name_app = "appx"
        # appfb = FirebaseKeysinit._init_app_(name_app)
        # client = OpenAIKeysinit._init_client_(key_openai)

        github_username, github_token = GithubKeys.CloudArchitect_github_keys()

        AI_CloudArchitect, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(appfb, client, key, instructionCloudArchitect, nameassistant, model_select, tools_CloudArchitect, vectorstore_in_assistant)
        
        if UseVectorstoreToGenerateFiles == True:
            file_paths = [os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", f"environment.txt")), os.getenv("PATH_SOFTWARE_DEVELOPMENT_PY_ENV"), path_python_software, path_Analysis, path_Roadmap, path_Spreadsheet, path_Timeline, path_Preproject]
            AI_CloudArchitect = Agent_files_update.del_all_and_upload_files_in_vectorstore(appfb, client, AI_CloudArchitect, "CloudArchitect_Work_Environment", file_paths)
            mensagem = f"""
            Crie a Documentacao para o github, salve e realize o upload no GitHub (usando autosave e autoupload) Baseie-se no codigo do software e nas documentacoes que estao armazenadas em CloudArchitect_Work_Environment\n
            repo_name: \n
            {repo_name}\n
            token: \n
            {github_token}\n
             
            """


        adxitional_instructions_CloudArchitect = f"""
        estrutura do projeto esta armazenada em environment.txt
        """

        rregras = "Regras: NÃO use a function update_readme_to_github"
        mensagem_final = mensagem + rregras
        response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensagem_final,
                                                                agent_id=AI_CloudArchitect, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_CloudArchitect,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_CloudArchitect
                                                                )

        path_Documentacao = os.getenv("PATH_DOCUMENTACAO_ENV")
        print(response)

        ##Agent Destilation##                   
        Agent_destilation.DestilationResponseAgent(mensagem_final, response, instructionsassistant, nameassistant)
        
        # mensaxgem = f"""deixe essa documentacao do github asseguir no formato markdown: \n {response}"""
        # format = 'Responda no formato JSON Exemplo: {"documentacao": "documentacao..."}'
        # mensagem = mensaxgem + format
        # response = ResponseAgent.ResponseAgent_message_completions(mensagem, key_openai, "", True, True)
        # documentacao_corrigida = response["documentacao"]
        # print(documentacao_corrigida)
        # python_functions.save_TXT(documentacao_corrigida, path_Documentacao, "w")

        # ##Agent Destilation##                   
        # Agent_destilation.DestilationResponseAgent(mensagem, response, instructionsassistant, nameassistant)
        
        self.diretorio_script = os.path.dirname(os.path.abspath(__file__))
        self.path_DocGitHubDataREADME = os.path.join(self.diretorio_script, '../../../', 'CoreCompany',  'KnowLedgeData', 'GitHubData', 'DocMd', f"README{random.randint(30, 900)}.md")
        self.path_DocGitHubData = os.path.join(self.diretorio_script, '../../../', 'CoreCompany', 'KnowLedgeData', 'GitHubData', 'DocMd')
        self.path_DocGitHubData_log = os.path.join(self.diretorio_script, '../../../', 'CoreCompany',  'KnowLedgeData', 'GitHubData', 'DocMd' , 'docs_uploaded.log')

        # python_functions.save_TXT(documentacao_corrigida, self.path_DocGitHubDataREADME, "w")

        # self.check_and_upload_docs(appfb, client)

        return path_Documentacao



    def CloudArchitect_Software_Documentation_Type_Update(self, appfb, client, repo_name, path_readme, code_python_software_old, code_path_python_software_new):

        
        Readme = python_functions.analyze_txt(path_readme)

        repo_name = f"A-I-O-R-G/{repo_name}" 
        branch_name = "main"  # Substitua pelo branch correto, se necessário

        Readme = self.get_file_content(repo_name, f"pyproject.toml", branch_name)

        python_functions.save_TXT(Readme, os.getenv("PATH_ANALISE_ENV"), 'w')


        # python_software_old = python_functions.analyze_txt(code_python_software_old)

        # python_software_new = python_functions.analyze_txt(code_path_python_software_new)

        # Analysis = python_functions.analyze_txt(path_Analysis)

        # Roadmap = python_functions.analyze_txt(path_Roadmap)

        # Spreadsheet = python_functions.analyze_txt(path_Spreadsheet)

        # Timeline = python_functions.analyze_txt(path_Timeline)

        # Preproject = python_functions.analyze_txt(path_Preproject)

        key = "AI_CloudArchitect_Software_Documentation"
        nameassistant = "AI CloudArchitect Software Documentation"
        model_select = "gpt-4o-mini-2024-07-18"
        
        Upload_1_file_in_thread = None
        Upload_1_file_in_message = None
        Upload_1_image_for_vision_in_thread = None
        Upload_list_for_code_interpreter_in_thread = None
        vectorstore_in_assistant = None
        vectorstore_in_Thread = None



        key_openai = OpenAIKeysteste.keys()
        # name_app = "appx"
        # appfb = FirebaseKeysinit._init_app_(name_app)
        # client = OpenAIKeysinit._init_client_(key_openai)


        AI_CloudArchitect, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(appfb, client, key, instructionCloudArchitect, nameassistant, model_select, tools_CloudArchitect, vectorstore_in_assistant)

        # vector_store_id = Agent_files.auth_or_create_vectorstore("DocGitHubData")
        #AI_CloudArchitect = Agent_files_update.update_vectorstore_in_agent(AI_CloudArchitect, [vector_store_id])
        
        mensagem = f"""
        Atualize a Documentacao atual do github desse software com base nas melhorias feitas \n
        Repo Name:\n
        {repo_name}\n
        Documentacao atual do github:\n
        {Readme}\n
        codigo python do software antigo :\n
        {code_python_software_old}
        codigo python do software novo :\n
        {code_path_python_software_new}\n

        """
        # Documentacao Analysis:\n
        # {Analysis}\n
        # Documentacao Roadmap:\n
        # {Roadmap}\n
        # Documentacao Spreadsheet:\n
        # {Spreadsheet}\n
        # Documentacao Timeline:\n
        # {Timeline}\n
        # Documentacao Preproject:\n
        # {Preproject}\n
        response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensagem,
                                                                agent_id=AI_CloudArchitect, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_CloudArchitect,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_CloudArchitect
                                                                )

        ##Agent Destilation##                   
        Agent_destilation.DestilationResponseAgent(mensagem, response, instructionsassistant, nameassistant)
        
        path_Documentacao = os.getenv("PATH_DOCUMENTACAO_ENV")
        print(response)
        

        mensaxgem = f"""deixe essa documentacao do github asseguir aprensentavel ao publico: \n {response}"""
        
        # referencias = """remova as referencias a criacao da documentacao por exemplo:\n
        #     ```json
        #         {
        #             "status_da_documentacao": "Documentação criada com sucesso.",
        #             "secoes_documentadas": [
        #                 "Introdução",
        #                 "Funcionalidade",
        #                 "Instalação",
        #                 "Uso",
        #                 "Referência de API",
        #                 "Contribuição",
        #                 "Licença"
        #             ],
        #             "observacoes": "A documentação deve ser mantida atualizada conforme novas funcionalidades "
        #         }
        #     ```
        # """

        format = 'Responda no formato JSON Exemplo: {"documentacao_corrigida": "documentacao corrigida..."}'
        mensagem = mensaxgem + format
        response = ResponseAgent.ResponseAgent_message_completions(mensagem, key_openai, "", True, True)
        documentacao_corrigida = response["documentacao_corrigida"]
        print(documentacao_corrigida)
        python_functions.save_TXT(documentacao_corrigida, path_Documentacao, "w")

        ##Agent Destilation##                   
        Agent_destilation.DestilationResponseAgent(mensagem, response, instructionsassistant, nameassistant)
        
        self.diretorio_script = os.path.dirname(os.path.abspath(__file__))
        self.path_DocGitHubDataREADME = os.path.join(self.diretorio_script, '../../../', 'CoreCompany',  'KnowLedgeData', 'GitHubData', 'DocMd', f"README{random.randint(30, 900)}.md")
        self.path_DocGitHubData = os.path.join(self.diretorio_script, '../../../', 'CoreCompany', 'KnowLedgeData', 'GitHubData', 'DocMd')
        self.path_DocGitHubData_log = os.path.join(self.diretorio_script, '../../../', 'CoreCompany',  'KnowLedgeData', 'GitHubData', 'DocMd' , 'docs_uploaded.log')

        python_functions.save_TXT(documentacao_corrigida, self.path_DocGitHubDataREADME, "w")

        github_username, github_token = GithubKeys.CloudArchitect_github_keys()

        mensagem = f"""
        Atualiza o Readme do repositorio no github\n
        file_path_readme_improvements:\n
        {path_readme}\n
        repo_name:\n
        {repo_name}\n
        token:\n
        {github_token}\n

        """

        
        response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensagem,
                                                                agent_id=AI_CloudArchitect, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_CloudArchitect,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_CloudArchitect
                                                                )
        path_Documentacao = os.getenv("PATH_DOCUMENTACAO_ENV")
        print(response)
                                            
        ##Agent Destilation##                   
        Agent_destilation.DestilationResponseAgent(mensaxgem, response, instructionsassistant, nameassistant)
        
        # self.check_and_upload_docs(appfb, client)

        return path_Documentacao




    def CloudArchitectUpdateReadme(self, appfb, client, repo_name, Melhorias,
                                    companyname = "SoftwareAI-Company"
                                   ):

        branch_name = "main"
        Readme = self.get_file_content(repo_name, f"README.md", branch_name)

        python_functions.save_TXT(Readme, os.getenv("PATH_DOCUMENTACAO_ENV"), 'w')

        key = "AI_CloudArchitect_Software_Documentation"
        nameassistant = "AI CloudArchitect Software Documentation"
        model_select = "gpt-4o-mini-2024-07-18"
        self.companyname = companyname
        Upload_1_file_in_thread = None
        Upload_1_file_in_message = None
        Upload_1_image_for_vision_in_thread = None
        Upload_list_for_code_interpreter_in_thread = None
        vectorstore_in_assistant = None
        vectorstore_in_Thread = None


        github_username, github_token = GithubKeys.CloudArchitect_github_keys()
        key_openai = OpenAIKeysteste.keys()

        AI_CloudArchitect, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(appfb, client, key, instructionCloudArchitect, nameassistant, model_select, tools_CloudArchitect, vectorstore_in_assistant)

        mensagem = f"""
        Atualize a Documentacao atual com base nas melhorias feitas, salve e realize o upload no GitHub (usando autosave e autoupload) \n
        Repo Name:\n
        {repo_name}\n
        token:\n
        {github_token}\n
        Melhorias:\n
        {Melhorias}
    

        """

        adxitional_instructions_CloudArchitect = f"""
        estrutura do projeto esta armazenada em environment.txt
        
        """
        response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=mensagem,
                                                                agent_id=AI_CloudArchitect, 
                                                                key=key,
                                                                app1=appfb,
                                                                client=client,
                                                                tools=tools_CloudArchitect,
                                                                model_select=model_select,
                                                                aditional_instructions=adxitional_instructions_CloudArchitect
                                                                )





    def get_file_content(self, repo_name, file_path, branch_name):

        github_username, github_token = GithubKeys.CloudArchitect_github_keys()

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
  

        file_url = f"https://api.github.com/repos/{self.companyname}/{repo_name}/contents/{file_path}?ref={branch_name}"
        response = requests.get(file_url, headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            import base64
            content = base64.b64decode(file_data['content']).decode('utf-8')
            return content
        else:
            print(f"Erro ao acessar {file_path}. Status: {response.status_code}  {response.content}")
            return None
        



    def read_uploaded_files(self):
        """Lê o arquivo de log e retorna um conjunto de arquivos já carregados"""
        if os.path.exists(self.path_DocGitHubData_log):
            with open(self.path_DocGitHubData_log, "r") as log:
                uploaded_files = {line.strip() for line in log.readlines()}
        else:
            uploaded_files = set()
        return uploaded_files

    def log_uploaded_file(self, file_name):
        """Registra um arquivo como carregado no arquivo de log"""
        with open(self.path_DocGitHubData_log, "a") as log:
            log.write(f"{file_name}\n")

    def check_and_upload_docs(self, app1, client,  name="DocGitHubData"):
        """Verifica novos arquivos .md e realiza o upload, registrando-os no log"""
        uploaded_files = self.read_uploaded_files()
        files = [f for f in os.listdir(self.path_DocGitHubData) if f.lower().endswith('.md')]
        new_files = [f for f in files if f not in uploaded_files]
        if new_files:
            for file in new_files:
                file_path = os.path.join(self.path_DocGitHubData, file)
                self.upload_to_vectorstore(app1, client, file_path, name)
                uploaded_files.add(file) 
                self.log_uploaded_file(file) 
            print(f"Novos arquivos carregados para {name}: {', '.join(new_files)}")
        else:
            print("Nenhum novo arquivo encontrado.")

    def upload_to_vectorstore(self, app1, client,  file_path, name):
 
        paths_to_upload  = [
            file_path
        ]

        vector_store_id = Agent_files.auth_or_create_vectorstore(app1, client, name, paths_to_upload, file_path)
        print(vector_store_id)
        print(paths_to_upload)
        print(file_path)
        

