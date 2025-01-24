import json


class PylwrError(object):
    """Exception related to operation with Pylwr."""
    def __init__(self, before_obj: object)-> None:
        '''
        生成报错需要传入报错之前的各项参数值, 方便排查, 需要json格式
        '''
        print(json.dumps(before_obj, ensure_ascii=False, indent=2, separators=(',', ':')))
        raise Exception