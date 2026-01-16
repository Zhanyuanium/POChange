"""测试 config 模块"""

import tempfile
from pathlib import Path
from datetime import datetime

from src.pochange.config import (
    find_latest_weekly_reports,
    get_config
)
from src.pochange.utils import extract_date_from_filename


def test_extract_date_from_filename():
    """测试从文件名提取日期"""
    # 正常格式
    date1 = extract_date_from_filename("OpenPO 1.9.2026.XLSX")
    assert date1 == datetime(2026, 1, 9)
    
    date2 = extract_date_from_filename("OpenPO 1.16.2026.XLSX")
    assert date2 == datetime(2026, 1, 16)
    
    # 无效格式
    date3 = extract_date_from_filename("invalid_file.xlsx")
    assert date3 is None
    
    # 无效日期
    date4 = extract_date_from_filename("OpenPO 13.32.2026.XLSX")
    assert date4 is None


def test_find_latest_weekly_reports():
    """测试查找最新的两个周报文件"""
    # 使用实际的 Weekly Reports 目录
    files = find_latest_weekly_reports(Path("Weekly Reports"))
    
    if files:
        file1, file2 = files
        # 验证返回了两个不同的文件
        assert file1 != file2
        # 验证 file1 的日期早于 file2
        date1 = extract_date_from_filename(file1.name)
        date2 = extract_date_from_filename(file2.name)
        assert date1 < date2


def test_find_latest_weekly_reports_not_enough_files():
    """测试文件不足的情况"""
    # 创建临时目录，只有一个文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # 创建一个文件
        test_file = tmp_path / "OpenPO 1.9.2026.XLSX"
        test_file.touch()
        
        result = find_latest_weekly_reports(tmp_path)
        assert result is None


def test_find_latest_weekly_reports_nonexistent_dir():
    """测试目录不存在的情况"""
    result = find_latest_weekly_reports(Path("nonexistent_directory"))
    assert result is None


def test_get_config_with_default_files(monkeypatch):
    """测试使用默认文件（需要模拟命令行参数为空）"""
    import sys
    from unittest.mock import patch
    
    # 模拟命令行参数为空
    with patch("sys.argv", ["main.py"]):
        # 模拟没有配置文件
        with patch("src.pochange.config.load_config_file", return_value={}):
            # 如果 Weekly Reports 目录存在且有文件，应该能自动找到
            config = get_config()
            assert config.input_file1 is not None
            assert config.input_file2 is not None
            assert config.output_dir == "Weekly Differences"


def test_get_config_with_explicit_files():
    """测试显式提供文件"""
    import sys
    from unittest.mock import patch
    
    with patch("sys.argv", ["main.py", "--file1", "file1.xlsx", "--file2", "file2.xlsx"]):
        with patch("src.pochange.config.load_config_file", return_value={}):
            config = get_config()
            assert config.input_file1 == "file1.xlsx"
            assert config.input_file2 == "file2.xlsx"
