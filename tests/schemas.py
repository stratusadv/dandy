from dandy.schema import Schema


class BusinessIdeaEvaluationSchema(Schema):
    title: str
    description: str
    positive_feedback: list
    negative_feedback: list
    advice: dict
    investment_required: float
    overall_score: int