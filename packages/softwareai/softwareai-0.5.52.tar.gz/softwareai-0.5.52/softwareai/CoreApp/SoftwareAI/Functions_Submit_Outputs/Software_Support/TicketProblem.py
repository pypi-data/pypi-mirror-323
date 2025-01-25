#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################
# IMPORT SoftwareAI Core
from softwareai.CoreApp._init_core_ import * 
#########################################

# IMPORT SoftwareAI Functions
from softwareai.CoreApp._init_functions_ import *
#########################################
import inspect
import json
tool_outputs = []
def submit_output_TicketProblem(function_name,
                                function_arguments,
                                tool_call,
                                threead_id,
                                client,
                                run,
                                appfb,
                                appproduct
                                ):

    global tool_outputs
    # if function_name == 'OpenSupportTicketProblem':
    #     args = json.loads(function_arguments)
    #     result = OpenSupportTicketProblem(
    #         user_email=args['user_email'],
    #         issue_description=args['issue_description'],
    #         appfb=appfb
    #     )
    #     tool_call_id = tool_call.id
    #     client.beta.threads.runs.submit_tool_outputs(
    #         thread_id=threead_id,
    #         run_id=run.id,
    #         tool_outputs=[
    #             {
    #                 "tool_call_id": tool_call_id, 
    #                 "output": json.dumps(result)  
    #             }
    #         ]
    #     )


    # Mapear funções pelo nome
    functions_map = {
        "OpenSupportTicketProblem": OpenSupportTicketProblem,  # Adicione mais funções aqui se necessário
    }

    # Obter a função correspondente
    target_function = functions_map.get(function_name)
    if not target_function:
        print(f"Função {function_name} não encontrada.")
        return False

    # Inspecionar os argumentos da função
    function_signature = inspect.signature(target_function)
    function_parameters = function_signature.parameters

    # Preparar argumentos para chamada
    args = json.loads(function_arguments)
    call_arguments = {}

    # Adicionar parâmetros obrigatórios (appcompany e appproduct) se forem necessários
    if "appcompany" in function_parameters:
        call_arguments["appcompany"] = appfb
    if "appproduct" in function_parameters:
        call_arguments["appproduct"] = appproduct

    # Adicionar outros argumentos do JSON somente se estiverem na assinatura da função
    for arg_name, arg_value in args.items():
        if arg_name in function_parameters:
            call_arguments[arg_name] = arg_value

    try:
        # Chamar a função com os argumentos preparados
        result = target_function(**call_arguments)

        # Submeter o resultado
        tool_call_id = tool_call.id
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=threead_id,
            run_id=run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call_id,
                    "output": json.dumps(result),
                }
            ]
        )
        print("Tool outputs submitted successfully.")
        return True

    except Exception as e:
        print(f"Erro ao executar {function_name}: {e}")
        



    if function_name == 'CloseSupportTicketProblem':
        args = json.loads(function_arguments)
        result = CloseSupportTicketProblem(
            ticketid=args['ticketid'],
            appfb=appfb
        )
        tool_outputs.append({
        "tool_call_id": tool_call.id,
        "output": result
        })

        if tool_outputs:
            try:
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=threead_id,
                run_id=run.id,
                tool_outputs=tool_outputs
                )
                print("Tool outputs submitted successfully.")
                tool_outputs = []
                return True
            except Exception as e:
                print("Failed to submit tool outputs:", e)
        else:
            print("No tool outputs to submit.")

    if function_name == 'RecordCSAT':
        args = json.loads(function_arguments)
        result = RecordCSAT(
            ticketid=args['ticketid'], 
            csat_score=args['csat_score'],
            appfb=appfb
        )
        tool_outputs.append({
        "tool_call_id": tool_call.id,
        "output": result
        })

        if tool_outputs:
            try:
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=threead_id,
                run_id=run.id,
                tool_outputs=tool_outputs
                )
                print("Tool outputs submitted successfully.")
                tool_outputs = []
                return True
            except Exception as e:
                print("Failed to submit tool outputs:", e)
        else:
            print("No tool outputs to submit.")


    if tool_outputs:
        try:
            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=threead_id,
            run_id=run.id,
            tool_outputs=tool_outputs
            )
            print("Tool outputs submitted successfully.")
            tool_outputs = []
            return True
        except Exception as e:
            print("Failed to submit tool outputs:", e)
    else:
        print("No tool outputs to submit.")