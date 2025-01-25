import yaml
import os
from recbole.config import Config
from recbole.data.utils import create_dataset, data_preparation
from recbole.trainer import Trainer


import corec.utils.recommenders_utils as recommenders_utils
from corec.recommenders.base_recommender import Recommender


class RecBoleRecommender(Recommender):
    """
    Base class for recommendation systems using the RecBole framework.
    """

    def __init__(self, *args, model_class: type, config_path: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.config_path = config_path
        self.model_class = model_class
        self.config = None
        self.dataset = None
        self.train_data = None
        self.valid_data = None
        self.test_data = None
        self.trainer = None

    def _load_and_prepare_data(self, fold: int):
        # Create specific config file for the fold
        with open(self.config_path, "r") as f:
            config_base = yaml.safe_load(f)

        config_fold = config_base.copy()
        config_fold["benchmark_filename"] = [
            f"f{fold}.train",
            f"f{fold}.valid",
            f"f{fold}.test",
        ]
        config_fold_path = os.path.splitext(self.config_path)[0] + f"_f{fold}.yaml"

        with open(config_fold_path, "w") as f:
            yaml.dump(config_fold, f, default_flow_style=True)

        with open(config_fold_path, "r") as f:
            config_fold = yaml.safe_load(f)

        # Configure the model
        self.logger.info("Configuring model")
        self.config = Config(
            model=self.name,
            dataset="clustered_bgg",
            config_file_list=[config_fold_path],
        )

        # Delete specific config file for the fold
        os.remove(config_fold_path)

        # Load the dataset based on the configuration
        self.logger.info("Loading dataset")
        self.dataset = create_dataset(self.config)

        # Prepare training, validation, and test datasets
        self.logger.info("Preparing data")
        self.train_data, self.valid_data, self.test_data = data_preparation(
            self.config, self.dataset
        )

    def evaluate_model(self):
        self.logger.info("Evaluating model")
        test_result = self.trainer.evaluate(self.test_data)
        self.logger.info("Test result: {}".format(test_result))

    def prepare_model(self, fold: int):
        super().prepare_model(fold)

        # Load and prepare the data
        self._load_and_prepare_data(fold)

        # Create the model
        self.create_model()

        # Create the trainer
        self.logger.info("Creating trainer")
        self.trainer = Trainer(self.config, self.model)

        # Train the model
        self.logger.info("Training model")
        best_valid_score, best_valid_result = self.trainer.fit(
            self.train_data, self.valid_data
        )

    def create_model(self):
        if not self.config or not self.train_data:
            self.logger.info("The recommender system is not ready to create the model.")

        self.model = self.model_class(self.config, self.train_data.dataset).to(
            self.config["device"]
        )

    def recommend(self, fold: int = None, K: int = 50):
        folds = super().recommend(fold, K)

        for fold in folds:
            self.logger.info("Started prediction for fold {}".format(fold))
            self.prepare_model(fold)

            self.logger.info("Extracting predictions")
            full_batch = recommenders_utils.create_new_batch(
                self.test_data.dataset.inter_feat,
                self.dataset.get_item_feature().numpy()["item_id"],
            )

            self.logger.info("Dividing batch")
            batches = recommenders_utils.divide_batches(
                full_batch, self.dataset.get_item_feature().numpy()["item_id"].shape[0]
            )

            for i, batch in enumerate(batches):
                if not i % 1000:
                    self.logger.info("Batch {} / {}".format(i, len(batches)))

                # Nos aseguramos de que el batch se procese
                # en el mismo dispositivo que el modelo
                for key in batch.keys():
                    batch[key] = batch[key].to(self.model.device)

                scores, indices = recommenders_utils.get_top_k(batch, self.model, K)

                # Liberamos espacio de la GPU
                for key in batch.keys():
                    batch[key] = batch[key].cpu()

                recommenders_utils.print_predictions_file(
                    self.predictions_path.format(fold=fold),
                    batch,
                    indices.cpu(),
                    scores.cpu(),
                    self.dataset,
                )
