import cx_Oracle
import loggerutility as logger
from datetime import datetime
import re

class Obj_Followup_Act:

    def check_or_update_followup_act(self, followup_act, connection):

        required_keys = [
            'obj_name', 'line_no', 'action_id'
        ]
        missing_keys = [key for key in required_keys if key not in followup_act]
        logger.log(f"Missing required keys for obj_followup_act table: {', '.join(missing_keys)}")

        if missing_keys:
            raise KeyError(f"Missing required keys for obj_followup_act table: {', '.join(missing_keys)}")
        else:
            obj_name = followup_act.get('obj_name', '')
            id = followup_act.get('id', '')
            line_no = followup_act.get('line_no', '')
            action_id = followup_act.get('action_id', '')
            action_type = followup_act.get('action_type', '')
            action_info = followup_act.get('action_info', '')
            conditional_expression = followup_act.get('conditional_expression', '')
            conditional_input = followup_act.get('conditional_input', '')
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_user = followup_act.get('chg_user', '').strip() or 'System'
            chg_term = followup_act.get('chg_term', '').strip() or 'System'
            max_retry_count = followup_act.get('max_retry_count', '')

            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM obj_followup_act 
                WHERE OBJ_NAME = :obj_name 
                AND LINE_NO = :line_no 
                AND ACTION_ID = :action_id
            """, obj_name=obj_name, line_no=line_no, action_id=action_id)
            count = cursor.fetchone()[0]
            logger.log(f"Count ::: {count}")
            cursor.close()
            if count > 0:
                logger.log(f"Inside update")

                cursor = connection.cursor()
                update_query = """
                    UPDATE obj_followup_act SET
                    ID = :id, ACTION_TYPE = :action_type, ACTION_INFO = :action_info,
                    CONDITIONAL_EXPRESSION = :conditional_expression, CONDITIONAL_INPUT = :conditional_input,
                    CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YY'), CHG_USER = :chg_user, CHG_TERM = :chg_term,
                    MAX_RETRY_COUNT = :max_retry_count
                    WHERE OBJ_NAME = :obj_name 
                    AND LINE_NO = :line_no 
                    AND ACTION_ID = :action_id
                """

                cursor.execute(update_query, {
                    'obj_name': obj_name,
                    'id': id,
                    'line_no': line_no,
                    'action_id': action_id,
                    'action_type': action_type,
                    'action_info': action_info,
                    'conditional_expression': conditional_expression,
                    'conditional_input': conditional_input,
                    'chg_date': chg_date,
                    'chg_user': chg_user,
                    'chg_term': chg_term,
                    'max_retry_count': max_retry_count
                })
                cursor.close()

            else:
                logger.log(f"Inside Insert")

                cursor = connection.cursor()
                insert_query = """
                    INSERT INTO obj_followup_act (
                    OBJ_NAME, ID, LINE_NO, ACTION_ID, ACTION_TYPE, ACTION_INFO,
                    CONDITIONAL_EXPRESSION, CONDITIONAL_INPUT, CHG_DATE, CHG_USER,
                    CHG_TERM, MAX_RETRY_COUNT
                    ) VALUES (
                    :obj_name, :id, :line_no, :action_id, :action_type, :action_info,
                    :conditional_expression, :conditional_input, TO_DATE(:chg_date, 'DD-MM-YY'), :chg_user,
                    :chg_term, :max_retry_count
                )
                """

                cursor.execute(insert_query, {
                    'obj_name': obj_name,
                    'id': id,
                    'line_no': line_no,
                    'action_id': action_id,
                    'action_type': action_type,
                    'action_info': action_info,
                    'conditional_expression': conditional_expression,
                    'conditional_input': conditional_input,
                    'chg_date': chg_date,
                    'chg_user': chg_user,
                    'chg_term': chg_term,
                    'max_retry_count': max_retry_count
                })
                cursor.close()

    def process_data(self, conn, follow_up_actions, obj_name):
        logger.log(f"Start of Obj_Followup_Act Class")
        for index, action in enumerate(follow_up_actions):
            parts = action.split(',', 1)
            new_parts = parts[1].split(':')

            logger.log(f"Inside follow_up_actions ::: {parts[0]}")
            logger.log(f"Inside follow_up_actions ::: {new_parts[0]}")
            logger.log(f"Inside follow_up_actions ::: {new_parts[1]}")

            action_id = ''
            action_info = ''
            if str(new_parts[1]).startswith("business_logic"):
                action_word = parts[0][3:]
                if 'add' == action_word.lower() or 'edit' == action_word.lower():
                    action_id = "save"
                else:
                    action_id = action_word

                action_info = new_parts[1].split("'")[1]
                logger.log(f"Inside action_id: {action_id}")
                logger.log(f"Inside business_logic: {action_info}")

                followup_act = {
                    'obj_name': obj_name,
                    'id': str(index+1),
                    'line_no': str(index+1),
                    'action_id': action_id,
                    'action_type': "D",
                    'action_info': action_info,
                    'conditional_expression': "",
                    'conditional_input': "",
                    'chg_date': datetime.now().strftime('%d-%m-%y'),
                    'chg_user': "System",
                    'chg_term': "System",
                    'max_retry_count': 0
                }
                logger.log(f"followup_act: {followup_act}")

                self.check_or_update_followup_act(followup_act, conn)

            elif str(new_parts[1]).startswith("email"):
                action_word = parts[0][3:]
                if 'add' == action_word.lower() or 'edit' == action_word.lower():
                    action_id = "save"
                else:
                    action_id = action_word

                logger.log(f"Inside action_id: {action_id}")

                followup_act = {
                    'obj_name': obj_name,
                    'id': str(index+1),
                    'line_no': str(index+1),
                    'action_id': action_id,
                    'action_type': "E",
                    'action_info': action_info,
                    'conditional_expression': "",
                    'conditional_input': "",
                    'chg_date': datetime.now().strftime('%d-%m-%y'),
                    'chg_user': "System",
                    'chg_term': "System",
                    'max_retry_count': 0
                }
                logger.log(f"followup_act: {followup_act}")

                self.check_or_update_followup_act(followup_act, conn)

                # -----------------------------------------------------------------------------

                pattern = r"email\((.*)\)"
                match = re.search(pattern, new_parts[1])

                format_code = ''
                body_mail = ''
                send_to = ''
                if match:
                    logger.log(f'Inside match ::: {match}')
                    inside_parentheses = match.group(1)
                    logger.log(f'Inside inside_parentheses ::: {inside_parentheses}')
                    pattern1 = r"\((.*)\)"
                    match1 = re.search(pattern1, inside_parentheses)
                    if match1:
                        logger.log(f'Inside match1 ::: {match1}')
                        send_to_lst = []
                        for data in match1.group(1).split(","):
                            send_to_lst.append('[(E)ROLE_CODE]')
                        send_to = ",".join(send_to_lst)
                    else:
                        send_to_word = inside_parentheses.split(",")[0].replace("'","")
                        logger.log(f"send_to_word ::: {send_to_word}")
                        if send_to_word == 'CUSTOMER_EMAIL':
                            send_to = "{(C)cust_code}"
                        else:
                            send_to = "[(E)ROLE_CODE]"

                    parts = inside_parentheses.split(",")
                    format_code = parts[-2].replace("'","")
                    body_mail = parts[-1].replace("'","")
                    logger.log(f"send_to ::: {send_to}")
                    logger.log(f"format_code ::: {format_code}")
                    logger.log(f"body_mail ::: {body_mail}")

                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT COUNT(*) FROM MAIL_FORMAT 
                    WHERE FORMAT_CODE = '{format_code}'
                """)

                count_mail_format = cursor.fetchone()[0]
                logger.log(f"Count MAIL_FORMAT {count_mail_format}")
                cursor.close()

                if count_mail_format > 0:
                    cursor = conn.cursor()
                    delete_query = f"""
                        DELETE FROM MAIL_FORMAT 
                        WHERE FORMAT_CODE = '{format_code}'
                    """
                    cursor.execute(delete_query)
                    cursor.close()
                    logger.log("Data deleted from MAIL_FORMAT")

                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO MAIL_FORMAT (
                        FORMAT_CODE, FORMAT_TYPE, SEND_TO, COPY_TO, BLIND_COPY, SUBJECT, BODY_COMP, PRIORITY,
                        DELIVERY_REPORT, RETURN_RECEIPT, MAIL_APPLICATION, MAIL_SERVER, MAIL_BOX, MAIL_ID, ATTACH_TYPE,
                        ATTACH_TEXT, WINNAME, WIN_NAME, MAIL_GENERATION, MAIL_DESCR, FN_NAME, COND_METHOD,
                        EMAIL_EXPR, ATTACH_OBJECT, TEMPLATE_PURPOSE, STATUS, USER_ID__OWN, BODY_TEXT
                    ) VALUES (
                        :format_code, :format_type, :send_to, :copy_to, :blind_copy, :subject, :body_comp, :priority,
                        :delivery_report, :return_receipt, :mail_application, :mail_server, :mail_box, :mail_id, :attach_type,
                        :attach_text, :winname, :win_name, :mail_generation, :mail_descr, :fn_name, :cond_method,
                        :email_expr, :attach_object, :template_purpose, :status, :user_id__own, :body_text
                    )
                """
                values = {
                    'format_code': format_code,
                    'format_type': 'T',
                    'send_to': send_to,
                    'copy_to': '',
                    'blind_copy': '',
                    'subject': body_mail,
                    'body_comp': '',
                    'priority': '',
                    'delivery_report': '',
                    'return_receipt': '',
                    'mail_application': 'M',
                    'mail_server': '',
                    'mail_box': '',
                    'mail_id': '',
                    'attach_type': '',
                    'attach_text': '',
                    'winname': '',
                    'win_name': f'w_{obj_name}',
                    'mail_generation': '',
                    'mail_descr': '',
                    'fn_name': '',
                    'cond_method': '',
                    'email_expr': '',
                    'attach_object': '',
                    'template_purpose': '',
                    'status': '',
                    'user_id__own': '',
                    'body_text': body_mail
                }
                logger.log(f"values ::: {values}")

                cursor.execute(insert_query, values)
                cursor.close()

        logger.log(f"End of Obj_Followup_Act Class")
