import os
import re
import json
import csv
from pathlib import Path

# ========== 配置 ==========
RAW_DATA_DIR = "../FJSP-benchmarks"   # 原始数据根目录（相对路径）
OUTPUT_DIR = "data"                   # 输出目录
INDEX_CSV = os.path.join(OUTPUT_DIR, "index.csv")
DETAILS_JSON = os.path.join(OUTPUT_DIR, "instances.json")
PER_INSTANCE_DIR = os.path.join(OUTPUT_DIR, "instances")  # 每个实例单独保存

# ========== 解析函数 ==========
def parse_fjs(filepath):
    """
    解析单个 .fjs 文件，返回字典：
    {
        'filename': str,
        'jobs': int,
        'machines': int,
        'total_operations': int,
        'max_time': int,
        'operations': [ [ [(machine, time), ...], ... ], ... ]  # 工件→工序→候选列表
    }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 去除空行和注释（#开头）
    lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    if not lines:
        return None

    # 第一行: jobs machines
    first = lines[0].split()
    if len(first) < 2:
        return None
    jobs = int(first[0])
    machines = int(first[1])
    
    operations = []
    total_ops = 0
    max_time = 0

    # 后续每行是一个工件的工序列表
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        num_ops = int(parts[0])
        ops = []
        idx = 1
        for _ in range(num_ops):
            if idx >= len(parts):
                break
            num_alt = int(parts[idx])
            idx += 1
            alt_list = []
            for _ in range(num_alt):
                machine = int(parts[idx])
                time = int(parts[idx+1])
                alt_list.append((machine, time))
                idx += 2
                if time > max_time:
                    max_time = time
            ops.append(alt_list)
        operations.append(ops)
        total_ops += num_ops

    return {
        'filename': os.path.basename(filepath),
        'jobs': jobs,
        'machines': machines,
        'total_operations': total_ops,
        'max_time': max_time,
        'operations': operations,
        'filepath': str(filepath)
    }

# ========== 主流程 ==========
def main():
    # 创建输出目录
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(PER_INSTANCE_DIR).mkdir(parents=True, exist_ok=True)

    # 收集所有 .fjs 文件（递归）
    raw_path = Path(RAW_DATA_DIR)
    fjs_files = list(raw_path.rglob("*.fjs")) + list(raw_path.rglob("*.FJS"))
    print(f"找到 {len(fjs_files)} 个 .fjs 文件")

    if not fjs_files:
        print("错误: 未找到任何 .fjs 文件，请检查 RAW_DATA_DIR 路径。")
        return

    index_rows = []
    all_details = {}

    for fpath in fjs_files:
        data = parse_fjs(fpath)
        if not data:
            print(f"警告: 解析失败 - {fpath}")
            continue

        # 索引记录
        index_rows.append({
            'filename': data['filename'],
            'jobs': data['jobs'],
            'machines': data['machines'],
            'total_operations': data['total_operations'],
            'max_time': data['max_time'],
            'filepath': data['filepath']
        })

        # 详细数据（仅保留结构，不包含filepath）
        detail = {k: v for k, v in data.items() if k != 'filepath'}
        all_details[data['filename']] = detail

        # 单独保存每个实例的 JSON（可选）
        instance_out = os.path.join(PER_INSTANCE_DIR, data['filename'].replace('.fjs', '.json').replace('.FJS', '.json'))
        with open(instance_out, 'w', encoding='utf-8') as f:
            json.dump(detail, f, indent=2, ensure_ascii=False)

    # 写索引 CSV
    with open(INDEX_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['filename', 'jobs', 'machines', 'total_operations', 'max_time', 'filepath']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(index_rows)
    print(f"索引已写入 {INDEX_CSV}")

    # 写总 JSON
    with open(DETAILS_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_details, f, indent=2, ensure_ascii=False)
    print(f"详细数据已写入 {DETAILS_JSON}")

    print("预处理完成！")

if __name__ == "__main__":
    main()
