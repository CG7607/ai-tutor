"""Quiz generation pipeline with adversarial verification + dedup."""
import hashlib
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

# 每个知识点的子维度，让题目更丰富
TOPIC_DIMENSIONS = {
    "梯度下降": [
        "基本概念与更新公式", "学习率的选择与影响", "批量/随机/小批量梯度下降的区别",
        "梯度下降的收敛性条件", "局部最优与鞍点问题", "动量法与Nesterov加速",
        "梯度下降在非凸优化中的表现", "梯度裁剪技术",
    ],
    "反向传播": [
        "链式法则的直观理解", "前向与反向的计算图", "梯度在深层网络中的流动",
        "激活函数对反向传播的影响", "反向传播的计算复杂度", "自动微分原理",
    ],
    "CNN": [
        "卷积操作的本质", "池化层的作用与类型", "感受野与特征层级",
        "1x1卷积与降维", "转置卷积与上采样", "CNN的平移不变性",
    ],
    "RNN/LSTM": [
        "序列建模的挑战", "BPTT与梯度问题", "LSTM门控机制详解",
        "GRU与LSTM的对比", "双向RNN的设计思想", "序列到序列模型",
    ],
    "Transformer": [
        "自注意力机制的数学原理", "多头注意力的设计动机", "位置编码方案对比",
        "残差连接与层归一化", "Encoder-Decoder架构", "Transformer的训练技巧",
    ],
    "过拟合与正则化": [
        "过拟合的检测方法", "L1/L2正则化的几何解释", "Dropout的工作原理",
        "早停法的理论与实践", "数据增强的正则化效果", "BatchNorm的正则化作用",
    ],
    "损失函数": [
        "MSE与MAE的对比", "交叉熵的推导过程", "Hinge Loss与SVM",
        "损失函数与激活函数的配对", "Focal Loss的设计思想", "对比损失函数",
    ],
    "优化算法": [
        "Momentum的物理直觉", "AdaGrad与RMSProp", "Adam的偏差修正",
        "学习率衰减策略", "二阶优化方法概述", "优化器的选择指南",
    ],
    "生成式模型": [
        "自编码器的变体", "GAN的训练技巧", "VAE的变分推导",
        "扩散模型的基本原理", "自回归生成模型", "生成模型的评估指标",
    ],
    "K-means聚类": [
        "K值选择方法", "初始中心点的影响", "K-means++初始化",
        "K-means的局限性", "K-medoids与K-modes", "聚类的内部评估指标",
    ],
    "SVM": [
        "最大间隔的几何理解", "核技巧的数学原理", "软间隔与松弛变量",
        "SVM的对偶问题", "支持向量的含义", "SVM与逻辑回归的对比",
    ],
    "决策树": [
        "信息增益与基尼系数", "剪枝策略对比", "CART与ID3/C4.5",
        "决策树的过拟合问题", "特征重要性的计算", "决策树与规则提取",
    ],
}

QUIZ_GENERATION_PROMPT = """你是《人工智能导论》课程的出题专家。根据以下参数生成一道全新的、有创意的测试题。

## 题目参数
- 知识点：{topic}
- 考察角度：{dimension}
- 布鲁姆认知层次：L{level} ({level_name})
- 层次说明：{level_hint}
- 要求题型：{question_types}

## 重要约束
1. **必须原创**：不要出常见的教科书原题，要从新的角度切入
2. 题目语言：中文
3. 选择题必须提供 4 个选项，选项长度不要太悬殊
4. 答案的字母(A/B/C/D)必须对应选项的前缀字母
5. 解析必须详细，至少 3 句话，解释为什么正确答案是对的、错误选项为什么错
6. 难度严格匹配指定的布鲁姆层次
7. {avoid_hint}

## 题目风格参考
- 可以问"以下哪个说法是**错误**的"来增加变化
- 可以给一个具体场景或数值算例
- 可以引用真实论文或历史事件作为背景
- 可以设计"代码填空"型选择题

## 输出格式（严格 JSON）
{{
  "question": "题面文本（必须是全新的、有创意的题目）",
  "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
  "question_type": "single_choice",
  "answer": "A",
  "explanation": "详细解析，至少3句话"
}}
"""

VERIFICATION_PROMPT = """你是《人工智能导论》课程的严厉审题专家。请以批判性眼光检查以下题目。

## 待审题目
知识点：{topic}
布鲁姆层次：L{level} ({level_name})
题目：{question}
选项：{options}
声称答案：{answer}
解析：{explanation}

## 严格检查清单
1. 答案是否**绝对正确**？（如果错误，给出正确答案）
2. 题面是否有歧义或表述不清？
3. 难度是否匹配 L{level} ({level_name}) 层次？
4. 所有错误选项是否都明显不对？（不能有模棱两可的选项）
5. 题目是否太简单/太偏/太常见？

## 输出格式（严格 JSON）
{{
  "is_valid": true,
  "issues": [],
  "corrected_answer": ""
}}
"""


class QuestionDeduplicator:
    """题目去重，基于题目文本的哈希值"""

    def __init__(self):
        self._hashes: set[str] = set()

    def add(self, question_text: str) -> None:
        h = hashlib.md5(question_text.strip().encode()).hexdigest()
        self._hashes.add(h)

    def is_duplicate(self, question_text: str) -> bool:
        h = hashlib.md5(question_text.strip().encode()).hexdigest()
        return h in self._hashes

    def load_from_history(self, history: list[dict]) -> None:
        for item in history:
            q = item.get("question", "")
            if q:
                self.add(q)


async def generate_quiz(
    topic: str,
    student_level: int,
    history: list[dict] | None = None,
    search_context: str = "",
) -> QuizResponse:
    """Generate a novel quiz question with adversarial verification and dedup.

    Args:
        topic: Knowledge topic
        student_level: Bloom level (1-6)
        history: Past quiz attempts (for accuracy calc AND dedup)
        search_context: Optional web search results as question context

    Returns:
        Verified QuizResponse.
    """
    import random

    level_info = BLOOM_LEVELS.get(student_level, BLOOM_LEVELS[1])
    question_types = get_question_types_for_level(student_level)
    level_hint = get_prompt_hint_for_level(student_level)

    # 随机选一个子维度，增加题目多样性
    dimensions = TOPIC_DIMENSIONS.get(topic, ["基本概念"])
    dimension = random.choice(dimensions)

    # Init deduplicator from history
    dedup = QuestionDeduplicator()
    dedup.load_from_history(history or [])

    # 构建避免重复提示
    past_questions = [h.get("question", "") for h in (history or []) if h.get("question")]
    avoid_hint = "不要出与之前雷同的题目。"
    if past_questions:
        recent = past_questions[-5:]
        avoid_hint += f" 最近出过的题目：{'；'.join(recent[:3])}"

    # 搜索上下文
    search_hint = ""
    if search_context:
        search_hint = f"\n\n## 参考资料（可据此出题，但必须确保准确性）\n{search_context[:1000]}"

    generation_prompt = QUIZ_GENERATION_PROMPT.format(
        topic=topic,
        dimension=dimension,
        level=student_level,
        level_name=level_info["name"],
        level_hint=level_hint,
        question_types=", ".join(question_types),
        avoid_hint=avoid_hint,
    )

    # Step 1: Generate the question (retry up to 3 times for uniqueness)
    max_attempts = 3
    raw = {}
    for attempt in range(max_attempts):
        raw = await structured_output(
            messages=[{"role": "user", "content": f"知识点：{topic}\n考察角度：{dimension}{search_hint}"}],
            system_prompt=generation_prompt,
            output_schema={
                "question": "题面文本",
                "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
                "question_type": "single_choice",
                "answer": "A",
                "explanation": "详细解析，至少3句话",
            },
            temperature=0.9 + attempt * 0.05,  # 逐步增加随机性
        )
        if not dedup.is_duplicate(raw.get("question", "")):
            break

    # Step 2: 规范化答案（确保是单个字母）
    answer = raw.get("answer", "A").strip().upper()
    if len(answer) > 1 and answer.startswith(("A", "B", "C", "D")):
        answer = answer[0]
    if answer not in ("A", "B", "C", "D"):
        answer = "A"  # fallback

    # Step 3: Adversarial verification
    verification_result = await _verify_question(
        topic=topic,
        level=student_level,
        level_name=level_info["name"],
        question=raw["question"],
        options=raw.get("options", []),
        answer=answer,
        explanation=raw.get("explanation", ""),
    )

    if not verification_result.get("is_valid", True):
        corrected = verification_result.get("corrected_answer", "").strip().upper()
        if corrected and corrected[0] in ("A", "B", "C", "D"):
            answer = corrected[0]
            raw["explanation"] += "\n\n（经审题系统校正）"

    # Step 4: Calculate adaptive action
    accuracy = _calculate_recent_accuracy(history)
    new_level, action = calculate_adaptive_action(
        student_level, accuracy, len(history or [])
    )

    # Step 5: 记录这题（防止后续重复）
    dedup.add(raw["question"])

    return QuizResponse(
        question_id=f"q_{uuid.uuid4().hex[:8]}",
        topic=topic,
        question=raw["question"],
        options=raw.get("options"),
        question_type=raw.get("question_type", "single_choice"),
        answer=answer,
        explanation=raw.get("explanation", ""),
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
                "corrected_answer": "",
            },
            temperature=0.1,
        )
        return result
    except Exception:
        return {"is_valid": True, "issues": [], "corrected_answer": ""}


def _calculate_recent_accuracy(history: list[dict] | None, n: int = 5) -> float:
    """Calculate accuracy over the most recent n questions."""
    if not history:
        return 0.5
    recent = history[-n:]
    if not recent:
        return 0.5
    correct = sum(1 for h in recent if h.get("correct", False))
    return correct / len(recent)
