"""主程序入口"""

import re
import sys
from pathlib import Path
from datetime import datetime

from src.pochange.reader import read_weekly_report
from src.pochange.comparator import find_common_rows, calculate_differences
from src.pochange.writer import write_diff_report
from src.pochange.config import get_config, Config


def extract_date_from_filename(filename: str) -> str | None:
    """
    从文件名中提取日期
    
    支持的格式：
    - OpenPO 1.9.2026.XLSX -> 2026-01-09
    - OpenPO 1.16.2026.XLSX -> 2026-01-16
    
    Args:
        filename: 文件名
        
    Returns:
        日期字符串（YYYY-MM-DD）或 None
    """
    # 匹配 M.D.YYYY 格式（如 1.9.2026）
    pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"
    match = re.search(pattern, filename)
    
    if match:
        month, day, year = match.groups()
        try:
            # 验证日期有效性
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None
    
    return None


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
    date1 = extract_date_from_filename(Path(file1).name)
    date2 = extract_date_from_filename(Path(file2).name)
    
    if date1 and date2:
        return f"diff_{date1}_to_{date2}.xlsx"
    else:
        # 如果无法提取日期，使用时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"diff_{timestamp}.xlsx"


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
        
        # 计算差异
        print("计算差异...")
        diff_data = calculate_differences(df1, df2, common_keys)
        
        # 生成输出路径
        output_filename = generate_output_filename(
            config.input_file1, config.input_file2, config
        )
        output_path = Path(config.output_dir) / output_filename
        
        # 写入差异报告
        print(f"写入差异报告: {output_path}")
        write_diff_report(diff_data, output_path)
        
        print(f"完成! 差异报告已保存到: {output_path}")
        print(f"  共 {len(diff_data)} 条差异记录")
        
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
