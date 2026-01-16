"""测试 comparator 模块"""

import pytest
import pandas as pd
from datetime import datetime

from src.pochange.comparator import (
    find_common_rows,
    calculate_differences,
    find_new_orders,
)


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
    """测试计算差异（只记录有变化的行）"""
    date1 = datetime(2026, 1, 9)
    date2 = datetime(2026, 1, 16)
    
    df1 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002", "PO003|30|MAT003"],
        "Purchasing Document": ["PO001", "PO002", "PO003"],
        "Item": ["10", "20", "30"],
        "Material": ["MAT001", "MAT002", "MAT003"],
        "Order Quantity": [100, 200, 300],
        "RSD": [date1, date1, date1],
        "Vendor/Supplying Plant": ["V001", "V002", "V003"],
        "MRP Controller": ["C1", "C2", "C3"],
        "Plant": ["P1", "P2", "P3"],
        "Destination": ["D1", "D2", "D3"],
    })
    
    df2 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002", "PO003|30|MAT003"],
        "Purchasing Document": ["PO001", "PO002", "PO003"],
        "Item": ["10", "20", "30"],
        "Material": ["MAT001", "MAT002", "MAT003"],
        "Order Quantity": [150, 200, 300],  # +50, 0, 0
        "RSD": [date2, date1, date2],  # +7 天, 0, +7 天
        "Vendor/Supplying Plant": ["V001", "V002", "V003"],
        "MRP Controller": ["C1", "C2", "C3"],
        "Plant": ["P1", "P2", "P3"],
        "Destination": ["D1", "D2", "D3"],
    })
    
    common_keys = pd.Index(["PO001|10|MAT001", "PO002|20|MAT002", "PO003|30|MAT003"])
    diff_data = calculate_differences(df1, df2, common_keys)
    
    # 应该只有2行（PO001和PO003有变化，PO002无变化被过滤）
    assert len(diff_data) == 2
    assert "Purchasing Document" in diff_data.columns
    assert "Item" in diff_data.columns
    assert "Material" in diff_data.columns
    assert "Vendor/Supplying Plant" in diff_data.columns
    assert "MRP Controller" in diff_data.columns
    assert "Plant" in diff_data.columns
    assert "Destination" in diff_data.columns
    assert "Order Quantity (Original)" in diff_data.columns
    assert "Order Quantity (Change)" in diff_data.columns
    assert "RSD (Original)" in diff_data.columns
    assert "RSD (Change)" in diff_data.columns
    
    # 验证第一行（PO001）的差异
    assert diff_data.iloc[0]["Order Quantity (Original)"] == 100
    assert diff_data.iloc[0]["Order Quantity (Change)"] == 50
    assert diff_data.iloc[0]["RSD (Change)"] == 7
    
    # 验证第二行（PO003）的差异
    assert diff_data.iloc[1]["Order Quantity (Original)"] == 300
    assert diff_data.iloc[1]["Order Quantity (Change)"] == 0
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


def test_calculate_differences_no_changes():
    """测试没有变化的情况（应该返回空DataFrame）"""
    date1 = datetime(2026, 1, 9)
    
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
        "Order Quantity": [100, 200],  # 无变化
        "RSD": [date1, date1],  # 无变化
    })
    
    common_keys = pd.Index(["PO001|10|MAT001", "PO002|20|MAT002"])
    diff_data = calculate_differences(df1, df2, common_keys)
    
    # 应该返回空DataFrame（所有行都没有变化）
    assert len(diff_data) == 0


def test_find_new_orders():
    """测试查找新增订单"""
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
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002", "PO003|30|MAT003", "PO004|40|MAT004"],
        "Purchasing Document": ["PO001", "PO002", "PO003", "PO004"],
        "Item": ["10", "20", "30", "40"],
        "Material": ["MAT001", "MAT002", "MAT003", "MAT004"],
        "Order Quantity": [100, 200, 150, 250],
        "RSD": [date1, date1, date2, date2],
        "Vendor/Supplying Plant": ["V001", "V002", "V003", "V004"],
        "MRP Controller": ["C1", "C2", "C3", "C4"],
        "Plant": ["P1", "P2", "P3", "P4"],
        "Destination": ["D1", "D2", "D3", "D4"],
    })
    
    new_orders = find_new_orders(df1, df2)
    
    # 应该找到2个新增订单（PO003和PO004）
    assert len(new_orders) == 2
    assert "Purchasing Document" in new_orders.columns
    assert "Item" in new_orders.columns
    assert "Material" in new_orders.columns
    assert "Vendor/Supplying Plant" in new_orders.columns
    assert "MRP Controller" in new_orders.columns
    assert "Plant" in new_orders.columns
    assert "Destination" in new_orders.columns
    assert "Order Quantity (Original)" in new_orders.columns
    assert "Order Quantity (Change)" in new_orders.columns
    assert "RSD (Original)" in new_orders.columns
    assert "RSD (Change)" in new_orders.columns
    
    # 验证新增订单的数据
    # Order Quantity: 原始值=0, 变更值=新值
    assert new_orders["Order Quantity (Original)"].iloc[0] == 0
    assert new_orders["Order Quantity (Change)"].iloc[0] == 150
    # RSD: 原始值=新值, 变更值=0
    assert new_orders["RSD (Original)"].iloc[0] == date2
    assert new_orders["RSD (Change)"].iloc[0] == 0


def test_find_new_orders_no_new():
    """测试没有新增订单的情况"""
    df1 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002"],
        "Purchasing Document": ["PO001", "PO002"],
        "Item": ["10", "20"],
        "Material": ["MAT001", "MAT002"],
    })
    
    df2 = pd.DataFrame({
        "_key": ["PO001|10|MAT001", "PO002|20|MAT002"],
        "Purchasing Document": ["PO001", "PO002"],
        "Item": ["10", "20"],
        "Material": ["MAT001", "MAT002"],
    })
    
    new_orders = find_new_orders(df1, df2)
    
    assert len(new_orders) == 0
    assert "Purchasing Document" in new_orders.columns
