"""测试 utils 模块"""

from datetime import datetime

from src.pochange.utils import extract_date_from_filename


def test_extract_date_from_filename_datetime():
    """测试从文件名提取日期（返回 datetime 对象）"""
    # 正常格式
    date1 = extract_date_from_filename("OpenPO 1.9.2026.XLSX")
    assert isinstance(date1, datetime)
    assert date1 == datetime(2026, 1, 9)
    
    date2 = extract_date_from_filename("OpenPO 1.16.2026.XLSX")
    assert isinstance(date2, datetime)
    assert date2 == datetime(2026, 1, 16)
    
    # 无效格式
    date3 = extract_date_from_filename("invalid_file.xlsx")
    assert date3 is None
    
    # 无效日期
    date4 = extract_date_from_filename("OpenPO 13.32.2026.XLSX")
    assert date4 is None


def test_extract_date_from_filename_string():
    """测试从文件名提取日期（返回字符串）"""
    # 正常格式
    date1 = extract_date_from_filename("OpenPO 1.9.2026.XLSX", return_string=True)
    assert isinstance(date1, str)
    assert date1 == "2026-01-09"
    
    date2 = extract_date_from_filename("OpenPO 1.16.2026.XLSX", return_string=True)
    assert isinstance(date2, str)
    assert date2 == "2026-01-16"
    
    # 无效格式
    date3 = extract_date_from_filename("invalid_file.xlsx", return_string=True)
    assert date3 is None
    
    # 无效日期
    date4 = extract_date_from_filename("OpenPO 13.32.2026.XLSX", return_string=True)
    assert date4 is None
