"""Excel 文件读取模块"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


# 必需的列名（支持大小写变化）
REQUIRED_COLUMNS = {
    "purchasing document": "Purchasing Document",
    "item": "Item",
    "material": "Material",
    "order quantity": "Order Quantity",
    "rsd": "RSD",
}

# 键列（用于唯一标识一行）
KEY_COLUMNS = ["Purchasing Document", "Item", "Material"]


def normalize_column_name(col: str) -> str:
    """标准化列名（去除空格，转为小写）"""
    return col.strip().lower()


def find_column_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """
    查找并映射列名
    
    Args:
        df: 输入的 DataFrame
        
    Returns:
        映射字典：{标准化列名: 原始列名}
        
    Raises:
        ValueError: 如果缺少必需的列
    """
    normalized_to_original = {}
    df_columns_normalized = {normalize_column_name(col): col for col in df.columns}
    
    missing_columns = []
    for normalized_name, standard_name in REQUIRED_COLUMNS.items():
        if normalized_name not in df_columns_normalized:
            missing_columns.append(standard_name)
        else:
            normalized_to_original[standard_name] = df_columns_normalized[normalized_name]
    
    if missing_columns:
        raise ValueError(
            f"缺少必需的列: {', '.join(missing_columns)}. "
            f"可用列: {', '.join(df.columns.tolist())}"
        )
    
    return normalized_to_original


def find_header_row(file_path: Path, sheet_name: str = None, max_rows_to_check: int = 20) -> int:
    """
    查找包含所需列名的表头行
    
    Args:
        file_path: Excel 文件路径
        sheet_name: 工作表名称（可选）
        max_rows_to_check: 最多检查的行数
        
    Returns:
        表头行号（0-based），如果找不到则返回 None
    """
    try:
        # 读取前几行，不设置表头
        kwargs = {"engine": "openpyxl", "header": None, "nrows": max_rows_to_check}
        if sheet_name:
            kwargs["sheet_name"] = sheet_name
        df_temp = pd.read_excel(file_path, **kwargs)
        
        # 检查每一行是否包含所需的列名
        required_cols_lower = [col.lower() for col in REQUIRED_COLUMNS.keys()]
        
        for row_idx in range(max_rows_to_check):
            if row_idx >= len(df_temp):
                break
            
            row_values = [str(val).strip().lower() if pd.notna(val) else "" for val in df_temp.iloc[row_idx].values]
            
            # 检查这一行是否包含所有必需的列名
            found_cols = 0
            for req_col in required_cols_lower:
                if any(req_col in val for val in row_values):
                    found_cols += 1
            
            # 如果找到至少3个必需的列，认为这是表头行
            if found_cols >= 3:
                return row_idx
        
        return None
    except Exception:
        return None


def is_valid_data_row(row: pd.Series, purchasing_doc_col: str) -> bool:
    """
    检查一行是否是有效的数据行
    
    Args:
        row: DataFrame 的一行
        purchasing_doc_col: Purchasing Document 列名
        
    Returns:
        是否是有效数据行
    """
    if purchasing_doc_col not in row.index:
        return False
    
    value = row[purchasing_doc_col]
    
    # 检查是否是 NaN
    if pd.isna(value):
        return False
    
    # 转换为字符串并检查
    value_str = str(value).strip()
    
    # 排除说明文字
    invalid_texts = [
        "compare columns",
        "purchasing document",
        "item",
        "materials",
        "result:",
        "order quantity",
        "rsd",
        "shipping",
        "new po",
        "po deleted",
        "vlookup",
        "create new column",
        "destnation",
        "new file not yet delivered",
    ]
    value_lower = value_str.lower()
    if any(invalid in value_lower for invalid in invalid_texts):
        return False
    
    # 排除 "nan" 字符串
    if value_lower == "nan":
        return False
    
    # 如果值太短（少于3个字符），可能是无效数据
    if len(value_str) < 3:
        return False
    
    # 允许数字或包含字母数字的值（如 "PO001" 或 "6102095255"）
    # 只要不是说明文字，就认为是有效数据
    return True


def read_weekly_report(file_path: str | Path) -> pd.DataFrame:
    """
    读取周报 Excel 文件
    
    Args:
        file_path: Excel 文件路径
        
    Returns:
        处理后的 DataFrame，包含标准化的列名和数据类型
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 列缺失或数据格式错误
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 获取所有工作表名称
    try:
        excel_file = pd.ExcelFile(file_path, engine="openpyxl")
        sheet_names = excel_file.sheet_names
    except Exception as e:
        raise ValueError(f"无法打开 Excel 文件 {file_path}: {e}")
    
    # 尝试每个工作表，找到包含有效数据的工作表
    df = None
    last_error = None
    
    for sheet_name in sheet_names:
        try:
            # 尝试找到表头行
            header_row = find_header_row(file_path, sheet_name=sheet_name)
            
            # 读取 Excel 文件
            if header_row is not None:
                df_temp = pd.read_excel(
                    file_path, engine="openpyxl", sheet_name=sheet_name, header=header_row
                )
            else:
                # 尝试默认方式（header=0）
                df_temp = pd.read_excel(
                    file_path, engine="openpyxl", sheet_name=sheet_name
                )
            
            if df_temp.empty:
                continue
            
            # 查找列映射
            try:
                column_mapping = find_column_mapping(df_temp)
            except ValueError:
                # 这个工作表没有所需的列，尝试下一个
                continue
            
            # 重命名列为标准名称
            df_temp = df_temp.rename(columns={v: k for k, v in column_mapping.items()})
            
            # 删除所有列都是 NaN 的行
            df_temp = df_temp.dropna(how="all")
            
            # 过滤有效数据行（Purchasing Document 应该是数字）
            purchasing_doc_col = "Purchasing Document"
            if purchasing_doc_col in df_temp.columns:
                # 创建掩码，标记有效行
                valid_mask = df_temp.apply(
                    lambda row: is_valid_data_row(row, purchasing_doc_col), axis=1
                )
                df_temp = df_temp[valid_mask]
            
            # 如果过滤后还有数据，使用这个工作表
            if len(df_temp) > 0:
                df = df_temp
                break
        except Exception as e:
            last_error = e
            continue
    
    if df is None or df.empty:
        if last_error:
            raise ValueError(f"无法读取有效的 Excel 数据 {file_path}: {last_error}")
        else:
            raise ValueError(f"文件 {file_path} 中没有找到有效数据")
    
    # 确保键列为字符串类型（用于匹配）
    for col in KEY_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # 确保 Order Quantity 为数值类型
    if "Order Quantity" in df.columns:
        df["Order Quantity"] = pd.to_numeric(
            df["Order Quantity"], errors="coerce"
        )
    
    # 确保 RSD 为日期类型
    if "RSD" in df.columns:
        df["RSD"] = pd.to_datetime(df["RSD"], errors="coerce")
    
    # 删除键列中有 NaN 的行（无效数据）
    df = df.dropna(subset=KEY_COLUMNS)
    
    # 再次过滤：确保 Purchasing Document 不是 "nan" 字符串
    if "Purchasing Document" in df.columns:
        df = df[df["Purchasing Document"].str.lower() != "nan"]
        df = df[~df["Purchasing Document"].str.contains("nan", case=False, na=False)]
    
    # 创建组合键列（用于后续匹配）
    df["_key"] = (
        df["Purchasing Document"].astype(str) + "|"
        + df["Item"].astype(str) + "|"
        + df["Material"].astype(str)
    )
    
    return df
