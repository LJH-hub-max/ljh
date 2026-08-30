import os
import json
from datetime import datetime
from pathlib import Path

PROMPT_DIR = Path("prompt")
PROMPT_DIR.mkdir(parents=True, exist_ok=True)

def parse_conversation(text):
    """
    解析对话文本，假设格式为：
    用户: ...
    助手: ...
    用户: ...
    ...
    返回消息列表
    """
    lines = text.strip().split('\n')
    messages = []
    for line in lines:
        if line.startswith("用户:"):
            messages.append({"role": "user", "content": line[3:].strip()})
        elif line.startswith("助手:"):
            messages.append({"role": "assistant", "content": line[3:].strip()})
        elif line.startswith("系统:") or line.startswith("System:"):
            messages.append({"role": "system", "content": line[3:].strip()})
        # 忽略其他行
    return messages

def save_conversation(text, phase, compressed_before=False):
    messages = parse_conversation(text)
    if not messages:
        print("未提取到有效消息，请检查文本格式。")
        return

    timestamp = datetime.utcnow().isoformat() + "Z"
    filename = f"{datetime.utcnow().strftime('%Y-%m-%d')}_{phase}.json"
    # 如果文件已存在，追加序号
    counter = 1
    while (PROMPT_DIR / filename).exists():
        base, ext = filename.rsplit('.', 1)
        filename = f"{base}_{counter}.{ext}"
        counter += 1

    data = {
        "timestamp": timestamp,
        "phase": phase,
        "conversation": messages,
        "compressed_before": compressed_before,
        "message_count": len(messages)
    }

    filepath = PROMPT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"对话已保存到 {filepath}")

# 使用示例（在命令行运行时可交互输入）
if __name__ == "__main__":
    phase = input("请输入当前阶段名称（如 data_preprocessing）: ")
    compressed = input("是否在上下文压缩前保存？(y/n): ").lower() == 'y'
    print("请将完整的对话内容粘贴进来，输入完成后按 Ctrl+D (Unix) 或 Ctrl+Z+Enter (Windows) 结束：")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    full_text = "\n".join(lines)
    save_conversation(full_text, phase, compressed)
