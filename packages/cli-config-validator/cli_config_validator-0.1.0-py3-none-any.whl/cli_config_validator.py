#!/usr/bin/env python3
import argparse
import yaml
import json
import toml
import configparser
from pathlib import Path
from pydantic import BaseModel, ValidationError, field_validator
from typing import Any, Dict

# Function to load configuration files
def load_config(file_path: Path) -> dict:
    """
    Load configuration file into a dictionary.

    Parameters:
    - file_path (Path): The path to the configuration file.

    Returns:
    - dict: A dictionary containing the configuration data.

    Raises:
    - ValueError: If the file type is not supported.
    """
    if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    elif file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            return json.load(f)
    elif file_path.suffix == '.toml':
        return toml.load(file_path)
    elif file_path.suffix == '.properties':
        config = configparser.ConfigParser()
        config.read(file_path)
        return {section: dict(config[section]) for section in config.sections()}
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

# Function to merge multiple dictionaries
def merge_configs(configs: Dict[str, Any]) -> dict:
    """
    Merge multiple dictionaries into one.

    Parameters:
    configs (Dict[str, Any]): A dictionary where each key is a string representing a configuration name,
                              and the value is another dictionary containing the configuration settings.

    Returns:
    dict: A single dictionary that contains all the configurations from the input dictionaries.
          If there are overlapping keys, the values from later dictionaries will overwrite those from earlier ones.
    """
    merged_config = {}
    for config in configs:
        merged_config.update(config)
    return merged_config

# Main validation function
def validate_config(config_data: dict, model_class: BaseModel):
    """
    Validate the configuration data against the provided Pydantic model class.

    Parameters:
    config_data (dict): A dictionary containing the configuration data to be validated.
    model_class (BaseModel): The Pydantic model class that defines the expected structure of the configuration data.

    Returns:
    None

    Raises:
    ValidationError: If the configuration data does not match the expected structure defined by `model_class`.
    """
    try:
        model_instance = model_class(**config_data)
        print(f"Validation successful: {model_instance}")
    except ValidationError as e:
        print("Validation failed with errors:")
        print(e.json())

# CLI entry point
def main():
    parser = argparse.ArgumentParser(description="Validate merged configuration files against a Pydantic model.")
    parser.add_argument("-v", "--variables", nargs='+', type=Path, required=True, help="Paths to the configuration files.")
    parser.add_argument("-m", "--model-file", type=Path, required=True, help="Path to the Python file containing the Pydantic model class.")
    parser.add_argument("-c", "--class-model", type=str, required=True, help="Name of the Pydantic model class to validate against.")

    args = parser.parse_args()

    # Dynamically load the model class from the provided Python file
    model_file_path = args.model_file
    model_class_name = args.class_model

    try:
        model_globals = {}
        exec(model_file_path.read_text(), model_globals)
        model_class = model_globals[model_class_name]
        if not issubclass(model_class, BaseModel):
            raise TypeError(f"{model_class_name} is not a subclass of Pydantic BaseModel.")
    except Exception as e:
        print(f"Failed to load the model class: {e}")
        return

    # Load and merge all configuration files
    configs = []
    for config_path in args.variables:
        try:
            print(f"Loading file: {config_path}")
            config_data = load_config(config_path)
            configs.append(config_data)
        except Exception as e:
            print(f"Error processing file {config_path}: {e}")
            return

    merged_config = merge_configs(configs)

    # Validate the merged configuration
    print("Validating merged configuration...")
    validate_config(merged_config, model_class)

if __name__ == "__main__":
    # ./cli_config_validator.py -v config.yaml -v config2.yaml -m model.py -c ConfigModel
    main()

