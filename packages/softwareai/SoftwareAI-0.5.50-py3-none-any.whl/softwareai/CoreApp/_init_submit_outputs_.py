
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.pegar_hora_submit_outputs import submit_output_pegar_hora

from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.upload_project_py_submit_outputs import submit_output_upload_project_py
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.get_current_datetime_submit_outputs import submit_output_get_current_datetime
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.improve_code_and_create_pull_request_submit_outputs import submit_output_improve_code_and_create_pull_request
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.test_software_submit_outputs import submit_output_test_software
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.add_project_map_submit_outputs import submit_output_add_projectmap_to_github
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.analyze_file_outputs import submit_output_analyze_file
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.save_TXT_outputs import submit_output_save_TXT
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.save_code_outputs import submit_output_save_code
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.execute_py_outputs import submit_output_execute_py
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.update_readme_outputs import submit_output_update_readme
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autosave_submit_outputs import submit_output_autosave
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autoupload_submit_outputs import submit_output_autoupload
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.create_repo_submit_outputs import submit_output_create_repo
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autopullrequest import submit_output_autopullrequest
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autoupdaterepo import submit_output_autoupdaterepo
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autogetstructure import submit_output_get_repo_structure
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autogetfilecontent import submit_output_autogetfilecontent
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.autocheckcommentspr import submit_output_checkcommentspr
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.Software_Support.TicketProblem import submit_output_TicketProblem
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.Software_Technical_Support.AutoGetLoggerUser import submit_output_AutoGetLoggerUser
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.Software_Development_Testing.AutoTestModule import submit_output_AutoTestModule
from softwareai.CoreApp.SoftwareAI.Functions_Submit_Outputs.Software_Support.GearAssist import submit_output_GearAssist



from firebase_admin import App
from typing import Optional


def _init_output_(function_name,
                function_arguments,
                tool_call,
                threead_id,
                client,
                run,
                appfb,
                OpenAIKeysteste,
                GithubKeys,
                python_functions,
                Agent_files_update,
                AutenticateAgent,
                ResponseAgent,
                app_product: Optional[App] = None,
                ):
    
    functions_to_call = [
        submit_output_pegar_hora,
        submit_output_get_current_datetime,
        submit_output_upload_project_py,
        submit_output_improve_code_and_create_pull_request,
        submit_output_test_software,
        submit_output_add_projectmap_to_github,
        submit_output_analyze_file,
        submit_output_save_TXT,
        submit_output_save_code,
        submit_output_execute_py,
        submit_output_update_readme,
        submit_output_autosave,
        submit_output_autoupload,
        submit_output_create_repo,
        submit_output_autopullrequest,
        submit_output_autoupdaterepo,
        submit_output_get_repo_structure,
        submit_output_autogetfilecontent,
        submit_output_checkcommentspr,
        submit_output_TicketProblem,
        submit_output_AutoGetLoggerUser,
        submit_output_AutoTestModule,
        submit_output_GearAssist
    ]
    
    for func in functions_to_call:
        if func == submit_output_get_current_datetime:
            flag = func(function_name, function_arguments, tool_call, threead_id, client, run)
            if flag:
                return True
        elif func == submit_output_autoupdaterepo:
            flag = func(function_name, function_arguments, tool_call, threead_id, client, run, 
                        appfb,
                        OpenAIKeysteste,
                        GithubKeys,
                        python_functions,
                        Agent_files_update,
                        AutenticateAgent,
                        ResponseAgent,
                    )
            if flag:
                return True
        elif func == submit_output_TicketProblem:
            flag = func(function_name, function_arguments, tool_call, threead_id, client, run, 
                        appfb
                    )
            if flag:
                return True
            
        elif func == submit_output_AutoGetLoggerUser:
            flag = func(function_name, function_arguments, tool_call, threead_id, client, run, 
                        appfb, app_product
                    )
            if flag:
                return True
        elif func == submit_output_GearAssist:
            flag = func(function_name, function_arguments, tool_call, threead_id, client, run, 
                        appfb, app_product
                    )
            if flag:
                return True

        else:
            func(function_name, function_arguments, tool_call, threead_id, client, run)