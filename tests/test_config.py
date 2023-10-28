import pytest
import os

from pycmo.configs import config

config = config.get_config()

@pytest.mark.parametrize("requested_path, expected", [(k, True) for k in config.keys()])
def test_paths(requested_path, expected):
    assert os.path.exists(config[requested_path]) == expected