"""差异报告写入模块"""

import pandas as pd
from pathlib import Path


def write_diff_report(diff_data: pd.DataFrame, output_path: str | Path) -> None:
    """
    将差异数据写入 Excel 文件
    
    Args:
        diff_data: 包含差异信息的 DataFrame
        output_path: 输出文件路径
        
    Raises:
        ValueError: 如果输出路径无效
        IOError: 如果无法写入文件
    """
    output_path = Path(output_path)
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 准备输出的 DataFrame（复制以避免修改原始数据）
    output_df = diff_data.copy()
    
    # 格式化日期列为字符串（便于 Excel 显示）
    if "RSD (Original)" in output_df.columns:
        output_df["RSD (Original)"] = output_df["RSD (Original)"].apply(
            lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else ""
        )
    
    # 确保 RSD (Change) 显示为整数（去除小数）
    if "RSD (Change)" in output_df.columns:
        output_df["RSD (Change)"] = output_df["RSD (Change)"].apply(
            lambda x: int(x) if pd.notna(x) else ""
        )
    
    # 确保 Order Quantity (Change) 显示为数值（保留小数）
    if "Order Quantity (Change)" in output_df.columns:
        output_df["Order Quantity (Change)"] = output_df["Order Quantity (Change)"].apply(
            lambda x: float(x) if pd.notna(x) else ""
        )
    
    try:
        # 写入 Excel 文件
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            output_df.to_excel(writer, index=False, sheet_name="差异报告")
            
            # 获取工作表以调整列宽
            worksheet = writer.sheets["差异报告"]
            for idx, col in enumerate(output_df.columns):
                # 设置列宽（根据列名长度和内容）
                max_length = max(
                    len(str(col)),
                    output_df[col].astype(str).map(len).max() if len(output_df) > 0 else 10,
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    except Exception as e:
        raise IOError(f"无法写入文件 {output_path}: {e}")
