from collections import defaultdict
import pathlib as plib
import yaml

default_config = {
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

def load(yaml_file_path):
    try:
        with open(yaml_file_path, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print('{yaml_file_path} not found.')
        return default_config
    except yaml.YAMLError:
        print('{yaml_file_path} is invalid.')
        return default_config

def get_path_converter(config):
    if 'PathConverter' in config and config['PathConverter'] is not None:
        return config['PathConverter']
    print('No path converter available.')
    return default_config['PathConverter']

def get_check_flags(config):
    if 'Checks' in config and config['Checks'] is not None:
        return ','.join(config['Checks'])
    print('No check flags available. Using all avaliable checks.')
    return ','.join(default_config['Checks'])

def get_clang_tidy(config):
    if 'ClangTidy' in config and config['ClangTidy'] is not None:
        return plib.Path(config['ClangTidy']).as_posix()
    print('No clang-tidy available.')
    return default_config['ClangTidy']

def get_additional_options(config):
    if 'AdditionalOptions' in config and config['AdditionalOptions'] is not None:
        return config['AdditionalOptions']
    print('No additional options available.')
    return default_config['AdditionalOptions']

def get_warnings(config):
    if 'Warnings' in config and config['Warnings'] is not None:
        return config['Warnings']
    print('No warnings available. Using -Wall and -Wextra.')
    return default_config['Warnings']

def get_header_filter(config):
    if 'HeaderFilterRegex' in config and config['HeaderFilterRegex'] is not None:
        return config['HeaderFilterRegex']
    print('No header filter regex available. Using \'.*\' as default.')
    return default_config['HeaderFilterRegex']



class Config(object):
    path_converter = []
    checks = ''
    clang_tidy = ''
    additional_options = []
    warnings = []
    header_filter = ''

    def __init__(self, yaml):
        if isinstance(yaml, str):
            yaml_file_path = yaml
            if yaml_file_path == '':
                config = default_config
            else:
                config = load(yaml_file_path)
        else:
            config = yaml

        self.path_converter = get_path_converter(config)
        self.checks = get_check_flags(config)
        self.clang_tidy = get_clang_tidy(config)
        self.additional_options = get_additional_options(config)
        self.warnings = get_warnings(config)
        self.header_filter = get_header_filter(config)
