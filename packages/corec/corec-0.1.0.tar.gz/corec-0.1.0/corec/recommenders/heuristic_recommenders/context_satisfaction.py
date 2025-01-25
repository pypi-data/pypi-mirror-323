import numpy as np

from ...utils.recommenders_utils import non_negative_integer_checker
from ..heuristic_recommender import HeuristicRecommender


# NOTE: Located out of the recommender class to import it from 'evaluation' module
def context_satisfaction(ctx_rec, ctx_i_matrix, alpha=0):
    intersect = np.sum((ctx_i_matrix == ctx_rec) & (ctx_i_matrix == 1), axis=1)
    union = np.sum((ctx_i_matrix | ctx_rec), axis=1)
    diff = np.sum((ctx_rec == 1) & (ctx_i_matrix == 0), axis=1)
    union = np.where(union == 0, 1, union)

    return intersect / (union + alpha * diff / np.sum(ctx_rec))


class ContextSatisfactionRecommender(HeuristicRecommender):
    def __init__(
        self,
        alpha: int = 0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.alpha = non_negative_integer_checker("alpha", alpha)

    def prepare_model(self, fold):
        super().prepare_model(fold)

        self.ncols = self.data.shape[1]
        self.item_ctx_df = self.data.iloc[
            :, [1] + list(range(3, self.ncols))
        ].drop_duplicates()

    def get_top_k(self, _, context, K: int = 50):
        ctx_rec = np.array(context).astype(int)
        cxt_i_matrix = self.item_ctx_df.iloc[:, 1 : self.ncols - 2].values
        self.item_ctx_df["sat"] = context_satisfaction(
            ctx_rec, cxt_i_matrix, self.alpha
        )
        top_k = self.item_ctx_df.nlargest(K, "sat")

        return (
            top_k.iloc[:, 0].values,
            top_k["sat"].values,
        )
