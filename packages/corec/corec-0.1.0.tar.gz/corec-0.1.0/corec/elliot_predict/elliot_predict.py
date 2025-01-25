import gzip
import os
import re
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import yaml

from elliot.run import run_experiment


def prepare_temp_file(file_path: str):
    """
    Creates a temporary file containing the first three columns of the input file,
    formatted as a tab-separated values (TSV) file without a header.
    """    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as temp_file:
        with open(file_path, "r") as f_in:
            df = pd.read_csv(f_in, sep="\t")

        df = df.iloc[:, :3]
        df.to_csv(temp_file.name, sep="\t", index=False, header=False)

    return temp_file.name


def unify_elliot_predictions_files(
    folder_path: str, dest_folder_path: str, dest_filename: str, feat_names: list = None
):
    """
    Organizes prediction files from a folder by model, selects the latest file for each model,
    adds a header, compresses it into gzip format, and saves it to a specified destination folder.
    Older files are removed.
    """
    folder_path = Path(folder_path).resolve()
    dest_folder_path = Path(dest_folder_path).resolve()
    files = [file for file in folder_path.iterdir() if file.is_file()]

    model_files = {}
    pattern = r"^(?P<model>\w+)_"

    for file in files:
        match = re.match(pattern, file.name)
        model = match.group("model") if match else file.name.rsplit(".", 1)[0]

        if model not in model_files:
            model_files[model] = []
        model_files[model].append(file)

    for model, files in model_files.items():
        files.sort(key=lambda f: f.stat().st_ctime, reverse=True)
        last_file = files[0]

        model_folder = dest_folder_path / model
        model_folder.mkdir(parents=True, exist_ok=True)
        new_file_path = model_folder / dest_filename.format(model=model)

        with open(last_file, "rt+") as f_in:
            content = f_in.read()
            f_in.seek(0, 0)
            f_in.write("\t".join(feat_names) + "\n" + content)

        with open(last_file, "rb") as f_in:
            with gzip.open(new_file_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        for file in files:
            file.unlink()


def elliot_predict(
    train_file_path: str,
    test_file_path: str,
    config_file_path: str,
    valid_file_path: str = None,
):
    """
    Prepares temporary training, testing and optionally validation files, updates the configuration
    file for an 'elliot' experiment, runs the experiment, and cleans up the temporary files. Returns
    the path to the folder with prediction results.
    """
    temp_train_file_path = prepare_temp_file(train_file_path)
    temp_test_file_path = prepare_temp_file(test_file_path)

    with open(config_file_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    config["experiment"]["data_config"]["train_path"] = temp_train_file_path
    config["experiment"]["data_config"]["test_path"] = temp_test_file_path
    predictions_folder_path = config["experiment"]["path_output_rec_result"]

    if valid_file_path is not None:
        temp_valid_file_path = prepare_temp_file(valid_file_path)
        config["experiment"]["data_config"]["validation_path"] = temp_valid_file_path

    with open(config_file_path, "w") as config_file:
        yaml.safe_dump(config, config_file)

    run_experiment(config_file_path)

    os.remove(temp_train_file_path)
    os.remove(temp_test_file_path)

    return predictions_folder_path
