#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################
# IMPORT SoftwareAI Core
from softwareai.CoreApp._init_core_ import * 
#########################################
# IMPORT SoftwareAI Settings
from Chat.QListAgent import QListAgents
from Chat.QReadOpenAI import QReadOpenAi
#########################################
# IMPORT SoftwareAI Keys
from softwareai.CoreApp.KeysFirebase.keys import Firebase_App
from softwareai.CoreApp.KeysOpenAI.keys import OpenAIKeysteste
#########################################



app = Flask(__name__)
CORS(app)  
app.secret_key = os.urandom(24)  

app1 = Firebase_App()
key_openai = OpenAIKeysteste.keys()
client = OpenAIKeysinit._init_client_(key_openai)

# Caminho do arquivo de log
LOG_FILE = 'Cache\WebChat.json'

# Função para carregar o log do arquivo JSON
def load_log():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return defaultdict(list)

# Função para salvar o log no arquivo JSON
def save_log(log_data):
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as file:
            json.dump(log_data, file, indent=4)
    except FileNotFoundError:
        return 
    
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message')
    agent = data.get('agent')  # Obtém o valor do agente enviado pelo frontend
    print(agent)
    # Verifica se o agente foi fornecido
    if not agent:
        return jsonify({'error': 'Agent is required'}), 400

    AI, instructionsassistant, nameassistant, model_select  = AutenticateAgent.create_or_auth_AI(
        app1=app1,
        client=client,
        key=agent
        
    )

    agent_response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                                mensagem=user_message,
                                                                agent_id=AI,
                                                                app1=app1,
                                                                key=agent,
                                                                client=client,
                                                                model_select=model_select,
                                                                AgentDestilation=False
                                                            )
    try:
            
        # Carregar o log atual, utilizando defaultdict para evitar KeyError
        log_data = load_log()

        # Usar defaultdict para garantir que a chave exista
        if agent not in log_data:
            log_data[agent] = []

        # Adicionar a nova entrada no log, com o 'agent' como chave
        log_data[agent].append({
            'user_message': user_message,
            'agent_response': agent_response
        })

        # Salvar o log atualizado no arquivo
        save_log(log_data)
    except Exception as e:
        pass

    # Retorna a resposta para o frontend
    return jsonify({'response': agent_response})


@app.route('/api/agents', methods=['GET'])
def get_agents():
    try:
        # Instanciar e executar a classe QListAgents
        agent_list_thread = QListAgents()
        agents = agent_list_thread.run()  # Recupera a lista de agentes
        return jsonify(agents), 200
    except Exception as e:
        return jsonify({"error agents": str(e)}), 500

@app.route('/api/messages/<string:agent>', methods=['GET'])
def get_messages(agent):
    log_data = load_log()

    # Verifica se o agente tem mensagens armazenadas
    if agent not in log_data:
        return jsonify({'error messages': 'No messages found for this agent'}), 404

    # Retorna as mensagens armazenadas para o agente
    messages = log_data[agent]
    return jsonify(messages)

@app.route('/api/threads/<agent>', methods=['GET'])
def get_threads(agent):
    try:
        # Configurar QReadOpenAi
        qread = QReadOpenAi(agent=agent, appx=app1, client=client)
        qread.start()
        qread.wait()  # Aguarda a conclusão da thread
        print(qread.result)
        if qread.result and "error" in qread.result:
            return jsonify({"error threads": qread.result["threads"]}), 500

        return jsonify(qread.result), 200
    except Exception as e:
        return jsonify({"threads": str(e)}), 500
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)
