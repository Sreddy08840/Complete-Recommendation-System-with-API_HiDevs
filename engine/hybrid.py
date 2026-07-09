
from .base import BaseRecommender
from typing import List
from data.models import Content


class HybridRecommender(BaseRecommender):
    def __init__(self):
        pass

    def fit(self):
        pass

    def recommend(self, user_id: int, top_k: int = 10) -> List[Content]:
        return []

