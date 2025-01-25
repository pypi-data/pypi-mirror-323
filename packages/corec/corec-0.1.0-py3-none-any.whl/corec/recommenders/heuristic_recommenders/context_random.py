import numpy as np

from ..heuristic_recommender import HeuristicRecommender


class ContextRandomRecommender(HeuristicRecommender):
    def get_top_k(self, _, context, K: int = 50):
        mask = (self.data.iloc[:, 3:] == context).all(axis=1)
        df_context = self.data[mask]

        distinct_items = np.unique(df_context.iloc[:, 1].values)
        N = min(distinct_items.shape[0], K)

        np.random.shuffle(distinct_items)
        scores = np.arange(N, 0, -1)

        return distinct_items[:N], scores[:N]
