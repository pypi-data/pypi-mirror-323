from abc import abstractmethod
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import numpy as np
import pandas as pd

from corec.recommenders.base_recommender import Recommender

from ..utils.recommenders_utils import (
    is_fold_formatable,
    positive_integer_checker,
    non_negative_integer_checker,
)


class HeuristicRecommender(Recommender):
    def __init__(
        self,
        train_data_path: str,
        test_data_path: str,
        chunk_size: int,
        valid_data_path: str = None,
        user_id_idx: int = 0,
        item_id_idx: int = 1,
        rating_idx: int = 2,
        data_sep: str = "\t",
        num_workers: int = 1,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if self.num_folds is not None:
            if not is_fold_formatable(train_data_path):
                raise ValueError("Invalid 'train_data_path'.")
            if not is_fold_formatable(test_data_path):
                raise ValueError("Invalid 'test_data_path'.")

        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.valid_data_path = valid_data_path
        self.data_sep = data_sep

        self.user_id_idx = non_negative_integer_checker("user_id_idx", user_id_idx)
        self.item_id_idx = non_negative_integer_checker("item_id_idx", item_id_idx)
        self.rating_idx = non_negative_integer_checker("rating_idx", rating_idx)
        self.chunk_size = positive_integer_checker("chunk_size", chunk_size)
        self.num_workers = positive_integer_checker("num_workers", num_workers)

    def prepare_model(self, fold):
        self.test_df = pd.read_csv(
            self.test_data_path.format(fold=fold), sep=self.data_sep
        )
        train_df = pd.read_csv(
            self.train_data_path.format(fold=fold), sep=self.data_sep
        )
        self.data = train_df

        if self.valid_data_path:
            valid_df = pd.read_csv(
                self.valid_data_path.format(fold=fold), sep=self.data_sep
            )
            self.data = pd.concat([self.data, valid_df])

        context_idxs = [
            idx
            for idx in range(self.data.shape[1])
            if idx not in [self.user_id_idx, self.item_id_idx, self.rating_idx]
        ]

        std_col_order = [
            self.user_id_idx,
            self.item_id_idx,
            self.rating_idx,
        ] + context_idxs
        self.data = self.data.iloc[:, std_col_order]

    @abstractmethod
    def get_top_k(self, user_id, context, K):
        pass

    def recommend(self, fold: int = None, K: int = 50):
        folds = super().recommend(fold, K)

        for fold in folds:
            self.logger.info("Started prediction for fold {}".format(fold))
            self.prepare_model(fold)

            test_matrix = self.test_df.to_numpy()
            num_rows = test_matrix.shape[0]
            num_chunks = num_rows // self.chunk_size + (
                1 if num_rows % self.chunk_size != 0 else 0
            )
            chunks_ids = np.arange(num_chunks)

            self.logger.info(
                f"Starting processing chunks for fold {fold}, using {num_chunks} workers"
            )

            results = None
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                worker = partial(
                    self.process_chunk, fold=fold, all_data=test_matrix, K=K
                )
                results = executor.map(worker, chunks_ids)

            results = np.vstack(results)

            results_cols_types = {
                "user_id:token": int,
                "item_id:token": int,
                "score:float": float,
                "test_item_id:token": int,
            }
            results_df = pd.DataFrame(results, columns=results_cols_types.keys())
            results_df = results_df.astype(results_cols_types)

            results_df.to_csv(
                self.predictions_path.format(fold=fold),
                sep="\t",
                index=False,
                compression="gzip",
            )

            self.logger.info(f"Finished fold {fold}")

    def process_chunk(self, chunk_id, fold, all_data, K):
        self.logger.info(f"Processing chunk {chunk_id} for fold {fold}")

        if (chunk_id + 1) * self.chunk_size < all_data.shape[0]:
            chunk = all_data[
                chunk_id * self.chunk_size : (chunk_id + 1) * self.chunk_size
            ]
        else:
            chunk = all_data[chunk_id * self.chunk_size :]

        self.logger.info(
            "Executing from row {} to row {}".format(
                chunk_id * self.chunk_size,
                (chunk_id + 1) * self.chunk_size
                if (chunk_id + 1) * self.chunk_size < all_data.shape[0]
                else all_data.shape[0],
            )
        )

        predictions = []
        last_percentage_logged = 0

        for i, row in enumerate(chunk):
            current_percentage = int(i / chunk.shape[0] * 100)

            if current_percentage >= last_percentage_logged + 10:
                self.logger.info(f"Processed {current_percentage}% of chunk {chunk_id}")
                last_percentage_logged = current_percentage

            user_id = row[0]
            test_item_id = row[1]
            context = row[3:]
            items, scores = self.get_top_k(user_id, context, K)

            result_matrix = np.zeros((items.shape[0], 4))
            result_matrix[:, 0] = user_id
            result_matrix[:, 1] = items
            result_matrix[:, 2] = scores
            result_matrix[:, 3] = test_item_id
            predictions.append(result_matrix)

        self.logger.info(f"Finished chunk {chunk_id} for fold {fold}")

        return np.vstack(predictions)
