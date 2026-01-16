"""配置管理模块"""

import argparse
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """配置数据类"""
    input_file1: str
    input_file2: str
    output_dir: str = "diff"
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
        help="输出目录（默认: diff）",
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
        or "diff"
    )
    
    output_filename = (
        args.output_filename
        or config_file.get("output_filename")
        or config_file.get("outputFilename")
    )
    
    # 验证必需参数
    if not input_file1:
        raise ValueError("必须提供 input_file1（通过命令行参数 --file1 或配置文件）")
    if not input_file2:
        raise ValueError("必须提供 input_file2（通过命令行参数 --file2 或配置文件）")
    
    return Config(
        input_file1=input_file1,
        input_file2=input_file2,
        output_dir=output_dir,
        output_filename=output_filename,
    )
