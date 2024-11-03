"""Configuration file processor."""
import pathlib as plib
import os
import yaml

default_config = {
    'CompileCommands': '',
    'ClangTidy': 'clang-tidy',
    'Checks': {
        '-*',
        'abseil-*',
        'altera-*',
        'android-*',
        'boost-*',
        'bugprone-*',
        'cert-*',
        'clang-analyzer-*',
        'concurrency-*',
        'cppcoreguidelines-*',
        'darwin-*',
        'fuchsia-*',
        'google-*',
        'hicpp-*',
        'linuxkernel-*',
        'llvm-*',
        'llvmlibc-*',
        'misc-*',
        'modernize-*',
        'mpi-*',
        'objc-*',
        'openmp-*',
        'performance-*',
        'portability-*',
        'readability-*',
        'zircon-*'
    },
    'Warnings': {
        '-Wall',
        '-Wextra'
    },
    'HeaderFilterRegex': '',
    'PathConverter': {},
    'AdditionalOptions': {}
}


def search_for_config_file(path):
    """Search for config.yml."""
    current_path = plib.Path(path)
    if current_path.is_file():
        current_path = current_path.parent
    parents = current_path.parents
    for parent in parents:
        config_file_path = os.path.join(parent.as_posix(), 'config.yml')
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
        print('{yaml_file_path} not found.')
        return default_config
    except yaml.YAMLError:
        print('{yaml_file_path} is invalid.')
        return default_config


def get_path_converter(config):
    """Get path converter settings."""
    if 'PathConverter' in config and config['PathConverter'] is not None:
        return config['PathConverter']
    print('No path converter available.')
    return default_config['PathConverter']


def get_check_flags(config):
    """Get enabled/disabled checks."""
    if 'Checks' in config and config['Checks'] is not None:
        return ','.join(config['Checks'])
    print('No check flags available. Using all avaliable checks.')
    return ','.join(default_config['Checks'])


def get_clang_tidy(config):
    """Get path to clang-tidy executable."""
    if 'ClangTidy' in config and config['ClangTidy'] is not None:
        return plib.Path(config['ClangTidy']).as_posix()
    print('No clang-tidy available.')
    return default_config['ClangTidy']


def get_additional_options(config):
    """Get additional options."""
    if 'AdditionalOptions' in config and config['AdditionalOptions'] is not None:
        return config['AdditionalOptions']
    print('No additional options available.')
    return default_config['AdditionalOptions']


def get_warnings(config):
    """Get warning flags."""
    if 'Warnings' in config and config['Warnings'] is not None:
        return config['Warnings']
    print('No warnings available. Using -Wall and -Wextra.')
    return default_config['Warnings']


def get_header_filter(config):
    """Get header filter regular expression."""
    if 'HeaderFilterRegex' in config and config['HeaderFilterRegex'] is not None:
        return config['HeaderFilterRegex']
    print('No header filter regex available. Using \'.*\' as default.')
    return default_config['HeaderFilterRegex']


def get_compile_commands(config):
    """Get path to compile commands."""
    if 'CompileCommands' in config and config['CompileCommands'] is not None:
        return plib.Path(config['CompileCommands']).as_posix()
    print('No clang-tidy available.')
    return default_config['CompileCommands']


class Config:
    """Configuration object."""

    _path_converter = {}
    _checks = ''
    _clang_tidy = ''
    _additional_options = {}
    _warnings = {}
    _header_filter = ''
    _compile_commands = ''

    def __init__(self, yml):
        if isinstance(yml, str):
            yaml_file_path = yml
            if yaml_file_path == '':
                config = default_config
            else:
                config = load(yaml_file_path)
        else:
            config = yml

        self._path_converter = get_path_converter(config)
        self._checks = get_check_flags(config)
        self._clang_tidy = get_clang_tidy(config)
        self._additional_options = get_additional_options(config)
        self._warnings = get_warnings(config)
        self._header_filter = get_header_filter(config)
        self._compile_commands = get_compile_commands(config)

    def get_path_converter(self):
        """Get path converter."""
        return self._path_converter

    def get_checks(self):
        """Get check flags."""
        return self._checks

    def get_clang_tidy(self):
        """Get clang-tidy executable path."""
        return self._clang_tidy

    def get_additional_options(self):
        """Get additional options."""
        return self._additional_options

    def get_warnings(self):
        """Get warning flags."""
        return self._warnings

    def get_header_filter(self):
        """Get header filter."""
        return self._header_filter

    def get_compile_commands(self):
        """Get path to compile commands."""
        return self._compile_commands
