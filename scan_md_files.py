#!/usr/bin/env python3
import os
import re
import json
import argparse
from pathlib import Path

def parse_md_file(md_path, base_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {
        'packageName': None,
        'originalPath': None,
        'baseDir': str(md_path.parent.absolute()),  # 新增
        'readme': '',
        'files': [],
        'describeFiles': [],
        'describeContents': {}
    }

    state = 'header'
    readme_lines = []
    for line in lines:
        line = line.rstrip('\n')
        if state == 'header':
            if line.startswith('# `'):
                match = re.match(r'# `(.*?)`', line)
                if match:
                    data['packageName'] = match.group(1)
            elif line.startswith('**原始路径**:'):
                raw = line.split(':', 1)[1].strip()
                if raw.startswith('`') and raw.endswith('`'):
                    raw = raw[1:-1]
                data['originalPath'] = raw
                state = 'readme_content'
        elif state == 'readme_content':
            if line.startswith('## 提取的说明文件'):
                state = 'describe_section'
                continue
            elif line.startswith('## 导入路径'):
                state = 'paths'
                continue
            else:
                readme_lines.append(line)
        elif state == 'describe_section':
            if line.startswith('## 导入路径'):
                state = 'paths'
                continue
            match = re.search(r'`(describe_files/.*?)`', line)
            if match:
                rel_path = match.group(1)
                fname = os.path.basename(rel_path)
                data['describeFiles'].append(fname)
                full_path = md_path.parent / rel_path
                if full_path.exists():
                    ext = full_path.suffix.lower()
                    if ext in {'.txt', '.md'}:
                        try:
                            with open(full_path, 'r', encoding='utf-8') as df:
                                data['describeContents'][fname] = df.read()
                        except:
                            pass
        elif state == 'paths':
            if line.startswith('- `'):
                path = line[3:].strip('`').strip()
                if path.endswith('00'):
                    path = path[:-2]
                data['files'].append(path)

    data['readme'] = '\n'.join(readme_lines).strip()
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('md_root', nargs='?', default='.', help='MD文件根目录（递归扫描）')
    parser.add_argument('-o', '--output', default='packages_index.json', help='输出JSON')
    args = parser.parse_args()

    root = Path(args.md_root)
    print(f"🔍 扫描目录: {root}")
    results = []
    for md_path in root.rglob('*.md'):
        try:
            data = parse_md_file(md_path, root)
            if data['packageName']:
                results.append(data)
        except Exception as e:
            print(f"⚠️ 解析 {md_path} 失败: {e}")

    print(f"✅ 找到 {len(results)} 个包信息")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"📦 索引已保存到: {args.output}")

if __name__ == '__main__':
    main()