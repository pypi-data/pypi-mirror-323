from ..heuristic_recommender import HeuristicRecommender


class ContextPopRecommender(HeuristicRecommender):
    def get_top_k(self, _, context, K: int = 50):
        mask = (self.data.iloc[:, 3:] == context).all(axis=1)
        df_context = self.data[mask]

        df_context = (
            df_context.groupby(df_context.iloc[:, 1])
            .size()
            .reset_index(name="count")
        )
        top_k = df_context.nlargest(K, "count")

        return (
            top_k.iloc[:, 0].values,
            top_k["count"].values,
        )
