import os
import re
from PyQt5.QtCore import QThread

class QListAgents(QThread):
    def __init__(self):
        super().__init__()
        pass

    def run(self):
        """Retorna a lista de agentes encontrados."""
        paths_agents = self.init_paths_agents()
        agents = []
        
        for path in paths_agents:
            try:
                agentss = os.listdir(path)
                for agent in agentss:
                    if agent in ["DocGitHubData", "docs_uploaded.log", "__pycache__",
                                "Expressvpn_auto_rotate",
                                "Ivpnautorotate",
                                "technical_report",
                                "Mullvadvpn_auto_rotate",
                                "Multi_Vpn_Auto_Rotate",
                                "Nordvpn_auto_rotate",
                                "PIAvpn_auto_rotate",
                                "Windscribevpn_auto_rotate"
                                ]:
                        continue
                    agentpath = os.path.join(path, agent)
                    try:
                        with open(agentpath, 'r', encoding='latin-1') as file:
                            content = file.read()
                            matches = re.findall(r'key\s*[:=]\s*["\']?([^"\',\s]+)["\']?', content)
                            if matches:
                                agents.append(matches[0])  # Adiciona a chave do agente
                    except Exception as e:
                        print(f"Erro ao processar o arquivo {agentpath}: {e}")
            except Exception as e:
                print(f"Erro ao acessar o diretório {path}: {e}")
        
        return agents

    def init_paths_agents(self):
        """Inicializa os caminhos dos agentes."""
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../CoreApp/Agents'))
        categories = [
            "Software_Support",
            "Software_Technical_Support",
            "Software_Requirements_Analysis",
            "Software_Planning",
            "Software_Documentation",
            "Software_Development",
            "Pre_Project",
            "Company_Managers",
            "Company_CEO"
        ]
        return [os.path.join(base_path, category) for category in categories]
