import cx_Oracle
import loggerutility as logger
import json
from datetime import datetime
import re

class Obj_Itemchange:
    
    sql_models = []
    event_context = 1
        
    def is_valid_json(self, data):
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False

    def check_or_update_obj_itemchange(self, item_change,connection):

        required_keys = ['obj_name', 'form_no', 'field_name']
        missing_keys = [key for key in required_keys if key not in item_change]
        logger.log(f"Missing required keys for obj_itemchange table: {missing_keys}")

        if missing_keys:
            raise KeyError(f"Missing required keys for obj_itemchange table: {', '.join(missing_keys)}")
        else:
            obj_name = item_change.get('obj_name', '')
            form_no = item_change.get('form_no', '')
            field_name = item_change.get('field_name', '')
            mandatory = item_change.get('mandatory_server', '')
            exec_at = item_change.get('exec_at', '')
            js_arg = item_change.get('js_arg', '')
            arg_list = item_change.get('arg_list', [])
            function_name = item_change.get('function_name', '')
            function_desc = item_change.get('function_desc', '')
        
            cursor = connection.cursor()
            queryy = f"""
                SELECT COUNT(*) FROM obj_itemchange 
                WHERE OBJ_NAME = '{obj_name}'
                AND FORM_NO =  '{form_no}'
                AND FIELD_NAME =  '{field_name.lower()}'
            """
            cursor.execute(queryy)
            count = cursor.fetchone()[0]
            cursor.close()
            if count > 0:
                cursor = connection.cursor()
                update_query = """
                    UPDATE obj_itemchange SET
                    MANDATORY = :mandatory,
                    EXEC_AT = :exec_at,
                    JS_ARG = :js_arg
                    WHERE OBJ_NAME = :obj_name 
                    AND FORM_NO = :form_no
                    AND FIELD_NAME = :field_name
                """
                cursor.execute(update_query, {
                    'obj_name': obj_name,
                    'form_no': form_no,
                    'field_name': field_name.lower(),
                    'mandatory': mandatory,
                    'exec_at': exec_at,
                    'js_arg': js_arg
                })
                cursor.close()
            else:

                self.event_context = self.event_context + 1

                service_code = f'poic_{obj_name}_{field_name}'
                logger.log(f"obj_item_changed obj_name :: {obj_name}")
                logger.log(f"obj_item_changed service_code :: {service_code}")

                cursor = connection.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM SYSTEM_EVENTS 
                    WHERE OBJ_NAME = :obj_name and EVENT_CODE = :event_code and FIELD_NAME = :field_name
                """, {'obj_name': obj_name,'event_code': 'post_item_change','field_name': field_name.lower()})
                
                count_system_events = cursor.fetchone()[0]
                logger.log(f"Count SYSTEM_EVENTS {count_system_events}")
                cursor.close()
                if count_system_events > 0:
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM SYSTEM_EVENTS WHERE OBJ_NAME = :obj_name and EVENT_CODE = :event_code and FIELD_NAME = :field_name"
                    cursor.execute(delete_query, {
                        'obj_name': obj_name,
                        'event_code': 'post_item_change',
                        'field_name': field_name.lower()
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
                    'event_code': 'post_item_change',
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
                    'field_name': field_name.lower()
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

                # --------------------------------

                cursor = connection.cursor()
                insert_query = f"""
                    INSERT INTO SYSTEM_SERVICE_ARGS (SERVICE_CODE, LINE_NO, ARG_NAME, 
                    ARG_MODE, DESCR, ARG_TYPE, ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM,
                    ARG_VALUE) VALUES ('{service_code}', '1', 'COMPONENT_TYPE', 'I', 
                    '', 'S', '', TO_DATE('{datetime.now().strftime('%d-%m-%Y')}', 'DD-MM-YYYY'), 
                    'System', 'System', 'DB')
                """
                cursor.execute(insert_query)
                cursor.close()
                logger.log(f"SYSTEM_SERVICE_ARGS values ::: {insert_query}")

                cursor = connection.cursor()
                insert_query = f"""
                    INSERT INTO SYSTEM_SERVICE_ARGS (SERVICE_CODE, LINE_NO, ARG_NAME, 
                    ARG_MODE, DESCR, ARG_TYPE, ARG_XFRM, CHG_DATE, CHG_USER, CHG_TERM,
                    ARG_VALUE) VALUES ('{service_code}', '2', 'COMPONENT_NAME', 'I', 
                    '', 'S', '', TO_DATE('{datetime.now().strftime('%d-%m-%Y')}', 'DD-MM-YYYY'), 
                    'System', 'System', '{function_name}')
                """
                cursor.execute(insert_query)
                cursor.close()
                logger.log(f"SYSTEM_SERVICE_ARGS values ::: {insert_query}")

                # --------------------------------

                for index, args in enumerate(arg_list):
                    line_no = str(index+3)

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
                        'line_no': line_no,
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
                insert_query = """
                                INSERT INTO obj_itemchange (
                                OBJ_NAME, FORM_NO, FIELD_NAME, MANDATORY, EXEC_AT, JS_ARG
                                ) VALUES (:obj_name, :form_no, :field_name, :mandatory, :exec_at, :js_arg)
                            """
                
                cursor.execute(insert_query, {
                    'obj_name': obj_name,
                    'form_no': form_no,
                    'field_name': field_name.lower(),
                    'mandatory': mandatory,
                    'exec_at': exec_at,
                    'js_arg': js_arg
                })
                cursor.close()
                logger.log("Data inserted from obj_itemchange") 

    def process_data(self, conn, sql_models_data, object_name, Owner):
        logger.log(f"Start of Obj_Itemchange Class")
        self.sql_models = sql_models_data
        for sql_model in self.sql_models:
            if "sql_model" in sql_model and "columns" in sql_model['sql_model']:
                for column in sql_model['sql_model']['columns']:
                    if "column" in column and "item_change" in column['column']:
                        item_change = column['column']['item_change']
                        logger.log(f"Value of item_change :: {item_change}")
                        # if self.is_valid_json(item_change):
                        if str(item_change).startswith("business_logic"):
                            sql_function_name = item_change.split("'")[1]
                            sql_desc = item_change.split("'")[3]
                            fld_name = column['column']['db_name']
                            form_no = sql_model['sql_model']['form_no']
                            logger.log(f"Inside sql_function_name: {sql_function_name}")
                            logger.log(f"Inside sql_desc: {sql_desc}")
                            logger.log(f"Inside fld_name: {fld_name}")
                            
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

                                logger.log(f"\n obj_itemchange sql_input:::\t{arg_list}")

                                item_change_json = {
                                    'obj_name': object_name,
                                    'form_no': form_no,
                                    'field_name': fld_name,
                                    'arg_list': arg_list,
                                    'function_name': sql_function_name,
                                    'function_desc': sql_desc
                                }
                                self.check_or_update_obj_itemchange(item_change_json, conn)
        logger.log(f"End of Obj_Itemchange Class")