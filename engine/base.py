
from abc import ABC, abstractmethod
from typing import List
from data.models import Content


class BaseRecommender(ABC):
    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def recommend(self, user_id: int, top_k: int = 10) -> List[Content]:
        pass

