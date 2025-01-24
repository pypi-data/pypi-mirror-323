from typing import List, Type, TypeVar
from dataclasses_json import DataClassJsonMixin
import orjson
import pandas as pd

T = TypeVar('T', bound=DataClassJsonMixin)

def listObject_to_dataclass(news: List[dict], dataclass_type: Type[T], field_mapping: dict) -> List[T]:
    """
    将List[dict]数据转换为指定的dataclass对象列表。

    Args:
        news (List[dict]): 每行为一个字典，例如：
            [{'项目编码': 'XB05BAI002B002010104817', '通用名称': '18种氨基酸注射液', '备注': ''}, ...]
        dataclass_type (Type[T]): 目标 dataclass 类型，例如 KA02。
        field_mapping (dict): 字段映射，将Excel列名映射到dataclass属性名，例如：
            {"项目编码": "aka060", "通用名称": "aka061", "备注": "aae013"}

    Returns:
        List[T]: 转换后的 dataclass 实例列表

    Raises:
        ValueError: 如果转换过程中遇到数据问题。
    """
    news = [{k.strip(): v for k, v in item.items()} for item in news]
    df = pd.DataFrame(news)
    df.rename(columns={k.strip(): v for k, v in field_mapping.items()}, inplace=True)
    records = df.to_dict(orient="records")

    return [dataclass_type.from_dict(record) for record in records]
