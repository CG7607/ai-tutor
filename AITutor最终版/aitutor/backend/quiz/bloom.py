"""Bloom's taxonomy classifier for adaptive difficulty."""

BLOOM_LEVELS = {
    1: {
        "name": "记忆",
        "keywords": ["列举", "定义", "复述", "识别", "描述"],
        "question_types": ["single_choice", "fill_blank"],
        "prompt_hint": "考查学生对基本概念、术语的记忆。题目应直接，不需要推理。",
    },
    2: {
        "name": "理解",
        "keywords": ["解释", "总结", "举例", "归纳", "用自己的话"],
        "question_types": ["single_choice", "multi_choice", "short_answer"],
        "prompt_hint": "考查学生是否真正理解了概念的含义，能否用自己的话解释。",
    },
    3: {
        "name": "应用",
        "keywords": ["计算", "实现", "求解", "使用", "应用"],
        "question_types": ["single_choice", "short_answer"],
        "prompt_hint": "考查学生能否将理论知识应用到具体问题中，进行实际计算或简单实现。",
    },
    4: {
        "name": "分析",
        "keywords": ["对比", "区分", "解构", "分析原因", "找出差异"],
        "question_types": ["multi_choice", "short_answer"],
        "prompt_hint": "考查学生能否分析问题的组成部分，识别因果关系和隐含假设。",
    },
    5: {
        "name": "评价",
        "keywords": ["评判", "论证", "推荐", "优缺点", "适用场景"],
        "question_types": ["short_answer", "open"],
        "prompt_hint": "考查学生能否对方法/模型做出有据可依的判断和评价。",
    },
    6: {
        "name": "创造",
        "keywords": ["设计", "构建", "综合", "改进", "提出新方法"],
        "question_types": ["open"],
        "prompt_hint": "考查学生能否综合所学知识，创造性地设计新方案或改进已有方法。",
    },
}


def calculate_adaptive_action(
    current_level: int,
    recent_accuracy: float,
    recent_count: int = 5,
) -> tuple[int, str]:
    """Determine whether to upgrade, maintain, or downgrade the student's level.

    Args:
        current_level: Current Bloom level (1-6)
        recent_accuracy: Accuracy rate over recent questions (0.0-1.0)
        recent_count: Number of recent questions to consider

    Returns:
        Tuple of (new_level, action_string).
    """
    if recent_count < 3:
        # Not enough data — maintain current level
        return current_level, "maintain"

    if recent_accuracy > 0.8:
        new_level = min(6, current_level + 1)
        return new_level, "upgrade"
    elif recent_accuracy < 0.5:
        new_level = max(1, current_level - 1)
        return new_level, "downgrade"
    else:
        return current_level, "maintain"


def get_question_types_for_level(level: int) -> list[str]:
    """Get appropriate question types for a Bloom level."""
    return BLOOM_LEVELS.get(level, BLOOM_LEVELS[1])["question_types"]


def get_prompt_hint_for_level(level: int) -> str:
    """Get the prompt hint for a Bloom level."""
    return BLOOM_LEVELS.get(level, BLOOM_LEVELS[1])["prompt_hint"]
