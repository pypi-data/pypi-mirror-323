# CLI do SoftwareAI (Interface de Linha de Comando)

## Visão Geral

A Interface de Linha de Comando (CLI) do SoftwareAI foi projetada para simplificar e automatizar diversas tarefas relacionadas ao gerenciamento e uso do framework SoftwareAI.

## Problemas Resolvidos

# 1. Gerenciamento de Configurações

#### Configuração de Banco de Dados da Empresa
- Configurar e armazenar credenciais de banco de dados da empresa de forma segura

##### Exemplo de Comando
```bash
# Configuração de Banco de Dados da Empresa
python softwareai-cli.py configure-db-company \
  --namefordb "Nome do Banco de Dados" \
  --databaseurl "https://database.url" \
  --storagebucketurl "https://storage.bucket" \
  --pathkey "/caminho/para/chave-firebase-admin-sdk.json"
```
#### Configuração de Banco de Dados do aplicativo
- Configurar facilmente conexões de banco de dados para aplicações gerenciadas

##### Exemplo de Comando
```bash
# Configuração de Banco de Dados do aplicativo
python softwareai-cli.py configure-db-app \
  --namefordb "Nome do Banco de Dados" \
  --databaseurl "https://database.url" \
  --storagebucketurl "https://storage.bucket" \
  --pathkey "/caminho/para/chave-firebase-admin-sdk.json"
```
#

#### Integrações de APIs e Serviços
  


#### Configuração de Credenciais da OpenAI
- Configuração rápida para Credenciais da OpenAI
##### Exemplo de Comando
```bash
python softwareai-cli.py configure-openai --name "Nome para Credenciais da OpenAI" --key "OpenAI-Key" 
```
#
#### Configuração de Credenciais da Hugging Face
- Configuração rápida para Chaves de API da Hugging Face
##### Exemplo de Comando
```bash
python softwareai-cli.py configure-huggingface --name "Nome para Credenciais da Hugging Face" --key "Hugging-Face-Key" 
```
#
#### Configuração de Credenciais do Github
- Configuração rápida para Chaves de API dos agentes na plataforma Github
##### Exemplo de Comando
```bash
python softwareai-cli.py configure-github-keys --name "Nome para Credenciais do Github" --github-username "Usuario do agente no github" --github-token "Chave do agente no github"
```

#

# 2. Geração Automatizada de Tools
- Criar uma tool para um agente com base em um arquivo de função python e categoria 
```bash
python softwareai-cli.py create-function --pathfunction "path/to/function.py" --category "Categoria da funcao" 
```


- Criar instruções de agentes com facilidade
- Gerar prompts otimizados para interações de agentes

### 3. Gerenciamento de Agentes e Sistema

- Execução local da interface web do SoftwareAI
- Modificação automatizada de componentes de agentes
- Execução direta de tarefas específicas de agentes

## Referência de Comandos da CLI

### Comandos de Configuração
```bash
# Configuração de Banco de Dados
python cli.py configure-db-company --key "sua_chave_db"
python cli.py configure-db-app --key "sua_chave_db_app"

# Configuração de Serviços de IA
python cli.py configure-openai --key "sua_chave_openai"
python cli.py configure-huggingface --key "sua_chave_huggingface"
```

### Comandos de Automação
```bash
# Criação de Funções e Agentes
python cli.py create-function --description "Função de Exemplo"
python cli.py create-instruction --agent-name "Agent1" --instruction "Instrução de Exemplo"
python cli.py create-prompt --agent-name "Agent1" --prompt "Prompt de Exemplo"
```

### Comandos de Gerenciamento
```bash
# Gerenciamento de Sistema e Agentes
python cli.py run-web
python cli.py modify-agent --agent-name "Agent1" --component "componenteX" --new-value "novo_valor"
python cli.py execute-agent-task --agent-name "Agent1" --task "tarefaX"
```

## Melhores Práticas

- Sempre use chaves seguras e específicas do ambiente
- Atualize e altere as credenciais regularmente
- Valide as configurações antes da implantação
