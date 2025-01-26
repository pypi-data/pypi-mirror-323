from contextlib import nullcontext as does_not_raise

import pytest

from src.repo_mapper import io, utils

from .conftest import (
    VALID_MAP_ALL_FILES,
    VALID_MAP_NO_SRC_DIR,
    VALID_MAP_PY_MD_ONLY,
    VALID_MAP_PY_ONLY,
    VALID_MAP_TOML_ONLY,
)


@pytest.mark.parametrize(
    "allowed_extensions, ignore_dirs, expected_result, expected_context",
    [
        (None, None, VALID_MAP_ALL_FILES, does_not_raise()),
        ([".py"], None, VALID_MAP_PY_ONLY, does_not_raise()),
        ([".toml"], None, VALID_MAP_TOML_ONLY, does_not_raise()),
        ([".py", ".md"], None, VALID_MAP_PY_MD_ONLY, does_not_raise()),
        ([], ["src"], VALID_MAP_NO_SRC_DIR, does_not_raise()),
    ],
)
def test_create_repo_map(
    get_mock_data_path,
    get_mock_data_readme_path,
    allowed_extensions,
    ignore_dirs,
    expected_result,
    expected_context,
):
    with expected_context:
        utils.create_repo_map(
            get_mock_data_path,
            get_mock_data_readme_path,
            allowed_extensions,
            ignore_dirs,
        )
        text = io.read_file(get_mock_data_readme_path)
        assert expected_result in text


@pytest.mark.parametrize(
    "files, ignore_dirs, expected_result, expected_context",
    [
        (
            [
                "project/src/main.py",
                "project/src/utils/helpers.py",
                "project/src/utils/__init__.py",
                "project/src/data/data_loader.py",
                "project/tests/test_main.py",
                "project/docs/README.md",
                "project/docs/tutorial/tutorial.md",
                "project/configs/example_config.yaml",
                "project/__pycache__/cached_file.pyc",
                "project/build/output.txt",
                "project/README.md",
                "project/some.toml",
            ],
            [],
            (
                "# generated repo map\n```\n└── project\n    "
                "├── __pycache__\n    │   └── cached_file.pyc\n    ├── build\n    "
                "│   └── output.txt\n    ├── configs\n    │   └── example_config.yaml\n    "
                "├── docs\n    │   ├── tutorial\n    │   │   └── tutorial.md\n    │   "
                "└── README.md\n    ├── src\n    │   ├── data\n    "
                "│   │   └── data_loader.py\n    │   ├── utils\n    │   "
                "│   ├── __init__.py\n    │   │   └── helpers.py\n    "
                "│   └── main.py\n    ├── tests\n    │   └── test_main.py\n    "
                "├── README.md\n    └── some.toml\n::\n```"
            ),
            does_not_raise(),
        )
    ],
)
def test_get_file_tree(files, ignore_dirs, expected_result, expected_context):
    with expected_context:
        assert utils.get_file_tree(files, ignore_dirs) == expected_result
