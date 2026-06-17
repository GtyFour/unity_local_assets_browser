#!/usr/bin/env python3
import os
import re
import tarfile
import shutil
from pathlib import Path

DESC_KEYWORDS = re.compile(r'(read[\s_\-\.]*me|manual|guide|instruction|doc|info|readme)', re.IGNORECASE)
DESC_EXTS = {'.pdf', '.md', '.txt', '.doc', '.docx', '.rtf'}

def clean_file_name(name: str) -> str:
    """
    去除文件名末尾可能存在的 '00' 或 '00\n' 等多余字符。
    例如 'README.pdf\n00' -> 'README.pdf'
    """
    # 先去除换行和空格
    name = name.strip()
    # 如果以 '00' 结尾，去掉它
    if name.endswith('00'):
        name = name[:-2]
    # 再去除可能残留的空白
    return name.strip()

def extract_package_info(package_path, output_base_dir):
    pkg_path = Path(package_path)
    pkg_name = pkg_path.stem

    # 创建包专属目录（自动重名处理）
    pkg_out_dir = Path(output_base_dir) / pkg_name
    if pkg_out_dir.exists():
        counter = 1
        while True:
            new_dir = Path(output_base_dir) / f"{pkg_name} ({counter})"
            if not new_dir.exists():
                pkg_out_dir = new_dir
                break
            counter += 1
    pkg_out_dir.mkdir(parents=True, exist_ok=True)

    md_file = pkg_out_dir / f"{pkg_name}.md"
    desc_dir = pkg_out_dir / "describe_files"
    desc_dir.mkdir(exist_ok=True)

    paths = []                # 所有导入路径（pathname）
    readme_text = ""          # 合并的 README 文本
    extracted_files = []      # (原始路径, 相对路径)

    try:
        with tarfile.open(package_path, 'r:gz') as tar:
            # 第一遍：建立 GUID -> pathname 和 asset 成员的映射
            guid_to_pathname = {}
            guid_to_asset_member = {}
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                parts = member.name.split('/')
                if len(parts) >= 2:
                    guid = parts[0]
                    fname = parts[-1]
                    if fname == 'pathname':
                        f = tar.extractfile(member)
                        if f:
                            content = f.read().decode('utf-8', errors='ignore').strip()
                            if content:
                                cleaned = clean_file_name(content)
                                guid_to_pathname[guid] = cleaned
                            f.close()
                    elif fname == 'asset':
                        guid_to_asset_member[guid] = member

            # 第二遍：处理每个 pathname
            for guid, path_str in guid_to_pathname.items():
                paths.append(path_str)  # 已经 cleaned，存入导入路径列表
                fname = os.path.basename(path_str)  # 文件名也是 cleaned
                ext = Path(fname).suffix.lower()

                # 如果是 README 文本文件，收集内容
                if DESC_KEYWORDS.search(fname) and ext in {'.txt', '.md'}:
                    asset_member = guid_to_asset_member.get(guid)
                    if asset_member:
                        f = tar.extractfile(asset_member)
                        if f:
                            try:
                                content = f.read().decode('utf-8')
                            except:
                                content = f.read().decode('latin-1', errors='replace')
                            readme_text += f"\n--- {fname} ---\n{content}\n"
                            f.close()

                # 如果是说明文件（匹配关键词或扩展名），解压到 describe_files/
                if DESC_KEYWORDS.search(fname) or ext in DESC_EXTS:
                    asset_member = guid_to_asset_member.get(guid)
                    if asset_member:
                        base_name = fname  # 已经 cleaned
                        dest_path = desc_dir / base_name
                        # 重名处理
                        if dest_path.exists():
                            stem = dest_path.stem
                            ext2 = dest_path.suffix
                            cnt = 1
                            while True:
                                new_name = f"{stem}_{cnt}{ext2}"
                                new_dest = desc_dir / new_name
                                if not new_dest.exists():
                                    dest_path = new_dest
                                    break
                                cnt += 1
                        # 提取 asset 内容
                        f = tar.extractfile(asset_member)
                        if f:
                            with open(dest_path, 'wb') as out_f:
                                shutil.copyfileobj(f, out_f)
                            rel_path = f"describe_files/{dest_path.name}"
                            extracted_files.append((path_str, rel_path))
                            f.close()

    except Exception as e:
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# `{pkg_name}` 文件清单\n\n")
            f.write(f"**原始路径**: `{package_path}`\n\n")
            f.write(f"**错误**: {e}\n")
        return False

    # 写入 MD 文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# `{pkg_name}` 文件清单\n\n")
        f.write(f"**原始路径**: `{package_path}`\n\n")

        f.write("## README 文档内容\n\n")
        if readme_text.strip():
            f.write("```\n")
            f.write(readme_text.strip())
            f.write("\n```\n\n")
        else:
            f.write("*（包内未找到任何 README 文件）*\n\n")

        if extracted_files:
            f.write("## 📄 提取的说明文件\n\n")
            for orig, rel in extracted_files:
                f.write(f"- 原始路径: `{orig}` → 已解压至: `{rel}`\n")
            f.write("\n")

        f.write("## 导入路径（从 `pathname` 解析）\n\n")
        if paths:
            for p in sorted(paths):
                f.write(f"- `{p}`\n")
        else:
            f.write("*（未提取到任何路径）*\n")

    return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('package', help='unitypackage 文件路径')
    parser.add_argument('-o', '--output', default='.', help='输出根目录')
    args = parser.parse_args()
    extract_package_info(args.package, args.output)