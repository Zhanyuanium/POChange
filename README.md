# POChange - 物流周报差异分析工具

一个用于比较两个物流周报 Excel 文件并生成差异报告的 Python 工具。

## 功能特性

- 📊 自动识别两个周报中的共同行（基于 `Purchasing Document`、`Item`、`Material` 三列组合键）
- 🔍 对比 `Order Quantity` 和 `RSD` 的变化
- 📈 生成详细的差异报告，包含原始值和变化值
- ⚙️ 支持命令行参数和配置文件两种输入方式
- 🧪 完整的单元测试覆盖

## 安装

### 前置要求

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) - 快速 Python 包管理器

### 安装步骤

1. 克隆或下载项目

2. 使用 uv 安装依赖：

```bash
uv sync
```

这将自动创建虚拟环境并安装所有依赖。

## 使用方法

### 命令行参数方式

```bash
uv run python main.py --file1 "examples/OpenPO 1.9.2026.XLSX" --file2 "examples/OpenPO 1.16.2026.XLSX"
```

### 配置文件方式

1. 创建 `config.yaml` 文件：

```yaml
input_file1: "examples/OpenPO 1.9.2026.XLSX"
input_file2: "examples/OpenPO 1.16.2026.XLSX"
output_dir: "diff"
```

2. 运行程序：

```bash
uv run python main.py
```

### 参数说明

- `--file1`: 第一个周报文件路径（必需）
- `--file2`: 第二个周报文件路径（必需）
- `--output-dir`: 输出目录（默认: `diff`）
- `--output-filename`: 输出文件名（可选，默认基于日期自动生成）
- `--config`: 配置文件路径（默认: `config.yaml`）

**优先级**: 命令行参数 > 配置文件 > 默认值

## 输入文件格式

Excel 文件必须包含以下列（列名大小写不敏感）：

- `Purchasing Document` - 采购文档号
- `Item` - 项目编号
- `Material` - 物料编号
- `Order Quantity` - 订单数量（数值）
- `RSD` - 要求发货日期（日期格式）

每一行由 `Purchasing Document`、`Item`、`Material` 三列的组合作为唯一键。

## 输出文件格式

差异报告将保存为 Excel 文件，包含以下列：

### 键列
- `Purchasing Document` - 采购文档号
- `Item` - 项目编号
- `Material` - 物料编号

### 额外信息列（来自原表格的 F、H、I、J 列）
- `Vendor/Supplying Plant` - 供应商/供应工厂
- `MRP Controller` - MRP 控制器
- `Plant` - 工厂
- `Destination` - 目的地

### 差异列
- `Order Quantity (Original)` - 原始订单数量（来自第一个文件，新增订单为 0）
- `Order Quantity (Change)` - 订单数量变化（新值 - 旧值，正负数值；新增订单为新值）
- `RSD (Original)` - 原始要求发货日期（来自第一个文件，新增订单为新值）
- `RSD (Change)` - 日期变化（天数差，正负整数；新增订单为 0）

### 输出规则

1. **只记录有变化的行**：如果 `Order Quantity` 和 `RSD` 都没有变化，该行不会出现在差异报告中
2. **新增订单**：后一个周报中新增的订单（不在第一个周报中）也会被记录：
   - `Order Quantity (Original)` = 0（从无到有）
   - `Order Quantity (Change)` = 新值（实际数量）
   - `RSD (Original)` = 新值（这是它一开始的日期）
   - `RSD (Change)` = 0（无从变化）

输出文件名格式：`diff_YYYY-MM-DD_to_YYYY-MM-DD.xlsx`（基于输入文件名中的日期自动生成）

## 项目结构

```
POChange/
├── src/
│   └── pochange/
│       ├── __init__.py
│       ├── reader.py          # Excel 文件读取模块
│       ├── comparator.py      # 数据比较逻辑模块
│       ├── writer.py          # 差异报告写入模块
│       └── config.py          # 配置管理模块
├── tests/
│   ├── test_reader.py
│   ├── test_comparator.py
│   └── test_writer.py
├── main.py                    # 命令行入口
├── config.yaml               # 配置文件（可选）
├── pyproject.toml
└── README.md
```

## 运行测试

```bash
uv run pytest tests/ -v
```

## 示例

假设有两个周报文件：
- `examples/OpenPO 1.9.2026.XLSX` - 第一周的数据
- `examples/OpenPO 1.16.2026.XLSX` - 第二周的数据

运行分析：

```bash
uv run python main.py --file1 "examples/OpenPO 1.9.2026.XLSX" --file2 "examples/OpenPO 1.16.2026.XLSX"
```

程序将：
1. 读取两个周报文件
2. 找出同时出现在两个文件中的行
3. 计算 `Order Quantity` 和 `RSD` 的变化（只记录有变化的行）
4. 识别新增订单（只在第二个文件中出现的订单）
5. 生成差异报告到 `diff/diff_2026-01-09_to_2026-01-16.xlsx`，包含变更记录和新增订单

## 开发

### 添加依赖

```bash
uv add <package-name>
```

### 添加开发依赖

```bash
uv add --dev <package-name>
```

## 许可证

本项目采用 MIT 许可证。
