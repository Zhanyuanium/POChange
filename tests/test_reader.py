"""测试 reader 模块"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.pochange.reader import (
    read_weekly_report,
    find_column_mapping,
    normalize_column_name,
)


def test_normalize_column_name():
    """测试列名标准化"""
    assert normalize_column_name("Purchasing Document") == "purchasing document"
    assert normalize_column_name("  Item  ") == "item"
    assert normalize_column_name("ORDER QUANTITY") == "order quantity"


def test_find_column_mapping():
    """测试列映射查找"""
    # 正常情况
    df = pd.DataFrame({
        "Purchasing Document": [1, 2],
        "Item": ["A", "B"],
        "Material": ["M1", "M2"],
        "Order Quantity": [10, 20],
        "RSD": ["2026-01-01", "2026-01-02"],
    })
    mapping = find_column_mapping(df)
    assert "Purchasing Document" in mapping
    assert "Item" in mapping
    assert "Material" in mapping
    assert "Order Quantity" in mapping
    assert "RSD" in mapping
    
    # 大小写不敏感
    df2 = pd.DataFrame({
        "purchasing document": [1, 2],
        "ITEM": ["A", "B"],
        "Material": ["M1", "M2"],
        "order quantity": [10, 20],
        "rsd": ["2026-01-01", "2026-01-02"],
    })
    mapping2 = find_column_mapping(df2)
    assert len(mapping2) == 5
    
    # 缺少列
    df3 = pd.DataFrame({
        "Purchasing Document": [1, 2],
        "Item": ["A", "B"],
    })
    with pytest.raises(ValueError, match="缺少必需的列"):
        find_column_mapping(df3)


def test_read_weekly_report():
    """测试读取周报文件"""
    # 创建临时 Excel 文件
    import tempfile
    fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    
    try:
        # 创建测试数据
        df = pd.DataFrame({
            "Purchasing Document": ["PO001", "PO002"],
            "Item": ["10", "20"],
            "Material": ["MAT001", "MAT002"],
            "Order Quantity": [100, 200],
            "RSD": ["2026-01-09", "2026-01-16"],
        })
        df.to_excel(tmp_path, index=False, engine="openpyxl")
        
        # 读取文件
        result = read_weekly_report(tmp_path)
        
        # 验证结果
        assert len(result) == 2
        assert "Purchasing Document" in result.columns
        assert "Item" in result.columns
        assert "Material" in result.columns
        assert "Order Quantity" in result.columns
        assert "RSD" in result.columns
        assert "_key" in result.columns
        
        # 验证键列是字符串
        assert result["Purchasing Document"].dtype == "object"
        assert result["Item"].dtype == "object"
        assert result["Material"].dtype == "object"
        
        # 验证 _key 列
        assert result["_key"].iloc[0] == "PO001|10|MAT001"
        
    finally:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass  # 忽略删除错误


def test_read_weekly_report_file_not_found():
    """测试文件不存在的情况"""
    with pytest.raises(FileNotFoundError):
        read_weekly_report("nonexistent_file.xlsx")


def test_read_weekly_report_empty_file():
    """测试空文件"""
    import tempfile
    fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    
    try:
        # 创建空 DataFrame
        df = pd.DataFrame()
        df.to_excel(tmp_path, index=False, engine="openpyxl")
        
        with pytest.raises(ValueError, match="没有找到有效数据|为空"):
            read_weekly_report(tmp_path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass  # 忽略删除错误
