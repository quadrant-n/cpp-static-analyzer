"""Configuration file processor."""

import pathlib as plib
import os
import yaml

default_config = {
    'compile_commands': '',
    'clang': {
        'executable_path': 'clang',
        'additional_options': {}
    },
    'clang-tidy': {
        'executable_path': 'clang-tidy',
        'config_file_path': './.clang-tidy',
        'additional_options': {}
    },
    'path_converters': {},
}


def search_for_config_file(path):
    """Search for .cpp-static-analyzer."""
    current_path = plib.Path(path)
    if current_path.is_file():
        current_path = current_path.parent
    parents = current_path.parents
    for parent in parents:
        config_file_path = os.path.join(parent.as_posix(),
                                        '.cpp-static-analyzer')
        if os.path.exists(config_file_path):
            return config_file_path
    return ''


def load(yaml_file_path):
    """Load config.yml."""
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f'{yaml_file_path} not found.')
        return default_config
    except yaml.YAMLError:
        print(f'{yaml_file_path} is invalid.')
        return default_config
    print(f'Error loading {yaml_file_path}')
    return default_config


def get_path_converters(config):
    """Get path converter settings."""
    if 'path_converters' in config:
        return config['path_converters']
    return default_config['path_converters']


def _get_clang_tidy_setting(config, key):
    default_clang_tidy_settings = default_config['clang-tidy']
    if 'clang-tidy' not in config:
        return default_clang_tidy_settings[key]
    clang_tidy_settings = config['clang-tidy']
    if key not in clang_tidy_settings:
        return default_clang_tidy_settings[key]
    return clang_tidy_settings[key]


def _get_clang_setting(config, key):
    default_clang_settings = default_config['clang']
    if 'clang' not in config:
        return default_clang_settings[key]
    clang_settings = config['clang']
    if key not in clang_settings:
        return default_clang_settings[key]
    return clang_settings[key]


def _get_setting(config, key):
    """Get setting using key."""
    if key not in config:
        return default_config[key]
    return config[key]


def get_clang_tidy_executable_path(config):
    """Get path to clang-tidy executable."""
    executable_path = _get_clang_tidy_setting(config, 'executable_path')
    return executable_path


def get_clang_tidy_config_file_path(config):
    """Get .clang-tidy file path settings."""
    config_file_path = _get_clang_tidy_setting(config, 'config_file_path')
    return config_file_path


def get_clang_tidy_additional_options(config):
    """Get clang-tidy additional options."""
    additional_options = _get_clang_tidy_setting(config, 'additional_options')
    return additional_options


def get_clang_executable_path(config):
    """Get path to clang executable."""
    executable_path = _get_clang_setting(config, 'executable_path')
    return executable_path


def get_clang_additional_options(config):
    """Get additional options for clang."""
    additional_options = _get_clang_setting(config, 'additional_options')
    return additional_options


def get_compile_commands(config):
    """Get path to compile commands."""
    compile_commands = _get_setting(config, 'compile_commands')
    return compile_commands


class Config:
    """Configuration object."""

    def __init__(self, yml):
        if isinstance(yml, str):
            yaml_file_path = yml
            if yaml_file_path == '':
                config = default_config
            else:
                config = load(yaml_file_path)
        else:
            config = yml

        self._path_converters = get_path_converters(config)

        self._clang_tidy_executable = get_clang_tidy_executable_path(config)
        self._clang_tidy_config_file = get_clang_tidy_config_file_path(config)
        self._clang_tidy_additional_options = \
            get_clang_tidy_additional_options(config)

        self._clang_executable = get_clang_executable_path(config)
        self._clang_additional_options = get_clang_additional_options(config)

        self._compile_commands = get_compile_commands(config)

    def get_path_converters(self):
        """Get path converter."""
        return self._path_converters

    def get_clang_tidy_executable(self):
        """Get clang-tidy executable path."""
        return self._clang_tidy_executable

    def get_clang_tidy_config_file(self):
        """Get path to config file."""
        return self._clang_tidy_config_file

    def get_clang_tidy_additional_options(self):
        """Get additional options."""
        return self._clang_tidy_additional_options

    def get_compile_commands(self):
        """Get path to compile commands."""
        return self._compile_commands

    def get_clang_executable(self):
        """Get path to clang executable."""
        return self._clang_executable

    def get_clang_additional_options(self):
        """Get clang additional options."""
        return self._clang_additional_options
