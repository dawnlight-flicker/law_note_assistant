import dashscope
from dashscope import Generation
import dashscope
from dashscope import Generation
import json  # 补充导入
import re    # 也可以放在顶部

import dashscope
from dashscope import Generation
import json
import re


def get_article_text(keyword, law_name="民法典"):
    """单独获取法条原文"""
    dashscope.api_key = "sk-ade6bfad3da64539b5273a95689729b5"
    # 替换成你在控制台找到的实际Workspace ID
    dashscope.workspace = "ws-gdl411633s9ymfim.cn-beijing.maas.aliyuncs.com"


    prompt = f"请直接输出{law_name}第{keyword}条的原文内容，不需要任何解释。"
    response = Generation.call(
        model="farui-plus",
        messages=[
            {"role": "system", "content": "你是一个中国法律专家，请精确输出法律条文原文。"},
            {"role": "user", "content": prompt}
        ],
        result_format='message'
    )
    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        print(f"获取法条原文失败: {response.message}")
        return ""


def get_judicial_interpretations(keyword, law_name="民法典"):
    """单独获取司法解释"""
    dashscope.api_key = "sk-ade6bfad3da64539b5273a95689729b5"
    # 替换成你在控制台找到的实际Workspace ID
    dashscope.workspace = "ws-gdl411633s9ymfim.cn-beijing.maas.aliyuncs.com"


    prompt = f"请列出与{law_name}第{keyword}条相关的所有司法解释，每条请给出标题和简要内容。如果没有相关司法解释，请返回'暂无'。"
    response = Generation.call(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": "你是一个中国法律专家，请精确输出与法条相关的司法解释。"},
            {"role": "user", "content": prompt}
        ],
        result_format='message'
    )
    if response.status_code == 200:
        content = response.output.choices[0].message.content
        # 简单解析，将文本转换为结构化列表
        interpretations = []
        if content != "暂无":
            # 按行分割，简单处理（可根据实际返回格式优化）
            lines = content.strip().split('\n')
            for line in lines:
                if line.strip():
                    interpretations.append({
                        "title": line[:50],  # 简化处理
                        "content": line
                    })
        return interpretations
    else:
        print(f"获取司法解释失败: {response.message}")
        return []


def get_exam_points(keyword, law_name="民法典"):
    """单独获取考点解析"""
    dashscope.api_key = "sk-ade6bfad3da64539b5273a95689729b5"
    # 替换成你在控制台找到的实际Workspace ID
    dashscope.workspace = "ws-gdl411633s9ymfim.cn-beijing.maas.aliyuncs.com"


    prompt = f"请列出{law_name}第{keyword}条在法律硕士考试中的常见考点，返回一个列表。如果没有常见考点，请返回'暂无'。"
    response = Generation.call(
        model="farui-plus",
        messages=[
            {"role": "system", "content": "你是一个中国法律教育专家，请精确输出法条在法硕考试中的考点。"},
            {"role": "user", "content": prompt}
        ],
        result_format='message'
    )
    if response.status_code == 200:
        content = response.output.choices[0].message.content
        if content == "暂无":
            return []
        # 简单解析，按行拆分
        points = [line.strip() for line in content.strip().split('\n') if line.strip()]
        return points
    else:
        print(f"获取考点解析失败: {response.message}")
        return []


def search_law_via_api_sdk(keyword, law_name="民法典"):
    """
    综合调用上述三个函数，获取完整数据
    """
    print(f"正在获取法条原文...")
    article_text = get_article_text(keyword, law_name)

    print(f"正在获取司法解释...")
    judicial_interpretations = get_judicial_interpretations(keyword, law_name)

    print(f"正在获取考点解析...")
    exam_points = get_exam_points(keyword, law_name)

    if article_text:
        return {
            "law_name": law_name,
            "article_number": keyword,
            "article_text": article_text,
            "judicial_interpretations": judicial_interpretations,
            "exam_points": exam_points,
            "source": "通义法睿API（AI生成，仅供参考）"
        }
    else:
        return None


