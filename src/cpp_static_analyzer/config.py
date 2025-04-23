"""Configuration file processor."""

import pathlib as plib
import os
import sys
import yaml


class Config:
    """Configuration object."""

    @classmethod
    def default_config(cls):
        """ Default configurations. """
        return {
            'compile_commands': './compile_commands.json',
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

    @classmethod
    def write_default_config_to_stdout(cls):
        """ Dump default config to stdout. """
        default_config = cls.default_config()
        sys.stdout.write(yaml.dump(default_config))

    def __init__(self, yml):
        if isinstance(yml, str):
            yaml_file_path = yml
            if yaml_file_path == '':
                config = Config.default_config()
            else:
                config = Config.load(yaml_file_path)
        else:
            config = yml

        self._path_converters = \
            Config.get_path_converters_from_config(config)

        self._clang_tidy_executable = \
            Config.get_clang_tidy_executable_path_from_config(config)
        self._clang_tidy_config_file = \
            Config.get_clang_tidy_config_file_path_from_config(config)
        self._clang_tidy_additional_options = \
            Config.get_clang_tidy_additional_options_from_config(config)

        self._clang_executable = \
            Config.get_clang_executable_path_from_config(config)
        self._clang_additional_options = \
            Config.get_clang_additional_options_from_config(config)

        self._compile_commands = \
            Config.get_compile_commands_from_config(config)

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

    @classmethod
    def search_for_config_file(cls, path):
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

    @classmethod
    def load(cls, yaml_file_path):
        """Load config.yml."""
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError:
            print(f'{yaml_file_path} not found.')
            return cls.default_config()
        except yaml.YAMLError:
            print(f'{yaml_file_path} is invalid.')
            return cls.default_config()

    @classmethod
    def get_path_converters_from_config(cls, config):
        """Get path converter settings."""
        if 'path_converters' in config:
            return config['path_converters']
        return cls.default_config()['path_converters']

    @classmethod
    def get_clang_tidy_setting_from_config(cls, config, key):
        """ Get settings for clang-tidy. """
        default_config = cls.default_config()
        default_clang_tidy_settings = default_config['clang-tidy']
        if 'clang-tidy' not in config:
            return default_clang_tidy_settings[key]
        clang_tidy_settings = config['clang-tidy']
        if key not in clang_tidy_settings:
            return default_clang_tidy_settings[key]
        return clang_tidy_settings[key]

    @classmethod
    def get_clang_setting_from_config(cls, config, key):
        """ Get settings for clang. """
        default_config = cls.default_config()
        default_clang_settings = default_config['clang']
        if 'clang' not in config:
            return default_clang_settings[key]
        clang_settings = config['clang']
        if key not in clang_settings:
            return default_clang_settings[key]
        return clang_settings[key]

    @classmethod
    def get_setting_from_config(cls, config, key):
        """Get setting using key."""
        if key not in config:
            default_config = cls.default_config()
            return default_config[key]
        return config[key]

    @classmethod
    def get_clang_tidy_executable_path_from_config(cls, config):
        """Get path to clang-tidy executable."""
        executable_path = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'executable_path')
        return executable_path

    @classmethod
    def get_clang_tidy_config_file_path_from_config(cls, config):
        """Get .clang-tidy file path settings."""
        config_file_path = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'config_file_path')
        return config_file_path

    @classmethod
    def get_clang_tidy_additional_options_from_config(cls, config):
        """Get clang-tidy additional options."""
        additional_options = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'additional_options')
        return additional_options

    @classmethod
    def get_clang_executable_path_from_config(cls, config):
        """Get path to clang executable."""
        executable_path = \
            cls.get_clang_setting_from_config(config,
                                              'executable_path')
        return executable_path

    @classmethod
    def get_clang_additional_options_from_config(cls, config):
        """Get additional options for clang."""
        additional_options = \
            cls.get_clang_setting_from_config(config,
                                              'additional_options')
        return additional_options

    @classmethod
    def get_compile_commands_from_config(cls, config):
        """Get path to compile commands."""
        compile_commands = \
            cls.get_setting_from_config(config, 'compile_commands')
        return compile_commands
