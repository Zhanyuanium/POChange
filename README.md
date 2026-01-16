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

### 默认方式（推荐）

如果不提供任何参数，程序会自动在 `Weekly Reports` 目录中查找最新的两个周报文件（按文件名中的日期排序）：

```bash
uv run python main.py
```

程序会自动：
- 在 `Weekly Reports` 目录中查找所有 Excel 文件（.xlsx, .XLSX, .xls, .XLS）
- 从文件名中提取日期（支持格式：`OpenPO M.D.YYYY.XLSX`）
- 选择最新的两个文件（较旧的作为 file1，较新的作为 file2）

### 命令行参数方式

如果需要指定特定的文件：

```bash
uv run python main.py --file1 "Weekly Reports/OpenPO 1.9.2026.XLSX" --file2 "Weekly Reports/OpenPO 1.16.2026.XLSX"
```

### 配置文件方式

1. 创建 `config.yaml` 文件：

```yaml
input_file1: "Weekly Reports/OpenPO 1.9.2026.XLSX"
input_file2: "Weekly Reports/OpenPO 1.16.2026.XLSX"
output_dir: "Weekly Differences"
```

2. 运行程序：

```bash
uv run python main.py
```

### 参数说明

- `--file1`: 第一个周报文件路径（可选，未提供时自动查找）
- `--file2`: 第二个周报文件路径（可选，未提供时自动查找）
- `--output-dir`: 输出目录（默认: `Weekly Differences`）
- `--output-filename`: 输出文件名（可选，默认基于日期自动生成）
- `--config`: 配置文件路径（默认: `config.yaml`）

**优先级**: 命令行参数 > 配置文件 > 自动查找最新文件

**注意**: 如果使用自动查找功能，请确保 `Weekly Reports` 目录中至少有两个包含有效日期的 Excel 文件。

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
- `Weekly Reports/OpenPO 1.9.2026.XLSX` - 第一周的数据
- `Weekly Reports/OpenPO 1.16.2026.XLSX` - 第二周的数据

运行分析：

```bash
uv run python main.py --file1 "Weekly Reports/OpenPO 1.9.2026.XLSX" --file2 "Weekly Reports/OpenPO 1.16.2026.XLSX"
```

程序将：
1. 读取两个周报文件
2. 找出同时出现在两个文件中的行
3. 计算 `Order Quantity` 和 `RSD` 的变化（只记录有变化的行）
4. 识别新增订单（只在第二个文件中出现的订单）
5. 生成差异报告到 `Weekly Differences/Diff 2026-01-09 to 2026-01-16.xlsx`，包含变更记录和新增订单

## 开发

### 添加依赖

```bash
uv add <package-name>
```

### 添加开发依赖

```bash
uv add --dev <package-name>
```

## 编译为二进制程序

本项目支持使用 [Nuitka](https://nuitka.net/) 将 Python 代码编译为独立的可执行文件。

### 前置要求

- Python >= 3.10
- 已安装项目依赖（包括开发依赖）

### 编译步骤

1. 确保已安装开发依赖（包括 Nuitka）：

```bash
uv sync
```

2. 在 Windows 下编译为单文件可执行程序：

```bash
nuitka --mode=onefile --output-filename=POChange.exe main.py
```

这将在当前目录生成 `POChange.exe` 文件，该文件包含了所有依赖，可以在没有安装 Python 的 Windows 系统上直接运行。

### 编译选项说明

- `--mode=onefile`: 生成单文件可执行程序，所有依赖都打包在一个文件中
- `--output-filename=POChange.exe`: 指定输出文件名

### 使用编译后的程序

编译完成后，可以直接运行生成的 `POChange.exe`：

```bash
POChange.exe --file1 "Weekly Reports/OpenPO 1.9.2026.XLSX" --file2 "Weekly Reports/OpenPO 1.16.2026.XLSX"
```

或者使用默认方式（自动查找最新文件）：

```bash
POChange.exe
```

所有命令行参数和配置文件方式与运行 Python 脚本时完全相同。

## 许可证

本项目采用 MIT 许可证。
