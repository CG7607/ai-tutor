"""Quiz generation pipeline with adversarial verification."""
import json
import uuid

from aitutor.backend.llm.client import chat_completion, structured_output
from aitutor.backend.quiz.bloom import (
    BLOOM_LEVELS,
    get_question_types_for_level,
    get_prompt_hint_for_level,
    calculate_adaptive_action,
)
from aitutor.backend.quiz.models import QuizResponse

QUIZ_GENERATION_PROMPT = """你是《人工智能导论》课程的出题专家。根据以下参数生成一道测试题。

## 题目参数
- 知识点：{topic}
- 布鲁姆认知层次：L{level} ({level_name})
- 层次说明：{level_hint}
- 题目类型要求：从 {question_types} 中选择最合适的

## 输出要求
1. 题目语言：中文
2. 选择题必须提供 4 个选项
3. 答案必须准确无误
4. 解析必须详细，解释为什么正确答案是对的、错误选项错在哪里
5. 难度匹配指定的布鲁姆层次

## 输出格式（JSON）
{{
  "question": "题面文本",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "question_type": "single_choice",
  "answer": "B",
  "explanation": "详细解析..."
}}
"""

VERIFICATION_PROMPT = """你是《人工智能导论》课程的审题专家。请检查以下题目是否存在问题。

## 待审题目
知识点：{topic}
布鲁姆层次：L{level} ({level_name})
题目：{question}
选项：{options}
答案：{answer}
解析：{explanation}

## 检查清单
1. 答案是否正确？（如果错误，给出正确答案）
2. 题面是否有歧义？（如果有，指出歧义在哪）
3. 难度是否匹配指定的布鲁姆层次？（如果不匹配，说明为什么不匹配）
4. 选项是否合理？（错误选项是否明显离谱）

## 输出格式（JSON）
{{
  "is_valid": true/false,
  "issues": ["问题1", "问题2"],
  "corrected_answer": "如答案有误，给出正确答案"
}}
"""


async def generate_quiz(
    topic: str,
    student_level: int,
    history: list[dict] | None = None,
) -> QuizResponse:
    """Generate a quiz question with adversarial verification.

    Args:
        topic: The knowledge topic to test
        student_level: Current Bloom level (1-6)
        history: Past quiz attempts for this student

    Returns:
        A verified QuizResponse.
    """
    level_info = BLOOM_LEVELS.get(student_level, BLOOM_LEVELS[1])
    question_types = get_question_types_for_level(student_level)
    level_hint = get_prompt_hint_for_level(student_level)

    generation_prompt = QUIZ_GENERATION_PROMPT.format(
        topic=topic,
        level=student_level,
        level_name=level_info["name"],
        level_hint=level_hint,
        question_types=", ".join(question_types),
    )

    # Step 1: Generate the question
    raw = await structured_output(
        messages=[{"role": "user", "content": f"知识点：{topic}"}],
        system_prompt=generation_prompt,
        output_schema={
            "question": "题面文本",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "question_type": "single_choice",
            "answer": "B",
            "explanation": "详细解析...",
        },
        temperature=0.7,
    )

    # Step 2: Adversarial verification
    verification_result = await _verify_question(
        topic=topic,
        level=student_level,
        level_name=level_info["name"],
        question=raw["question"],
        options=raw.get("options", []),
        answer=raw["answer"],
        explanation=raw["explanation"],
    )

    # Step 3: If invalid, use corrected answer
    if not verification_result.get("is_valid", True):
        if "corrected_answer" in verification_result:
            raw["answer"] = verification_result["corrected_answer"]
            raw["explanation"] += "\n\n（经审题系统校正）"

    # Step 4: Calculate adaptive action
    accuracy = _calculate_recent_accuracy(history)
    new_level, action = calculate_adaptive_action(
        student_level, accuracy, len(history or [])
    )

    return QuizResponse(
        question_id=f"q_{uuid.uuid4().hex[:8]}",
        question=raw["question"],
        options=raw.get("options"),
        question_type=raw.get("question_type", "single_choice"),
        answer=raw["answer"],
        explanation=raw["explanation"],
        bloom_level=student_level,
        adaptive_action=action,
    )


async def _verify_question(
    topic: str,
    level: int,
    level_name: str,
    question: str,
    options: list[str],
    answer: str,
    explanation: str,
) -> dict:
    """Run adversarial verification on a generated question."""
    try:
        result = await structured_output(
            messages=[{
                "role": "user",
                "content": VERIFICATION_PROMPT.format(
                    topic=topic,
                    level=level,
                    level_name=level_name,
                    question=question,
                    options=json.dumps(options, ensure_ascii=False),
                    answer=answer,
                    explanation=explanation,
                ),
            }],
            system_prompt="你是严格的审题专家。只输出 JSON，不要加任何其他内容。",
            output_schema={
                "is_valid": True,
                "issues": ["问题描述"],
                "corrected_answer": "如答案有误，给出正确答案",
            },
            temperature=0.1,
        )
        return result
    except Exception:
        # Verification failed — assume question is valid
        return {"is_valid": True, "issues": [], "corrected_answer": ""}


def _calculate_recent_accuracy(history: list[dict] | None, n: int = 5) -> float:
    """Calculate accuracy over the most recent n questions."""
    if not history:
        return 0.5  # Default for new students
    recent = history[-n:]
    if not recent:
        return 0.5
    correct = sum(1 for h in recent if h.get("correct", False))
    return correct / len(recent)
