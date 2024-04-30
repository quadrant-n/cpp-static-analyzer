from collections import defaultdict
import yaml

default_config = {
    'Checks': {
        'abseil': 0,
        'altera': 0,
        'android': 0,
        'boost': 0,
        'bugprone': 0,
        'cert': 0,
        'clang-analyzer': 0,
        'concurrency': 0,
        'cppcoreguidelines': 0,
        'darwin': 0,
        'fuchsia': 0,
        'google': 0,
        'hicpp': 0,
        'linuxkernel': 0,
        'llvm': 0,
        'llvmlibc': 0,
        'misc': 0,
        'modernize': 0,
        'mpi': 0,
        'objc': 0,
        'openmp': 0,
        'performance': 0,
        'portability': 0,
        'readability': 0,
        'zircon': 0
    },
    'PathConverter': {}
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
    if 'PathConverter' in config:
        return config['PathConverter']
    print('No path converter available.')
    return default_config['PathConverter']

def get_check_flags(config):
    if 'Checks' in config:
        checks = config['Checks']
        defaultChecks = default_config['Checks']
        result = {}

        for key, value in defaultChecks.items():
            if key in checks:
                result[key] = checks[key]
            else:
                result[key] = 0

        return result

    print('No checks available.')
    return default_config['Checks']