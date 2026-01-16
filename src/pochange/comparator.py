"""数据比较模块"""

import pandas as pd
from typing import Dict, List, Tuple
import numpy as np


def find_common_rows(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.Index:
    """
    找出两个 DataFrame 中的共同行（基于组合键）
    
    Args:
        df1: 第一个周报的 DataFrame（必须包含 _key 列）
        df2: 第二个周报的 DataFrame（必须包含 _key 列）
        
    Returns:
        共同键的 Index
    """
    if "_key" not in df1.columns or "_key" not in df2.columns:
        raise ValueError("DataFrame 必须包含 _key 列（由 reader 模块创建）")
    
    keys1 = set(df1["_key"].values)
    keys2 = set(df2["_key"].values)
    common_keys = keys1 & keys2
    
    return pd.Index(list(common_keys))


def calculate_differences(
    df1: pd.DataFrame, df2: pd.DataFrame, common_keys: pd.Index
) -> pd.DataFrame:
    """
    计算共同行的差异
    
    Args:
        df1: 第一个周报的 DataFrame（旧数据）
        df2: 第二个周报的 DataFrame（新数据）
        common_keys: 共同键的 Index
        
    Returns:
        包含差异信息的 DataFrame，列包括：
        - Purchasing Document, Item, Material (键列)
        - Order Quantity (Original): 原始值（来自 df1）
        - Order Quantity (Change): 变化值（df2 - df1）
        - RSD (Original): 原始日期（来自 df1）
        - RSD (Change): 天数差（df2 - df1，整数）
    """
    if len(common_keys) == 0:
        # 返回空的 DataFrame，但包含正确的列结构
        return pd.DataFrame(
            columns=[
                "Purchasing Document",
                "Item",
                "Material",
                "Order Quantity (Original)",
                "Order Quantity (Change)",
                "RSD (Original)",
                "RSD (Change)",
            ]
        )
    
    # 筛选共同行
    df1_common = df1[df1["_key"].isin(common_keys)].copy()
    df2_common = df2[df2["_key"].isin(common_keys)].copy()
    
    # 设置 _key 为索引以便对齐
    df1_common = df1_common.set_index("_key")
    df2_common = df2_common.set_index("_key")
    
    # 确保索引顺序一致
    df1_common = df1_common.reindex(common_keys)
    df2_common = df2_common.reindex(common_keys)
    
    # 构建结果 DataFrame
    result = pd.DataFrame(index=common_keys)
    
    # 键列（从 df1 获取）
    result["Purchasing Document"] = df1_common["Purchasing Document"]
    result["Item"] = df1_common["Item"]
    result["Material"] = df1_common["Material"]
    
    # Order Quantity 原始值和变化
    result["Order Quantity (Original)"] = df1_common["Order Quantity"]
    result["Order Quantity (Change)"] = (
        df2_common["Order Quantity"] - df1_common["Order Quantity"]
    )
    
    # RSD 原始值和变化（天数差）
    result["RSD (Original)"] = df1_common["RSD"]
    
    # 计算天数差
    rsd_diff = df2_common["RSD"] - df1_common["RSD"]
    # 转换为天数（整数）
    result["RSD (Change)"] = rsd_diff.apply(
        lambda x: x.days if pd.notna(x) and hasattr(x, "days") else np.nan
    )
    result["RSD (Change)"] = result["RSD (Change)"].astype("Int64")  # 可空整数类型
    
    # 重置索引
    result = result.reset_index(drop=True)
    
    return result
