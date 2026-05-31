"""Quiz API endpoints."""
from aitutor.backend.quiz.models import (
    QuizRequest,
    QuizSubmitRequest,
    QuizResponse,
    QuizSubmitResponse,
)
from aitutor.backend.quiz.generator import generate_quiz
from aitutor.backend.quiz.bloom import calculate_adaptive_action


async def generate_quiz_endpoint(request: QuizRequest) -> QuizResponse:
    """Generate a new quiz question."""
    return await generate_quiz(
        topic=request.topic,
        student_level=request.student_level,
        history=request.history,
    )


async def submit_quiz_endpoint(request: QuizSubmitRequest) -> QuizSubmitResponse:
    """Submit a quiz answer and get adaptive feedback."""
    return QuizSubmitResponse(
        acknowledged=True,
        new_level=0,
        next_action="pending",
    )
