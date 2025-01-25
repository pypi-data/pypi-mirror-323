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

tool_outputs = []
def submit_output_GearAssist(function_name,
                                function_arguments,
                                tool_call,
                                threead_id,
                                client,
                                run,
                                appfb,
                                app_product
                                ):

    global tool_outputs
    if function_name == 'GearAssist_Technical_Support':
        args = json.loads(function_arguments)
        GearAssistclass = GearAssist()
        result = GearAssistclass.GearAssist_Technical_Support(
            Ticketid=args['Ticketid'],
            appcompany=appfb,
            app_product=app_product
        )
        tool_call_id = tool_call.id
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=threead_id,
            run_id=run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call_id, 
                    "output": json.dumps(result)  
                }
            ]
        )




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