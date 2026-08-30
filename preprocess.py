import os
import csv
from pathlib import Path

# ========== 配置 ==========
RAW_DATA_DIR = "data"               # 原始数据根目录（包含 0_BehnkeGeiger/ 等子文件夹）
OUTPUT_DIR = "processed_data"       # 输出目录，只存放索引文件
INDEX_CSV = os.path.join(OUTPUT_DIR, "index.csv")

# ========== 解析函数 ==========
def parse_fjs(filepath):
    """
    解析单个 .fjs 文件，返回字典（仅元数据，不包含工序详细数据）
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
    
    total_ops = 0
    max_time = 0

    # 后续每行是一个工件的工序列表
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        num_ops = int(parts[0])
        total_ops += num_ops
        idx = 1
        for _ in range(num_ops):
            if idx >= len(parts):
                break
            num_alt = int(parts[idx])
            idx += 1
            for _ in range(num_alt):
                # 跳过机器号，只取时间
                machine = int(parts[idx])
                time = int(parts[idx+1])
                idx += 2
                if time > max_time:
                    max_time = time

    return {
        'filename': os.path.basename(filepath),
        'jobs': jobs,
        'machines': machines,
        'total_operations': total_ops,
        'max_time': max_time,
        'filepath': str(filepath)
    }

# ========== 主流程 ==========
def main():
    # 创建输出目录
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # 收集所有 .fjs 文件（递归）
    raw_path = Path(RAW_DATA_DIR)
    fjs_files = list(raw_path.rglob("*.fjs")) + list(raw_path.rglob("*.FJS"))
    print(f"找到 {len(fjs_files)} 个 .fjs 文件")

    if not fjs_files:
        print("错误: 未找到任何 .fjs 文件，请检查 RAW_DATA_DIR 路径。")
        return

    index_rows = []

    for fpath in fjs_files:
        data = parse_fjs(fpath)
        if not data:
            print(f"警告: 解析失败 - {fpath}")
            continue

        index_rows.append({
            'filename': data['filename'],
            'jobs': data['jobs'],
            'machines': data['machines'],
            'total_operations': data['total_operations'],
            'max_time': data['max_time'],
            'filepath': data['filepath']
        })

    # 写索引 CSV
    with open(INDEX_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['filename', 'jobs', 'machines', 'total_operations', 'max_time', 'filepath']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(index_rows)
    print(f"索引已写入 {INDEX_CSV}")

    print("预处理完成！")

if __name__ == "__main__":
    main()
