# exporter.py
import datetime


def export_to_markdown(law_data, save_path):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = law_data.get('source', '本地审核库')
    content = f"""# {law_data['law_name']}第{law_data['article_number']}条 学习笔记

> 导出时间：{now}
> 数据来源：{source}

## 📜 法条原文

{law_data['article_text']}

## ⚖️ 关联司法解释

"""
    if law_data.get('judicial_interpretations'):
        for ji in law_data['judicial_interpretations']:
            content += f"### {ji['title']}\n\n{ji['content']}\n\n"
    else:
        content += "暂无关联司法解释\n\n"

    content += "## 🎯 常见考点\n\n"
    if law_data.get('exam_points'):
        for point in law_data['exam_points']:
            content += f"- {point}\n"
    else:
        content += "暂无考点信息\n"

    content += "\n---\n*笔记由「法条笔记助手」自动生成*"

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)