"""主程序入口"""

import sys
from pathlib import Path
import pandas as pd

from src.pochange.reader import read_weekly_report
from src.pochange.comparator import (
    find_common_rows,
    calculate_differences,
    find_new_orders,
)
from src.pochange.writer import write_diff_report
from src.pochange.config import get_config, Config
from src.pochange.utils import extract_date_from_filename


def generate_output_filename(file1: str, file2: str, config: Config) -> str:
    """
    生成输出文件名
    
    Args:
        file1: 第一个文件路径
        file2: 第二个文件路径
        config: 配置对象
        
    Returns:
        输出文件名
    """
    if config.output_filename:
        return config.output_filename
    
    # 尝试从文件名提取日期
    date1 = extract_date_from_filename(Path(file1).name, return_string=True)
    date2 = extract_date_from_filename(Path(file2).name, return_string=True)
    
    if date1 and date2:
        return f"Diff {date1} to {date2}.xlsx"
    else:
        raise ValueError(
            f"无法从文件名中提取日期: '{Path(file1).name}' 或 '{Path(file2).name}'，无法生成输出文件名。"
        )


def main():
    """主函数"""
    try:
        # 获取配置
        config = get_config()
        
        print(f"读取第一个周报: {config.input_file1}")
        df1 = read_weekly_report(config.input_file1)
        print(f"  读取到 {len(df1)} 行数据")
        
        print(f"读取第二个周报: {config.input_file2}")
        df2 = read_weekly_report(config.input_file2)
        print(f"  读取到 {len(df2)} 行数据")
        
        # 找出共同行
        print("查找共同行...")
        common_keys = find_common_rows(df1, df2)
        print(f"  找到 {len(common_keys)} 个共同行")
        
        if len(common_keys) == 0:
            print("警告: 没有找到共同行，将生成空的差异报告")
        
        # 计算差异（只记录有变化的行）
        print("计算差异...")
        diff_data = calculate_differences(df1, df2, common_keys)
        print(f"  找到 {len(diff_data)} 行有变化的记录")
        
        # 查找新增订单
        print("查找新增订单...")
        new_orders = find_new_orders(df1, df2)
        print(f"  找到 {len(new_orders)} 个新增订单")
        
        # 合并差异数据和新增订单
        if len(new_orders) > 0:
            diff_data = pd.concat([diff_data, new_orders], ignore_index=True)
        else:
            new_orders = pd.DataFrame()  # 确保变量已定义
        
        # 生成输出路径
        output_filename = generate_output_filename(
            config.input_file1, config.input_file2, config
        )
        output_path = Path(config.output_dir) / output_filename
        
        # 写入差异报告
        print(f"写入差异报告: {output_path}")
        write_diff_report(diff_data, output_path)
        
        print(f"完成! 差异报告已保存到: {output_path}")
        print(f"  共 {len(diff_data)} 条记录（{len(diff_data) - len(new_orders)} 条变更记录，{len(new_orders)} 条新增订单）")
        
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未预期的错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
