import pytest
import os

from pycmo.configs.config import get_config

config = get_config()

@pytest.mark.parametrize("requested_path, expected", [(k, True) for k in config.keys()])
def test_paths(requested_path, expected):
    if requested_path != 'command_mo_version' and requested_path != "gymnasium":
        assert os.path.exists(config[requested_path]) == expected