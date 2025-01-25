from math import sqrt

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.metrics.pairwise import cosine_similarity

from ..heuristic_recommender import HeuristicRecommender


def decode_time_context(time_ctx):
    num_ones = [1, 2, 4, 6, 10]
    time_index = np.argmax(time_ctx)
    decoded_time = np.zeros(10, dtype=int)
    decoded_time[: num_ones[time_index]] = 1
    return decoded_time


def decode_social_context(social_ctx):
    decoded_age = np.zeros(3, dtype=int)
    age_index = np.argmax(social_ctx[2:5]) if 1 in social_ctx[2:5] else 0
    decoded_age[:age_index] = 1
    return np.concatenate([social_ctx[:2], decoded_age, social_ctx[5:]])


def decode_context(context):
    decoded_time = decode_time_context(context[:5])
    decoded_social = decode_social_context(context[12:19])
    return np.concatenate([decoded_time, context[5:12], decoded_social])


class ContextSimilarityRecommender(HeuristicRecommender):
    MAX_DISTANCE = sqrt(10)

    def prepare_model(self, fold):
        super().prepare_model(fold)

        # Items context
        self.items_context = (
            self.data.drop(columns=["user_id:token", "rating:float"])
            .drop_duplicates()
            .sort_values("item_id:token")
            .reset_index(drop=True)
        )

        # Items ratings
        self.items_ratings = (
            self.data[["user_id:token", "item_id:token", "rating:float"]]
            .drop_duplicates(subset=["user_id:token", "item_id:token"])
            .pivot(
                columns="user_id:token", index="item_id:token", values="rating:float"
            )
            .fillna(0)
        )

        # Convertimos `self.data` en una matriz de `numpy`
        self.data_np = self.data[
            ["item_id:token", "user_id:token", "rating:float"]
        ].to_numpy()

        # Creamos un diccionario id-index para los items
        self.item_id_to_index = dict(
            zip(self.items_context["item_id:token"], self.items_context.index)
        )
        self.items_ids = list(self.item_id_to_index.keys())

        self.decode_items_contexts()
        self.fit()

    def _rating_similarity_matrix(self):
        sim_matrix = cosine_similarity(self.items_ratings.fillna(0))
        np.fill_diagonal(sim_matrix, 0)
        return sim_matrix

    def fit(self):
        self.logger.info("Calculating rating similarity matrix...")
        self.rating_similarity_matrix = self._rating_similarity_matrix()

    def decode_items_contexts(self):
        self.logger.info("Decoding contexts...")
        encoded_contexts = self.items_context.drop("item_id:token", axis=1).values
        self.decoded_ctx_matrix = np.apply_along_axis(
            decode_context, 1, encoded_contexts
        )

    def predict(self, user_id, item_id, context):
        # Extraemos el item_id a predecir del conjunto de entrenamiento
        # y obtenemos los respectivos índices
        items_ids = list(self.items_ids)
        items_ids.remove(item_id)
        item_indices = np.array([self.item_id_to_index[i] for i in items_ids])

        # Desglose de los contextos
        ctx_matrix_time = self.decoded_ctx_matrix[:, :10]
        ctx_matrix_mood = self.decoded_ctx_matrix[:, 10:17]
        ctx_matrix_social = self.decoded_ctx_matrix[:, 17:]

        decoded_ctx = decode_context(context)
        ctx_time = decoded_ctx[:10]
        ctx_mood = decoded_ctx[10:17]
        ctx_social = decoded_ctx[17:]

        # Cálculo de similitudes respecto al contexto
        time_similarity = 1 - (
            cdist(ctx_matrix_time, [ctx_time], metric="euclidean").flatten()
            / self.MAX_DISTANCE
        )
        mood_similarity = (
            1 - cdist(ctx_matrix_mood, [ctx_mood], metric="cosine").flatten()
        )
        social_similarity = (
            1 - cdist(ctx_matrix_social, [ctx_social], metric="cosine").flatten()
        )
        mood_similarity = np.nan_to_num(mood_similarity, nan=0)
        social_similarity = np.nan_to_num(social_similarity, nan=0)

        ctx_similarities = (time_similarity + mood_similarity + social_similarity) / 3

        # Cálculo de similitudes respecto al rating
        item_index = self.item_id_to_index[item_id]
        rating_similarities = self.rating_similarity_matrix[item_index, item_indices]

        # Producto de similitudes
        sim_products = (
            rating_similarities
            * np.delete(
                ctx_similarities, item_index
            )  # ctx de entrada - ctx's de entrenamiento
            * ctx_similarities[item_index]  # ctx de entrada - ctx de interés
        )

        # Extraemos los ratings de los items usando el diccionario rating_dict
        # Si el usuario no lo puntuó el valor es 0
        items_ratings = np.array([self.user_ratings_dict.get(i, 0) for i in items_ids])

        # Calculamos los sumatorios
        sumatorio_a = np.dot(
            sim_products, items_ratings
        )  # suma de rating * similitud para los items valorados por el usuario
        sumatorio_b = np.sum(sim_products)

        return sumatorio_a / sumatorio_b if sumatorio_b != 0 else 0

    def get_top_k(self, user_id, context, K: int = 50):
        super().get_top_k(user_id, context, K)

        # Filtramos de antemano los ratings del usuario
        user_ratings = self.data_np[(self.data_np[:, 1] == user_id)]

        # Creamos un diccionario item_id-rating para un acceso rápido
        item_ids_in_data = user_ratings[:, 0].astype(int)
        ratings_in_data = user_ratings[:, 2].astype(float)
        self.user_ratings_dict = dict(zip(item_ids_in_data, ratings_in_data))

        # Calculamos las predicciones para todos los items de entrenamiento
        predictions = np.array(
            [self.predict(user_id, item_id, context) for item_id in self.items_ids]
        )

        # Seleccionamos los K con mayor puntuación
        indices = np.argpartition(predictions, -K)[-K:]
        sorted_indices = indices[np.argsort(predictions[indices])][::-1]

        return np.array(self.items_ids)[sorted_indices], predictions[sorted_indices]
