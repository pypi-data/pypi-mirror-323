import cx_Oracle
from datetime import datetime
import loggerutility as logger
import re

class Obj_Actions:

    sql_models = []
    event_context = 1
    
    def insert_or_update_actions(self, actions, connection):

        required_keys = [
            'obj_name', 'line_no', 'title'
        ]

        missing_keys = [key for key in required_keys if key not in actions]
        logger.log(f"Missing required keys for obj_actions table: {', '.join(missing_keys)}")

        if missing_keys:
            raise KeyError(f"Missing required keys for obj_actions table: {', '.join(missing_keys)}")
        else:
            obj_name = actions.get('obj_name', '')
            line_no = actions.get('line_no', '')
            image = actions.get('image', '')
            description = actions.get('description', '')
            service_code = actions.get('service_code', '')
            service_code = f"{obj_name}_{service_code}"
            interactive = actions.get('interactive', '')
            rights_char = actions.get('rights_char', '')
            title = actions.get('title', '')
            form_no = actions.get('form_no', '')
            service_handler = actions.get('service_handler', '')
            placement = actions.get('placement', '')
            action_type = actions.get('action_type', '')
            tran_type = actions.get('tran_type', '')
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_term = actions.get('chg_term', '').strip() or 'System'
            chg_user = actions.get('chg_user', '').strip() or 'System'
            is_confirmation_req = actions.get('confirmation_req', '')
            sep_duty_opt = actions.get('sep_duty_opt', '')
            re_auth_opt = actions.get('re_auth_opt', '')
            show_in_panel = actions.get('show_in_panel', '')
            page_context = actions.get('page_context', '')
            type_ = actions.get('type', '')  
            action_arg = actions.get('action_arg', '')
            swipe_position = actions.get('swipe_position', '')
            multi_row_opt = actions.get('multi_row_opt', '')
            action_id = actions.get('id', '')
            def_nodata = actions.get('def_no_data', '')
            in_proc_intrupt = actions.get('in_proc_intrupt', '')
            estimated_time = actions.get('estimated_time', '')
            action_group = actions.get('action_group', '')
            display_opt = actions.get('display_opt', '')
            display_mode = actions.get('display_mode', '')
            show_confirm = actions.get('show_confirm', '')
            rec_specific = actions.get('rec_specific', '')
            
            arg_list = actions.get('arg_list', [])
            function_name = actions.get('function_name', '')
            function_desc = actions.get('function_desc', '')

            cursor = connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM obj_actions WHERE OBJ_NAME = '{obj_name}' AND LINE_NO = '{line_no}'")
            count = cursor.fetchone()[0]
            cursor.close()
            if count > 0:
                cursor = connection.cursor()
                values = {
                    "obj_name": obj_name, "line_no": line_no, "image": image, "description": description, "service_code": str(service_code),
                    "interactive": interactive, "rights_char": rights_char, "title": title, "form_no": form_no, "service_handler": service_handler,
                    "placement": placement, "action_type": action_type, "tran_type": tran_type, "chg_date": chg_date, "chg_term": chg_term,
                    "chg_user": chg_user, "is_confirmation_req": is_confirmation_req, "sep_duty_opt": sep_duty_opt, "re_auth_opt": re_auth_opt,
                    "show_in_panel": show_in_panel, "page_context": page_context, "type": type_, "action_arg": action_arg, "swipe_position": swipe_position,
                    "multi_row_opt": multi_row_opt, "action_id": action_id, "def_nodata": def_nodata, "in_proc_intrupt": in_proc_intrupt, 
                    "estimated_time": estimated_time, "action_group": action_group, "display_opt": display_opt, "display_mode": display_mode,
                    "show_confirm": show_confirm, "rec_specific": rec_specific
                }

                update_query = """
                    UPDATE obj_actions SET
                    IMAGE = :image, DESCRIPTION = :description, SERVICE_CODE = :service_code,
                    INTERACTIVE = :interactive, RIGHTS_CHAR = :rights_char, TITLE = :title,
                    FORM_NO = :form_no, SERVICE_HANDLER = :service_handler, PLACEMENT = :placement,
                    ACTION_TYPE = :action_type, TRAN_TYPE = :tran_type, 
                    CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YYYY'), CHG_TERM = :chg_term, CHG_USER = :chg_user,
                    IS_CONFIRMATION_REQ = :is_confirmation_req, SEP_DUTY_OPT = :sep_duty_opt,
                    RE_AUTH_OPT = :re_auth_opt, SHOW_IN_PANEL = :show_in_panel,
                    PAGE_CONTEXT = :page_context, TYPE = :type, ACTION_ARG = :action_arg,
                    SWIPE_POSITION = :swipe_position, MULTI_ROW_OPT = :multi_row_opt,
                    ACTION_ID = :action_id, DEF_NODATA = :def_nodata, 
                    IN_PROC_INTRUPT = :in_proc_intrupt, ESTIMATED_TIME = :estimated_time,
                    ACTION_GROUP = :action_group, DISPLAY_OPT = :display_opt,
                    DISPLAY_MODE = :display_mode, SHOW_CONFIRM = :show_confirm,
                    REC_SPECIFIC = :rec_specific
                    WHERE OBJ_NAME = :obj_name AND LINE_NO = :line_no
                """
                cursor.execute(update_query, values)
                logger.log(f"Updated: {obj_name} - {line_no}")
                cursor.close()
            else:

                event_code = service_code

                cursor = connection.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM SYSTEM_EVENTS 
                    WHERE OBJ_NAME = :obj_name and EVENT_CODE = :event_code
                """, {'obj_name': obj_name,'event_code': event_code})
                
                count_system_events = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
                cursor.close()
                if count_system_events > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_EVENTS WHERE OBJ_NAME = :obj_name and EVENT_CODE = :event_code"
                    cursor.execute(delete_query, {
                        'obj_name': obj_name,
                        'event_code': event_code
                    })
                    cursor.close()
                    logger.log("Data deleted from SYSTEM_EVENTS") 

                cursor = connection.cursor()
                insert_query = """
                    INSERT INTO SYSTEM_EVENTS (
                        OBJ_NAME, EVENT_CODE, EVENT_CONTEXT, SERVICE_CODE, METHOD_RULE, OVERWRITE_CORE, 
                        CHG_DATE, CHG_USER, CHG_TERM, RESULT_HANDLE, COMP_TYPE, COMP_NAME, COMM_FORMAT, FIELD_NAME
                    ) VALUES (
                        :obj_name, :event_code, :event_context, :service_code, :method_rule, :overwrite_core, 
                        TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :result_handle, :comp_type, 
                        :comp_name, :comm_format, :field_name
                    )
                """
                values = {
                    'obj_name': obj_name,
                    'event_code': event_code,
                    'event_context': self.event_context,
                    'service_code': service_code,
                    'method_rule': None,
                    'overwrite_core': '0',
                    'chg_date': datetime.now().strftime('%d-%m-%y'),  
                    'chg_user': 'System',
                    'chg_term': 'System',
                    'result_handle': '2',
                    'comp_type': 'DB',
                    'comp_name': function_name,
                    'comm_format': None,
                    'field_name': ''
                }
                logger.log(f"values ::: {values}") 

                cursor.execute(insert_query, values)
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENTS") 

                # -------------------------------------------------------------------------------------

                cursor = connection.cursor()
                cursor.execute("""SELECT COUNT(*) FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = :service_code""", 
                               {'service_code': service_code})
                
                count_system_services = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENT_SERVICES {count_system_services}")
                cursor.close()
                if count_system_services > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_EVENT_SERVICES WHERE SERVICE_CODE = :service_code"
                    cursor.execute(delete_query, {'service_code': service_code})
                    cursor.close()
                    logger.log("Data deleted from SYSTEM_EVENT_SERVICES") 

                cursor = connection.cursor()
                insert_query = """
                    INSERT INTO SYSTEM_EVENT_SERVICES (
                        SERVICE_CODE, SERVICE_DESCR, SERVICE_URI, SERVICE_PROVIDER, METHOD_NAME, 
                        RETURN_VALUE, RETURN_TYPE, RETURN_DESCR, RETURN_XFRM, CHG_DATE, 
                        CHG_USER, CHG_TERM, SERVICE_NAMESPACE, RES_ELEM, SOAP_ACTION
                    ) VALUES (
                        :service_code, :service_descr, :service_uri, :service_provider, :method_name, 
                        :return_value, :return_type, :return_descr, :return_xfrm, 
                        TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, 
                        :service_namespace, :res_elem, :soap_action
                    )
                """
                values = {
                    'service_code': service_code,
                    'service_descr': function_desc,
                    'service_uri': function_name,
                    'service_provider': '',
                    'method_name': ' ',
                    'return_value': '',
                    'return_type': '',
                    'return_descr': '',
                    'return_xfrm': '',
                    'chg_date': datetime.now().strftime('%d-%m-%Y'),  
                    'chg_user': 'System',
                    'chg_term': 'System',
                    'service_namespace': '',
                    'res_elem': '',
                    'soap_action': ''
                }

                cursor.execute(insert_query, values)
                cursor.close()
                logger.log("Data inserted from SYSTEM_EVENT_SERVICES") 

                # -------------------------------------------------------------------------------------
                
                cursor = connection.cursor()
                cursor.execute("""SELECT COUNT(*) FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = :service_code""", 
                            {'service_code': service_code})
                
                count_system_services_args = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_SERVICE_ARGS {count_system_services_args}")
                cursor.close()
                if count_system_services_args > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_SERVICE_ARGS WHERE SERVICE_CODE = :service_code"
                    cursor.execute(delete_query, {'service_code': service_code})
                    cursor.close()
                    logger.log("Data deleted from SYSTEM_SERVICE_ARGS") 

                for index, args in enumerate(arg_list):
                    args_line_no = str(index+1)
                    cursor = connection.cursor()
                    insert_query = """
                        INSERT INTO SYSTEM_SERVICE_ARGS (
                            SERVICE_CODE, LINE_NO, ARG_NAME, ARG_MODE, DESCR, ARG_TYPE, 
                            ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM, ARG_VALUE
                        ) VALUES (
                            :service_code, :line_no, :arg_name, :arg_mode, :descr, :arg_type, 
                            :arg_xfrm, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_user, :chg_term, :arg_value
                        )
                    """
                    values = {
                        'service_code': service_code,
                        'line_no': args_line_no,
                        'arg_name': args.lower(),
                        'arg_mode': 'I',
                        'descr': '',
                        'arg_type': 'S',
                        'arg_xfrm': '',
                        'chg_date': datetime.now().strftime('%d-%m-%Y'),
                        'chg_user': 'System',
                        'chg_term': 'System',
                        'arg_value': ''
                    }

                    logger.log(f"SYSTEM_SERVICE_ARGS values ::: {values}")

                    cursor.execute(insert_query, values)
                    cursor.close()
                    logger.log("Data inserted from SYSTEM_SERVICE_ARGS") 

                # -------------------------------------------------------------------------------------
                cursor = connection.cursor()
                values = {
                    'obj_name': obj_name, 'line_no': line_no, 'image': image, 'description': description, 'service_code': str(service_code),
                    'interactive': interactive, 'rights_char': rights_char, 'title': title, 'form_no': form_no, 'service_handler': service_handler,
                    'placement': placement, 'action_type': action_type, 'tran_type': tran_type, 'chg_date': chg_date, 'chg_term': chg_term,
                    'chg_user': chg_user, 'is_confirmation_req': is_confirmation_req, 'sep_duty_opt': sep_duty_opt, 're_auth_opt': re_auth_opt,
                    'show_in_panel': show_in_panel, 'page_context': page_context, 'type': type_, 'action_arg': action_arg, 'swipe_position': swipe_position,
                    'multi_row_opt': multi_row_opt, 'action_id': action_id, 'def_nodata': def_nodata, 'in_proc_intrupt': in_proc_intrupt, 
                    'estimated_time': estimated_time, 'action_group': action_group, 'display_opt': display_opt, 'display_mode': display_mode,
                    'show_confirm': show_confirm, 'rec_specific': rec_specific
                }

                insert_query = """
                    INSERT INTO obj_actions (
                    OBJ_NAME, LINE_NO, IMAGE, DESCRIPTION, SERVICE_CODE, INTERACTIVE,
                    RIGHTS_CHAR, TITLE, FORM_NO, SERVICE_HANDLER, PLACEMENT, ACTION_TYPE,
                    TRAN_TYPE, CHG_DATE, CHG_TERM, CHG_USER, IS_CONFIRMATION_REQ,
                    SEP_DUTY_OPT, RE_AUTH_OPT, SHOW_IN_PANEL, PAGE_CONTEXT, TYPE,
                    ACTION_ARG, SWIPE_POSITION, MULTI_ROW_OPT, ACTION_ID, DEF_NODATA,
                    IN_PROC_INTRUPT, ESTIMATED_TIME, ACTION_GROUP, DISPLAY_OPT,
                    DISPLAY_MODE, SHOW_CONFIRM, REC_SPECIFIC
                    ) VALUES (
                    :obj_name, :line_no, :image, :description, :service_code, :interactive,
                    :rights_char, :title, :form_no, :service_handler, :placement, :action_type,
                    :tran_type, TO_DATE(:chg_date, 'DD-MM-YYYY'), :chg_term, :chg_user, :is_confirmation_req,
                    :sep_duty_opt, :re_auth_opt, :show_in_panel, :page_context, :type,
                    :action_arg, :swipe_position, :multi_row_opt, :action_id, :def_nodata,
                    :in_proc_intrupt, :estimated_time, :action_group, :display_opt,
                    :display_mode, :show_confirm, :rec_specific)
                """

                logger.log(f"obj_actions values ::: {values}")
                cursor.execute(insert_query, values)
                logger.log(f"Inserted: {obj_name} - {line_no}")
                cursor.close()

    def process_data(self, conn, sql_models_data, Owner):
        logger.log(f"Start of Obj_Actions Class")
        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "action" in sql_model['sql_model']:
                for actions in sql_model['sql_model']['action']:
                    if actions:
                        if ':' in actions['actual_func']:
                            logger.log(f"Actions: {actions['actual_func'].split(':')[1]}")
                            pattern = r"\w+\(['\"](.*?)['\"],\s*['\"](.*?)['\"]\)"
                            matches = re.findall(pattern, actions['actual_func'].split(':')[1])

                            sql_function_name = matches[0][0]
                            sql_desc = matches[0][1]
                            logger.log(f"Inside sql_function_name: {sql_function_name}")
                            logger.log(f"Inside sql_desc: {sql_desc}")
                            
                            cursor = conn.cursor()
                            queryy = f"""
                                SELECT LISTAGG(TEXT, '') WITHIN GROUP (ORDER BY LINE) AS FUNCTION_DEFINITION
                                FROM ALL_SOURCE
                                WHERE NAME = UPPER('{sql_function_name}')
                                AND TYPE = 'FUNCTION'
                                AND OWNER = '{Owner}'
                            """
                            cursor.execute(queryy)
                            result = cursor.fetchone()[0]
                            logger.log(f"\n result value:::\t{result}")
                            cursor.close()

                            if result != None:
                                cleaned_str = re.sub(r"\s+", " ", result).strip()
                                arg_list = []
                                patterns = ["-- (", "--("]  
                                for pattern in patterns:
                                    if pattern in cleaned_str:
                                        for i in cleaned_str.split(pattern):
                                            if ")" in i:
                                                new_str = i.split(")")[0]
                                                if '.' in new_str:
                                                    arg_list.append(f"{new_str.split('.')[1]}")

                                logger.log(f"\n Obj_Actions sql_input:::\t{arg_list}")

                                actions["arg_list"] = arg_list
                                actions["function_name"] = sql_function_name
                                actions["function_desc"] = sql_desc
                        
                        logger.log(f"actions ::: {actions}")
                        self.insert_or_update_actions(actions, conn)
        logger.log(f"End of Obj_Actions Class")
