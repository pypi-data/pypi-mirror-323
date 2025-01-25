import logging
from abc import ABC, abstractmethod
from pathlib import Path

from ..utils.recommenders_utils import is_fold_formatable


class Recommender(ABC):
    """
    Base class for recommendation systems.

    Attributes:
    - name: Name of the recommender system.
    - data_path: Path to the data.
    - predictions_path: Path for storing predictions.
    - logs_path: Path where logs are stored.
    - num_folds: Number of folds for cross-validation.
    """

    def __init__(
        self,
        predictions_path: str,
        logs_path: str,
        num_folds: int = None,
    ):

        if num_folds is not None:
            if num_folds <= 0:
                raise ValueError("'num_folds' must be a positive integer or None.")
            if not is_fold_formatable(predictions_path):
                raise Exception("Invalid 'predictions_path'.")
        
        self.predictions_path = predictions_path
        self.logs_path = logs_path
        self.num_folds = num_folds

        # Logger setup
        logs_dir = Path(self.logs_path).parent
        logs_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(f"{__name__}.{logs_path}")
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            file_handler = logging.FileHandler(logs_path, mode="w+", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s: %(levelname)-.1s %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    @abstractmethod
    def prepare_model(self, fold: int):
        if fold < 0:
            raise ValueError("'fold' must be a non-negative integer.")

    @abstractmethod
    def recommend(self, fold: int = None, K: int = 50):
        if fold and fold < 0:
            raise ValueError("'fold' must be a non-negative integer.")

        if K <= 0:
            raise ValueError("'K' must be a positive integer.")

        predictions_dir = Path(self.predictions_path).parent
        predictions_dir.mkdir(parents=True, exist_ok=True)

        return range(0, self.num_folds) if fold is None else [fold]
