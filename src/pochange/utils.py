"""工具函数模块"""

import re
from datetime import datetime


def extract_date_from_filename(
    filename: str, return_string: bool = False
) -> datetime | str | None:
    """
    从文件名中提取日期
    
    支持的格式：
    - OpenPO 1.9.2026.XLSX -> datetime(2026, 1, 9) 或 "2026-01-09"
    - OpenPO 1.16.2026.XLSX -> datetime(2026, 1, 16) 或 "2026-01-16"
    
    Args:
        filename: 文件名
        return_string: 如果为 True，返回字符串格式（YYYY-MM-DD），否则返回 datetime 对象
        
    Returns:
        日期对象、日期字符串或 None
    """
    # 匹配 M.D.YYYY 格式（如 1.9.2026）
    pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"
    match = re.search(pattern, filename)
    
    if match:
        month, day, year = match.groups()
        try:
            # 验证日期有效性
            date_obj = datetime(int(year), int(month), int(day))
            if return_string:
                return date_obj.strftime("%Y-%m-%d")
            return date_obj
        except ValueError:
            return None
    
    return None
