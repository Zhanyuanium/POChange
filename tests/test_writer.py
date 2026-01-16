"""测试 writer 模块"""

import pandas as pd
from pathlib import Path
import tempfile
import os
from datetime import datetime

from src.pochange.writer import write_diff_report


def test_write_diff_report():
    """测试写入差异报告"""
    # 创建测试数据
    diff_data = pd.DataFrame({
        "Purchasing Document": ["PO001", "PO002"],
        "Item": ["10", "20"],
        "Material": ["MAT001", "MAT002"],
        "Order Quantity (Original)": [100, 200],
        "Order Quantity (Change)": [50, -20],
        "RSD (Original)": [datetime(2026, 1, 9), datetime(2026, 1, 9)],
        "RSD (Change)": [7, 7],
    })
    
    # 创建临时输出文件
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 写入文件
        write_diff_report(diff_data, tmp_path)
        
        # 验证文件存在
        assert os.path.exists(tmp_path)
        
        # 读取并验证内容
        result = pd.read_excel(tmp_path, engine="openpyxl")
        assert len(result) == 2
        assert "Purchasing Document" in result.columns
        assert "Order Quantity (Original)" in result.columns
        assert "Order Quantity (Change)" in result.columns
        assert "RSD (Original)" in result.columns
        assert "RSD (Change)" in result.columns
        
        # 验证数据
        assert result.iloc[0]["Purchasing Document"] == "PO001"
        assert result.iloc[0]["Order Quantity (Change)"] == 50
        assert result.iloc[0]["RSD (Change)"] == 7
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_write_diff_report_creates_directory():
    """测试自动创建输出目录"""
    diff_data = pd.DataFrame({
        "Purchasing Document": ["PO001"],
        "Item": ["10"],
        "Material": ["MAT001"],
        "Order Quantity (Original)": [100],
        "Order Quantity (Change)": [50],
        "RSD (Original)": [datetime(2026, 1, 9)],
        "RSD (Change)": [7],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "subdir" / "output.xlsx"
        
        # 写入文件（应该自动创建 subdir 目录）
        write_diff_report(diff_data, output_path)
        
        # 验证文件存在
        assert output_path.exists()


def test_write_diff_report_empty_data():
    """测试写入空数据"""
    diff_data = pd.DataFrame(columns=[
        "Purchasing Document",
        "Item",
        "Material",
        "Order Quantity (Original)",
        "Order Quantity (Change)",
        "RSD (Original)",
        "RSD (Change)",
    ])
    
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # 应该能正常写入空 DataFrame
        write_diff_report(diff_data, tmp_path)
        assert os.path.exists(tmp_path)
        
        # 读取验证
        result = pd.read_excel(tmp_path, engine="openpyxl")
        assert len(result) == 0
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
