import sys
from loguru import logger

logger.add(sys.stderr, level="CRITICAL", format="{time} {level} {message}", colorize=True)

def warning(text: str) -> None:
    """输出警告日志信息。

    Args:
        text (str): 日志内容，需记录的警告信息。

    Returns:
        None: 该函数不返回任何值，日志信息将被记录。
    """
    logger.warning(text)
