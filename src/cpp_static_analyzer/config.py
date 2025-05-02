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
            'compile_commands': 'compile_commands.json',
            'compile_commands_pkl': '',
            'number_of_jobs': 1,
            'output_directory': 'out',
            'error_directory': '',
            'clang': {
                'enabled': True,
                'executable_path': 'clang++',
                'additional_options': {},
                'diagnostic_directory': ''
            },
            'clang-tidy': {
                'enabled': True,
                'executable_path': 'clang-tidy',
                'config_file_path': '.clang-tidy',
                'additional_options': {}
            }
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

        self._clang_tidy_executable = \
            Config._get_clang_tidy_executable_path_from_config(config)
        self._clang_tidy_config_file = \
            Config._get_clang_tidy_config_file_path_from_config(config)
        self._clang_tidy_additional_options = \
            Config._get_clang_tidy_additional_options_from_config(config)
        self._clang_tidy_enabled = \
            Config._get_clang_tidy_enabled_from_config(config)

        self._clang_executable = \
            Config._get_clang_executable_path_from_config(config)
        self._clang_additional_options = \
            Config._get_clang_additional_options_from_config(config)
        self._clang_enabled = \
            Config._get_clang_enabled_from_config(config)
        self._clang_diagnostic_directory = \
            Config._get_clang_diagnostic_directory_from_config(config)

        self._compile_commands = \
            Config._get_compile_commands_from_config(config)
        self._compile_commands_pkl = \
            Config._get_compile_commands_pkl_from_config(config)

        self._number_of_jobs = \
            Config._get_number_of_jobs_from_config(config)

        self._output_directory = \
            Config._get_output_directory_from_config(config)
        self._error_directory = \
            Config._get_error_directory_from_config(config)

    def get_clang_tidy_executable(self):
        """Get clang-tidy executable path."""
        return self._clang_tidy_executable

    def get_clang_tidy_config_file(self):
        """Get path to config file."""
        return self._clang_tidy_config_file

    def get_clang_tidy_additional_options(self):
        """Get additional options."""
        return self._clang_tidy_additional_options

    def is_clang_tidy_enabled(self):
        """Is clang-tidy enabled."""
        return self._clang_tidy_enabled

    def set_clang_tidy_enabled(self, enabled):
        """Set clang-tidy enabled."""
        self._clang_tidy_enabled = enabled

    def get_compile_commands(self):
        """Get path to compile commands."""
        return self._compile_commands

    def get_compile_commands_pkl(self):
        """Get path to compile commands PKL."""
        return self._compile_commands_pkl

    def get_clang_executable(self):
        """Get path to clang executable."""
        return self._clang_executable

    def get_clang_additional_options(self):
        """Get clang additional options."""
        return self._clang_additional_options

    def is_clang_enabled(self):
        """Is clang enabled."""
        return self._clang_enabled

    def set_clang_enabled(self, enabled):
        """Set clang enabled."""
        self._clang_enabled = enabled

    def get_clang_diagnostic_directory(self):
        """Get path to plist directory."""
        return self._clang_diagnostic_directory

    def get_number_of_jobs(self):
        """Get number of jobs."""
        return self._number_of_jobs

    def get_output_directory(self):
        """Get output directory."""
        return self._output_directory

    def get_error_directory(self):
        """Get error directory."""
        return self._error_directory

    @classmethod
    def _get_config_file_path(cls, posix_path):
        config_file_path = os.path.join(posix_path,
                                        '.cpp-static-analyzer')
        if os.path.exists(config_file_path):
            return config_file_path
        return ''

    @classmethod
    def search_for_config_file(cls, path):
        """Search for .cpp-static-analyzer."""
        if not os.path.exists(path):
            return ''
        current_path = plib.Path(path)
        if current_path.is_dir():
            found_path = cls._get_config_file_path(current_path.as_posix())
            if found_path != '':
                return found_path
        if current_path.is_file():
            current_path = current_path.parent
        parents = current_path.parents
        for parent in parents:
            config_file_path = cls._get_config_file_path(parent.as_posix())
            if config_file_path != '':
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
    def get_clang_tidy_setting_from_config(cls, config, key,
                                           replace_empty=False):
        """ Get settings for clang-tidy. """
        default_config = cls.default_config()
        default_clang_tidy_settings = default_config['clang-tidy']
        if 'clang-tidy' not in config:
            return default_clang_tidy_settings[key]
        clang_tidy_settings = config['clang-tidy']
        if key not in clang_tidy_settings:
            return default_clang_tidy_settings[key]
        if replace_empty and clang_tidy_settings[key] == '':
            return default_clang_tidy_settings[key]
        return clang_tidy_settings[key]

    @classmethod
    def get_clang_setting_from_config(cls, config, key, replace_empty=False):
        """ Get settings for clang. """
        default_config = cls.default_config()
        default_clang_settings = default_config['clang']
        if 'clang' not in config:
            return default_clang_settings[key]
        clang_settings = config['clang']
        if key not in clang_settings:
            return default_clang_settings[key]
        if replace_empty and clang_settings[key] == '':
            return default_clang_settings[key]

        return clang_settings[key]

    @classmethod
    def _get_setting_from_config(cls, config, key, replace_empty=False):
        """Get setting using key."""
        if key not in config:
            default_config = cls.default_config()
            return default_config[key]
        if replace_empty and config[key] == '':
            default_config = cls.default_config()
            return default_config[key]
        return config[key]

    @classmethod
    def _get_clang_tidy_executable_path_from_config(cls, config):
        """Get path to clang-tidy executable."""
        executable_path = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'executable_path', True)
        return executable_path

    @classmethod
    def _get_clang_tidy_config_file_path_from_config(cls, config):
        """Get .clang-tidy file path settings."""
        config_file_path = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'config_file_path', True)
        return config_file_path

    @classmethod
    def _get_clang_tidy_additional_options_from_config(cls, config):
        """Get clang-tidy additional options."""
        additional_options = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'additional_options')
        return additional_options

    @classmethod
    def _get_clang_tidy_enabled_from_config(cls, config):
        """Get clang-tidy enable flag."""
        enabled = \
            cls.get_clang_tidy_setting_from_config(config,
                                                   'enabled')
        return enabled

    @classmethod
    def _get_clang_executable_path_from_config(cls, config):
        """Get path to clang executable."""
        executable_path = \
            cls.get_clang_setting_from_config(config,
                                              'executable_path', True)
        return executable_path

    @classmethod
    def _get_clang_additional_options_from_config(cls, config):
        """Get additional options for clang."""
        additional_options = \
            cls.get_clang_setting_from_config(config,
                                              'additional_options')
        return additional_options

    @classmethod
    def _get_clang_enabled_from_config(cls, config):
        """Get clang enable flag."""
        enabled = \
            cls.get_clang_setting_from_config(config,
                                              'enabled')
        return enabled

    @classmethod
    def _get_clang_diagnostic_directory_from_config(cls, config):
        """Get path to diagnostic directory."""
        diagnostic_directory = \
            cls.get_clang_setting_from_config(config,
                                              'diagnostic_directory')
        return diagnostic_directory

    @classmethod
    def _get_compile_commands_from_config(cls, config):
        """Get path to compile commands."""
        compile_commands = \
            cls._get_setting_from_config(config, 'compile_commands', True)
        return compile_commands

    @classmethod
    def _get_number_of_jobs_from_config(cls, config):
        """Get number of jobs."""
        number_of_jobs = \
            cls._get_setting_from_config(config, 'number_of_jobs')
        try:
            num_jobs_int = int(number_of_jobs)
            return max(num_jobs_int, 1)
        except (ValueError, TypeError):
            return 1

    @classmethod
    def _get_output_directory_from_config(cls, config):
        """Get output directory."""
        output_directory = \
            cls._get_setting_from_config(config, 'output_directory', True)
        return output_directory

    @classmethod
    def _get_error_directory_from_config(cls, config):
        """Get error directory."""
        error_directory = \
            cls._get_setting_from_config(config, 'error_directory')
        return error_directory

    @classmethod
    def _get_compile_commands_pkl_from_config(cls, config):
        """Get path to compile commands PKL file."""
        compile_commands = \
            cls._get_setting_from_config(config, 'compile_commands_pkl')
        return compile_commands
