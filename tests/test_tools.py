import pytest
import datetime
import os

from pycmo.lib.tools import *
from pycmo.configs.config import get_config

config = get_config()

parse_datetime_test_parameters = [
    (0, datetime(1, 1, 1)),
    (636374376000000000, datetime(2017, 8, 4, 10, 0)),
    (626325877650000000, datetime(1985, 10, 1, 5, 2, 45)),
]

ticks_to_unix_test_parameters = [
    (626325877650000000, 496990965),
]

@pytest.mark.parametrize("time_int, expected", parse_datetime_test_parameters)
def test_parse_datetime(time_int, expected):
    assert parse_datetime(time_int) == expected

@pytest.mark.parametrize("ticks, expected", ticks_to_unix_test_parameters)
def test_ticks_to_unix(ticks, expected):
    assert ticks_to_unix(ticks) == expected

def test_clean_up_steps():
    steps_folder_path = config['observation_path']
    test_xml_file_paths = [os.path.join(steps_folder_path, f'test_{i}.xml') for i in range(2)]

    for test_xml_file in test_xml_file_paths:
        if os.path.exists(test_xml_file):
            os.remove(test_xml_file)

        with open(test_xml_file, 'w') as f:
            f.write('test')
    
    clean_up_steps(steps_folder_path)

    for test_xml_file in test_xml_file_paths:
        assert not os.path.exists(test_xml_file)
    
    assert os.path.exists(os.path.join(steps_folder_path, 'placeholder.txt'))

def test_euclidean_distance():
    ...

def test_discretize_2d_space():
    ...

def test_get_nearest_point_from_location():
    ...

def test_cmo_steam_observation_file_to_xml():
    observation_file_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", 'test_steam_observation.inst')
    xml_string = cmo_steam_observation_file_to_xml(observation_file_path)
    assert isinstance(xml_string, str)
    assert len(xml_string) > 1

# def test_window_exists():
#     window_name = "Side selection and briefing"
#     assert window_exists(window_name=window_name) == False

# def test_send_key_press():
#     key = "{ESC}"
#     window_name = ""
#     assert send_key_press(key=key, window_name=window_name) == True
