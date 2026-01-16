"""测试 comparator 模块"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from src.pochange.comparator import find_common_rows, calculate_differences


def test_find_common_rows():
    """测试查找共同行"""
    df1 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002", "PO003|30|MAT003"],
        "Purchasing Document": ["PO001", "PO002", "PO003"],
        "Item": ["10", "20", "30"],
        "Material": ["MAT001", "MAT002", "MAT003"],
    })
    
    df2 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002", "PO004|40|MAT004"],
        "Purchasing Document": ["PO001", "PO002", "PO004"],
        "Item": ["10", "20", "40"],
        "Material": ["MAT001", "MAT002", "MAT004"],
    })
    
    common_keys = find_common_rows(df1, df2)
    
    assert len(common_keys) == 2
    assert "PO001|10|MAT001" in common_keys
    assert "PO002|20|MAT002" in common_keys
    assert "PO003|30|MAT003" not in common_keys
    assert "PO004|40|MAT004" not in common_keys


def test_find_common_rows_no_common():
    """测试没有共同行的情况"""
    df1 = pd.DataFrame({
        "_key": ["PO001|10|MAT001"],
        "Purchasing Document": ["PO001"],
        "Item": ["10"],
        "Material": ["MAT001"],
    })
    
    df2 = pd.DataFrame({
        "_key": ["PO002|20|MAT002"],
        "Purchasing Document": ["PO002"],
        "Item": ["20"],
        "Material": ["MAT002"],
    })
    
    common_keys = find_common_rows(df1, df2)
    assert len(common_keys) == 0


def test_find_common_rows_missing_key_column():
    """测试缺少 _key 列的情况"""
    df1 = pd.DataFrame({"col1": [1, 2]})
    df2 = pd.DataFrame({"col1": [1, 2]})
    
    with pytest.raises(ValueError, match="_key"):
        find_common_rows(df1, df2)


def test_calculate_differences():
    """测试计算差异"""
    date1 = datetime(2026, 1, 9)
    date2 = datetime(2026, 1, 16)
    
    df1 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002"],
        "Purchasing Document": ["PO001", "PO002"],
        "Item": ["10", "20"],
        "Material": ["MAT001", "MAT002"],
        "Order Quantity": [100, 200],
        "RSD": [date1, date1],
    })
    
    df2 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002"],
        "Purchasing Document": ["PO001", "PO002"],
        "Item": ["10", "20"],
        "Material": ["MAT001", "MAT002"],
        "Order Quantity": [150, 180],  # +50, -20
        "RSD": [date2, date2],  # +7 天, +7 天
    })
    
    common_keys = pd.Index(["PO001|10|MAT001", "PO002|20|MAT002"])
    diff_data = calculate_differences(df1, df2, common_keys)
    
    assert len(diff_data) == 2
    assert "Purchasing Document" in diff_data.columns
    assert "Item" in diff_data.columns
    assert "Material" in diff_data.columns
    assert "Order Quantity (Original)" in diff_data.columns
    assert "Order Quantity (Change)" in diff_data.columns
    assert "RSD (Original)" in diff_data.columns
    assert "RSD (Change)" in diff_data.columns
    
    # 验证第一行的差异
    assert diff_data.iloc[0]["Order Quantity (Original)"] == 100
    assert diff_data.iloc[0]["Order Quantity (Change)"] == 50
    assert diff_data.iloc[0]["RSD (Change)"] == 7
    
    # 验证第二行的差异
    assert diff_data.iloc[1]["Order Quantity (Original)"] == 200
    assert diff_data.iloc[1]["Order Quantity (Change)"] == -20
    assert diff_data.iloc[1]["RSD (Change)"] == 7


def test_calculate_differences_no_common():
    """测试没有共同行的情况"""
    df1 = pd.DataFrame({
        "_key": ["PO001|10|MAT001"],
        "Purchasing Document": ["PO001"],
        "Item": ["10"],
        "Material": ["MAT001"],
        "Order Quantity": [100],
        "RSD": [datetime(2026, 1, 9)],
    })
    
    df2 = pd.DataFrame({
        "_key": ["PO002|20|MAT002"],
        "Purchasing Document": ["PO002"],
        "Item": ["20"],
        "Material": ["MAT002"],
        "Order Quantity": [200],
        "RSD": [datetime(2026, 1, 16)],
    })
    
    common_keys = pd.Index([])
    diff_data = calculate_differences(df1, df2, common_keys)
    
    assert len(diff_data) == 0
    assert "Purchasing Document" in diff_data.columns
    assert "Order Quantity (Change)" in diff_data.columns
    assert "RSD (Change)" in diff_data.columns
