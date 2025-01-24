from pylwr import add, Db
from pylwr.const import *



def get_knowledge_active(db: Db, )-> list:
    """
    获取当前在用的知识库

    :rtype: list
    """
    result = db.select_json('SELECT RULE_NAME, SQL FROM RULE_INFO WHERE ID IN (SELECT RULE_ID FROM RULE_INSTANCE WHERE VALID_FLAG = 1 AND START_FLAG = 1)')
    return result

def get_drug_active(db: Db, )-> list:
    """
    获取药品在用的知识库

    :rtype: list
    """
    result = db.select_json('SELECT RULE_NAME, SQL FROM RULE_INFO WHERE ID IN (SELECT RULE_ID FROM RULE_INSTANCE WHERE VALID_FLAG = 1 AND START_FLAG = 1 AND RULE_NAME LIKE \'%药%\')')
    return result

@add(FUN_IS_MIDC)
def is_medical_insurance_drug_code(text: str, )-> bool:
    """
    判断字符串是不是西药中成药的贯标码
    :param: text 需要判断的字符串
    :type text: str

    :rtype: bool
    """
    code = ''
    if not isinstance(text, str):
        code = str(text)
    else:
        code = text
    # 西药药品编码以'X'开头，中成药药品编码以'Z'开头
    if code.startswith('X') or code.startswith('Z'):
        # 检查编码长度是否为23位, 有时候20位也有
        if len(code) == 23 or len(code) == 20:
            return True
    return False
    