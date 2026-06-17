# UnityPackage 本地资源管理器

> 在 Unity 锁国区后，帮你高效管理和检索本地成百上千个 `.unitypackage` 缓存文件的离线工具集。

## 📌 项目背景

由于 Unity 官方调整了区域策略，中国大陆用户无法正常访问 Asset Store 的在线服务，导致大量已购买的资源包只能躺在本地缓存目录中，难以查找和使用。本项目提供了一套**完全离线**的解决方案，让你可以：
- 快速浏览每个包的内容（文件列表）
- 提取包内的 README 和说明文档（支持 PDF/TXT/MD 等）
- 通过关键词搜索包名、文件路径、文档内容
- 一键定位包文件或说明文件目录

无需联网，无需 Unity 编辑器，仅需 Python 3 和一个现代浏览器。

## ✨ 功能特点

- 📦 **批量处理** – 自动扫描指定目录下所有 `.unitypackage`，逐个提取元数据。
- 📄 **内容提取** – 提取每个包内的 `pathname`（真实导入路径）和 README 文本，并解压所有说明文件（PDF/MD/TXT/DOC 等）到独立目录。
- 🗂️ **结构化存储** – 每个包生成一个独立文件夹，包含一个 Markdown 清单文件和 `describe_files` 子目录。
- 🔍 **全文搜索** – 通过 HTML 界面，可搜索包名、原始路径、README 内容、文件列表，实时过滤。
- 📖 **内联预览** – 支持 `.txt` 和 `.md` 说明文件的在线预览，无需打开外部程序。
- 📁 **快速定位** – 一键在 Finder 中打开包所在目录或 `describe_files` 目录。
- 🚀 **分页浏览** – 支持每页 18/36/72/96 条记录，方便浏览大量数据。

## 🛠️ 系统要求

- **操作系统**：macOS（理论上 Linux/Windows 也可运行，但 Finder 打开功能需调整）
- **Python**：3.6 或更高版本（仅需标准库，无需额外安装包）
- **浏览器**：Chrome / Edge / Safari（支持 `file://` 协议）

## 📂 项目结构

```
UnityPackageManager/
├── extract_package_info.py   # 单包处理核心
├── batch_extract.py          # 批量处理脚本（需填写路径）
├── scan_md_files.py          # 生成 JSON 索引
├── browser.html              # 本地浏览器界面
└── README.md
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/GtyFour/UnityLocalAssetsBrowser.git
cd UnityLocalAssetsBrowser
```

### 2. 配置批量处理脚本

编辑 `batch_extract.py`，修改以下两个路径：

```python
TARGET_DIR = "/Users/你的用户名/Library/Unity/Asset Store-5.x"   # 你的 Unity 缓存目录
OUTPUT_DIR = "/Users/你的用户名/Downloads/UnityPackage_Manifests" # 输出目录（可自定义）
```

> 缓存目录通常为 `~/Library/Unity/Asset Store-5.x/`，请根据实际情况调整。

### 3. 运行批量处理

```bash
python3 batch_extract.py
```

该脚本会遍历 `TARGET_DIR` 下的所有 `.unitypackage` 文件，调用 `extract_package_info.py` 逐一处理。  
处理后的输出目录结构如下：

```
OUTPUT_DIR/
  包名1/
    包名1.md
    describe_files/
      说明文件1.pdf
      说明文件2.txt
  包名2/
    包名2.md
    describe_files/
      ...
  ...
```

处理时间取决于包的数量和大小，请耐心等待。

### 4. 生成 JSON 索引

```bash
python3 scan_md_files.py /path/to/OUTPUT_DIR -o packages_index.json
```

例如：

```bash
python3 scan_md_files.py /Users/你的用户名/Downloads/UnityPackage_Manifests -o packages_index.json
```

该脚本会扫描 `OUTPUT_DIR` 下的所有 `.md` 文件，提取关键信息，并生成 `packages_index.json`。

### 5. 启动浏览器界面

双击 `assets_browser.html` 文件，在浏览器中打开。

- 点击 **“📂 选择 JSON 索引”**，选择上一步生成的 `packages_index.json`。
- 加载完成后，即可浏览所有包的信息。
- 在搜索框中输入关键词，按 **回车** 或点击 **“搜索”** 按钮进行筛选。
- 点击包卡片可展开查看 README 和完整文件列表。
- 使用右侧按钮快速定位：
  - **📁 包路径** – 在 Finder 中打开 `.unitypackage` 所在文件夹
  - **📋 复制路径** – 复制文件夹路径到剪贴板
  - **📄 描述文件** – 在 Finder 中打开该包的 `describe_files` 目录（如果存在）
  - **📄 说明文件 (N)** – 展开显示所有提取的说明文件，支持预览 `.txt` 和 `.md`

## 🔧 自定义与扩展

- **修改 README 匹配规则**：编辑 `extract_package_info.py` 中的 `DESC_KEYWORDS` 正则表达式，可自定义哪些文件名被视为说明文件。
- **添加更多扩展名支持**：修改 `DESC_EXTS` 集合，可增加 `.doc`、`.rtf` 等格式（目前这些格式虽会被提取，但不会内联预览）。
- **调整分页大小**：在 `browser.html` 中的 `pageSizeOptions` 数组中修改可选值。
- **Main分支是适配Mac端的，需要Windows端的请切换Windows分支。

## ⚠️ 注意事项

- 本工具**不会修改或删除**原始 `.unitypackage` 文件，所有操作均为只读。
- 由于浏览器安全策略，`file://` 协议下打开 Finder 可能会被拦截，若拦截会自动降级为复制路径并提示。
- 如果某个包损坏或无法读取，脚本会记录错误并继续处理下一个包，不影响整体流程。
- 输出目录可能会占用一定磁盘空间（主要是提取的说明文件），但远小于原始包的总大小。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。如果你有更好的想法或发现了 Bug，请随时告知。
感谢小鲸鱼(Deepseek)的帮助。

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

感谢所有在 Unity 锁区后依然坚持分享经验的开发者们，正是你们的智慧让我们能够继续前行。
