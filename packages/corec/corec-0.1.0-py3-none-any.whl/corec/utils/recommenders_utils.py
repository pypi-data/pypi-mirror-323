import gzip
import os
from string import Formatter

# import torch
#
#
# def create_new_batch(initial_batch, item_ids):
#     """
#     Crea un nuevo batch a partir del batch inicial, repitiendo cada fila para cada identificador de item en item_ids.
#
#     Parámetros:
#     - initial_batch: Diccionario que contiene el batch inicial.
#     - item_ids: Lista de identificadores de items.
#
#     Devuelve:
#     - new_batch: Diccionario que contiene el nuevo batch.
#     """
#     # Obtener el tamaño del batch inicial y el número de items en item_ids
#     batch_size = initial_batch["user_id"].shape[0]
#     num_items = len(item_ids)
#
#     # Inicializar un nuevo batch con el mismo formato que el inicial
#     new_batch = {
#         key: torch.repeat_interleave(torch.tensor(value), num_items, dim=0)
#         for key, value in initial_batch.numpy().items()
#     }
#
#     # Modificar los item_ids en el nuevo batch
#     repeated_item_ids = torch.tensor(
#         item_ids, dtype=initial_batch["item_id"].dtype
#     ).repeat(batch_size)
#     new_batch["item_id"] = repeated_item_ids
#
#     # Incluir una nueva columna con los items_ids originales de test repetidos num_items veces
#     test_item_ids = torch.repeat_interleave(initial_batch["item_id"], num_items, dim=0)
#     new_batch["test_item_id"] = test_item_ids
#
#     return new_batch
#
#
# def divide_batches(new_batch, batch_size):
#     # Número total de batches
#     num_batches = (new_batch["user_id"].size(0) + batch_size - 1) // batch_size
#
#     # Crear una lista para almacenar los batches
#     batches = []
#
#     for i in range(num_batches):
#         batch = {}
#         start_idx = i * batch_size
#         end_idx = min((i + 1) * batch_size, new_batch["user_id"].size(0))
#
#         for key in new_batch:
#             batch[key] = new_batch[key][start_idx:end_idx]
#
#         batches.append(batch)
#
#     return batches
#
#
# def get_top_k(batch, model, k=10):
#     pred = model.predict(batch)
#     scores, indices = torch.topk(pred, k)
#     return scores, indices


def print_predictions_file(filepath, batch, indices, scores, dataset):
    if not filepath.endswith(".gzip"):
        filepath += ".gzip"

    if not os.path.exists(filepath):
        with gzip.open(filepath, "wt") as f:
            f.write("user_id:token\titem_id:token\tscore:float\ttest_item_id:token\n")

    with gzip.open(filepath, "at") as f:
        for i in range(indices.numpy().shape[0]):
            user_id = dataset.id2token("user_id", batch["user_id"][i].item())
            item_id = dataset.id2token("item_id", indices[i].item())
            score = scores[i].item()
            test_item_id = dataset.id2token("item_id", batch["test_item_id"][i].item())
            f.write(
                user_id
                + "\t"
                + item_id
                + "\t"
                + str(score)
                + "\t"
                + test_item_id
                + "\n"
            )


def is_fold_formatable(txt: str):
    format_placeholders = [
        tup[1] for tup in Formatter().parse(txt) if tup[1] is not None
    ]
    return len(format_placeholders) == 1 and "fold" in format_placeholders


def positive_integer_checker(arg_name: str, value: int):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"'{arg_name}' must be a positive integer.")
    return value


def non_negative_integer_checker(arg_name: str, value: int):
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"'{arg_name}' must be a non-negative integer.")
    return value
