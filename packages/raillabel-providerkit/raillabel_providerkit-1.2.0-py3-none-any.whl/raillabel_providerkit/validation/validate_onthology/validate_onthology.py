# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import jsonschema
import raillabel
import yaml

from raillabel_providerkit.exceptions import OnthologySchemaError
from raillabel_providerkit.validation import Issue

from ._onthology_classes._onthology import _Onthology


def validate_onthology(scene: raillabel.Scene, onthology_input: dict | Path) -> list[Issue]:
    """Validate a scene based on the classes and attributes.

    Parameters
    ----------
    scene : raillabel.Scene
        The scene containing the annotations.
    onthology_input : dict or Path
        Onthology YAML-data or file containing a information about all classes and their
        attributes. The onthology must adhere to the onthology_schema. If a path is provided, the
        file is loaded as a YAML.

    Returns
    -------
    list[Issue]
        list of all onthology errors in the scene. If an empty list is returned, then there are no
        errors present.

    """
    if isinstance(onthology_input, Path):
        onthology_input = _load_onthology(Path(onthology_input))

    _validate_onthology_schema(onthology_input)

    onthology = _Onthology.fromdict(onthology_input)

    return onthology.check(scene)


def _load_onthology(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def _validate_onthology_schema(onthology: dict | None) -> None:
    schema_path = Path(__file__).parent / "onthology_schema_v2.yaml"

    with schema_path.open() as f:
        onthology_schema = yaml.safe_load(f)

    validator = jsonschema.Draft7Validator(schema=onthology_schema)

    schema_errors = ""
    for error in validator.iter_errors(onthology):
        schema_errors += f"${error.json_path[1:]}: {error.message}\n"

    if schema_errors != "":
        raise OnthologySchemaError(
            "The provided onthology is not valid. The following errors have been found:\n"
            + schema_errors
        )
