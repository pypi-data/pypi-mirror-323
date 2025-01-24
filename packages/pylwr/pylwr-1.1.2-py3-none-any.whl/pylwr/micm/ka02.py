'''
此外，dataclass_json的to_json()和from_json()方法允许你轻松地将这些实体类实例转换为JSON字符串，以及从JSON字符串创建实体类实例。这使得在Python应用程序与其他系统或组件进行数据交换时非常方便。
'''
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional

@dataclass_json
@dataclass
class KA02:
    baz501: Optional[int] = None
    '''药品ID'''
    aka060: Optional[str] = None
    '''药品编码'''
    bka227: Optional[str] = None
    '''药品产品名（药监局注册名称）'''
    aka061: Optional[str] = None
    '''药品通用名'''
    bka462: Optional[str] = None
    '''药品知识库使用名称[仅供知识库匹配使用]'''
    bka221: Optional[str] = None
    '''商品名'''
    bka027: Optional[str] = None
    '''药品化学名（分子式）'''
    aka062: Optional[str] = None
    '''英文名称'''
    aka020: Optional[str] = None
    '''拼音助记码'''
    aka021: Optional[str] = None
    '''五笔助记码'''
    bka605: Optional[str] = None
    '''自定义码'''
    aka063: Optional[str] = None
    '''收费类别'''
    aka065: Optional[str] = None
    '''收费项目等级'''
    aka064: Optional[str] = None
    '''处方药标志'''
    aka067: Optional[str] = None
    '''药品剂量单位'''
    aka070: Optional[str] = None
    '''药品注册剂型'''
    aka170: Optional[str] = None
    '''标注剂型'''
    aka071: Optional[float] = None
    '''每次用量'''
    aka072: Optional[str] = None
    '''使用频次'''
    bka076: Optional[str] = None
    '''单位[包装单位]'''
    bka232: Optional[str] = None
    '''最小包装单位'''
    bka235: Optional[int] = None
    '''包装数量'''
    bka455: Optional[float] = None
    '''包装剂量[包装数量*规格剂量]'''
    aka074: Optional[str] = None
    '''规格'''
    bka456: Optional[float] = None
    '''规格剂量[装量]'''
    bka457: Optional[str] = None
    '''规格剂量单位[装量]'''
    bka458: Optional[float] = None
    '''规格剂量[含量]'''
    bka460: Optional[str] = None
    '''规格剂量单位[含量]'''
    bka461: Optional[str] = None
    '''规格备注'''
    bka084: Optional[str] = None
    '''院内制剂标志'''
    akb020: Optional[str] = None
    '''定点医疗机构编码'''
    bka608: Optional[str] = None
    '''特药标志'''
    aka107: Optional[str] = None
    '''用法'''
    aka108: Optional[int] = None
    '''限定天数'''
    aae013: Optional[str] = None
    '''备注'''
    aka109: Optional[str] = None
    '''药厂名称'''
    aka085: Optional[str] = None
    '''批准文号'''
    bka616: Optional[str] = None
    '''产地'''
    bka620: Optional[str] = None
    '''药品分类编号'''
    bka613: Optional[str] = None
    '''限制使用范围'''
    bka639: Optional[int] = None
    '''单处方限制数量'''
    bkc173: Optional[str] = None
    '''是否需要审批标志'''
    aka101: Optional[str] = None
    '''最小医院等级'''
    bka602: Optional[str] = None
    '''最小医师等级'''
    ala011: Optional[str] = None
    '''工伤使用标志'''
    ama011: Optional[str] = None
    '''生育使用标志'''
    aka022: Optional[str] = None
    '''基本医疗使用标识'''
    aae030: Optional[int] = None
    '''开始日期'''
    aae031: Optional[int] = None
    '''终止日期'''
    aka068: Optional[float] = None
    '''最高限价'''
    bka205: Optional[str] = None
    '''零差价药品标识'''
    bka106: Optional[str] = None
    '''中草药管理办法'''
    bka204: Optional[str] = None
    '''中心使用标志'''
    bka610: Optional[str] = None
    '''国家目录编码'''
    bka210: Optional[str] = None
    '''门诊统筹可用标识'''
    aae100: Optional[str] = None
    '''有效标志'''
    bka217: Optional[str] = None
    '''非单处方药标识 (1 是，0 或者空为否)'''
    bka218: Optional[str] = None
    '''药品一级编码'''
    bka219: Optional[str] = None
    '''药品二级编码'''
    bka220: Optional[str] = None
    '''药品三级编码'''
    bka222: Optional[str] = None
    '''限定条件'''
    bka200: Optional[str] = None
    '''维护标志（0，默认未维护；1，已维护）'''
    bka224: Optional[str] = None
    '''药监本位码'''
    bka225: Optional[str] = None
    '''备用2'''
    bka226: Optional[str] = None
    '''备用3'''
    bka228: Optional[str] = None
    '''备用4'''
    bka229: Optional[str] = None
    '''备用5'''
    bze011: Optional[str] = None
    '''创建人'''
    bze036: Optional[int] = None
    '''创建时间'''
    aae011: Optional[str] = None
    '''经办人'''
    aae036: Optional[int] = None
    '''经办时间'''
    aab034: Optional[str] = None
    '''经办机构编码'''
    aaa027: Optional[str] = None
    '''统筹区编码'''
    baz002: Optional[int] = None
    '''操作序号'''
    baa027: Optional[str] = None
    '''地区代码'''
    bka506: Optional[str] = None
    '''药品类别[1-西药 2-中成药 3-中药饮片/草药 4-生物制品 5-辅料]'''
    bka700: Optional[str] = None
    '''对照标志（0，默认未对照；1，已对照）'''
    bka505: Optional[str] = None
    '''注射液标识（1 是，0 否）'''
    bka561: Optional[str] = None
    '''基本医疗保险药品代码'''
    bka562: Optional[str] = None
    '''药品四级编码'''
    bka563: Optional[str] = None
    '''中药单味复方不予支付标识'''
    bka564: Optional[str] = None
    '''备用7'''
    bka565: Optional[str] = None
    '''备用8'''
    bka566: Optional[str] = None
    '''备用9'''
    bka567: Optional[str] = None
    '''备用10'''
    bka568: Optional[str] = None
    '''备用11'''
    bka569: Optional[str] = None
    '''备用12'''
    bka570: Optional[str] = None
    '''备用13'''
    bkf800: Optional[str] = None
    '''限制种类（1-急救，2-器官移植，3-下肢关节置换，4-放化疗，5-限儿童，6-限新生儿）'''