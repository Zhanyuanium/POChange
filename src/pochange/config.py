"""配置管理模块"""

import argparse
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple

from src.pochange.utils import extract_date_from_filename


@dataclass
class Config:
    """配置数据类"""
    input_file1: str
    input_file2: str
    output_dir: str = "Weekly Differences"
    output_filename: Optional[str] = None


def load_config_file(config_path: str | Path) -> dict:
    """
    从 YAML 配置文件加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典，如果文件不存在则返回空字典
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config if config else {}
    except Exception as e:
        print(f"警告: 无法读取配置文件 {config_path}: {e}")
        return {}


def find_latest_weekly_reports(search_dir: Path = None) -> Tuple[Path, Path] | None:
    """
    在指定目录中查找最新的两个周报文件
    
    Args:
        search_dir: 搜索目录，如果为 None 则使用程序所在路径的 Weekly Reports 目录
        
    Returns:
        元组 (file1, file2)，file1 是较旧的，file2 是较新的。如果找不到则返回 None
    """
    if search_dir is None:
        # 使用程序所在路径的 Weekly Reports 目录
        # main.py 所在目录的 Weekly Reports 子目录
        script_dir = Path.cwd()
        search_dir = script_dir / "Weekly Reports"
    
    search_dir = Path(search_dir)
    
    if not search_dir.exists() or not search_dir.is_dir():
        return None
    
    # 查找所有 Excel 文件
    excel_files = []
    for ext in ["*.xlsx", "*.XLSX", "*.xls", "*.XLS"]:
        excel_files.extend(search_dir.glob(ext))
    
    # 过滤掉临时文件（以 ~$ 开头的文件）
    excel_files = [f for f in excel_files if not f.name.startswith("~$")]
    
    # 去重（使用绝对路径）
    excel_files = list({f.resolve(): f for f in excel_files}.values())
    
    if len(excel_files) < 2:
        return None
    
    # 提取每个文件的日期并排序
    files_with_dates = []
    for file_path in excel_files:
        date = extract_date_from_filename(file_path.name)
        if date is not None:
            files_with_dates.append((date, file_path))
    
    if len(files_with_dates) < 2:
        return None
    
    # 按日期排序（最新的在前）
    files_with_dates.sort(key=lambda x: x[0], reverse=True)
    
    # 返回最新的两个文件（较旧的在前，较新的在后）
    file2 = files_with_dates[0][1]  # 最新的
    file1 = files_with_dates[1][1]  # 第二新的
    
    return (file1, file2)


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数
    
    Returns:
        解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        description="物流周报差异分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--file1",
        type=str,
        help="第一个周报文件路径",
    )
    
    parser.add_argument(
        "--file2",
        type=str,
        help="第二个周报文件路径",
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="输出目录（默认: Weekly Differences）",
    )
    
    parser.add_argument(
        "--output-filename",
        type=str,
        help="输出文件名（可选，默认基于日期生成）",
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径（默认: config.yaml）",
    )
    
    return parser.parse_args()


def get_config() -> Config:
    """
    获取配置（优先级：命令行参数 > 配置文件 > 默认值）
    
    Returns:
        Config 对象
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载配置文件
    config_file = load_config_file(args.config)
    
    # 确定各个配置项的值
    input_file1 = (
        args.file1
        or config_file.get("input_file1")
        or config_file.get("inputFile1")
    )
    
    input_file2 = (
        args.file2
        or config_file.get("input_file2")
        or config_file.get("inputFile2")
    )
    
    output_dir = (
        args.output_dir
        or config_file.get("output_dir")
        or config_file.get("outputDir")
        or "Weekly Differences"
    )
    
    output_filename = (
        args.output_filename
        or config_file.get("output_filename")
        or config_file.get("outputFilename")
    )
    
    # 如果没有提供文件，尝试查找最新的两个周报文件
    if not input_file1 or not input_file2:
        latest_files = find_latest_weekly_reports()
        if latest_files:
            file1, file2 = latest_files
            if not input_file1:
                input_file1 = str(file1)
            if not input_file2:
                input_file2 = str(file2)
        else:
            # 如果找不到默认文件，仍然需要报错
            if not input_file1:
                raise ValueError(
                    "必须提供 input_file1（通过命令行参数 --file1、配置文件或自动查找 Weekly Reports 目录）"
                )
            if not input_file2:
                raise ValueError(
                    "必须提供 input_file2（通过命令行参数 --file2、配置文件或自动查找 Weekly Reports 目录）"
                )
    
    return Config(
        input_file1=input_file1,
        input_file2=input_file2,
        output_dir=output_dir,
        output_filename=output_filename,
    )
