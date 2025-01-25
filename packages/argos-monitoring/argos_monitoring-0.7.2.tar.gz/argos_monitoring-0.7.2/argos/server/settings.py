"""Pydantic schemas for server"""
from pathlib import Path

import yaml
from yamlinclude import YamlIncludeConstructor

from argos.schemas.config import Config


def read_yaml_config(filename: str) -> Config:
    parsed = _load_yaml(filename)
    return Config(**parsed)


def _load_yaml(filename: str):
    base_dir = Path(filename).resolve().parent
    YamlIncludeConstructor.add_to_loader_class(
        loader_class=yaml.FullLoader, base_dir=str(base_dir)
    )

    with open(filename, "r", encoding="utf-8") as stream:
        return yaml.load(stream, Loader=yaml.FullLoader)
