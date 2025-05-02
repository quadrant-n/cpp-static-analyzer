"""Main functions."""

import os
import os.path as fpath
import argparse
import threading
import time
import pathlib as plib

import cpp_static_analyzer.command_manager as cm
import cpp_static_analyzer.thread_manager as tm
import cpp_static_analyzer.config as cfg
import cpp_static_analyzer.console as con


def _check_and_make_directory(directory):
    if not fpath.exists(directory):
        os.mkdir(directory)
        return 1

    if fpath.isfile(directory):
        return -1

    return 0


def _print_progress(command_manager,
                    last_index,
                    sleep_interval):
    current_idx = command_manager.get_current_index()
    msg_len = 0

    while current_idx <= last_index:
        rate = current_idx / last_index * 100

        prev_msg_len = msg_len
        msg = f'Processing files: {rate:.1f}%'
        msg_len = len(msg)

        if msg_len < prev_msg_len:
            del_line = ''
            for _ in range(prev_msg_len):
                del_line += ' '
            con.error(del_line, end='\r')

        if current_idx < last_index:
            con.error(msg, end='\r')
            current_idx = command_manager.get_current_index()
        else:
            con.error(msg)
            break

        time.sleep(sleep_interval)


def _analyze_single_file(arguments, command_manager, config):
    input_file = os.path.abspath(arguments.input_file)
    con.trace(f'Analyzing {input_file}')
    return command_manager.analyze(config, input_file)


def _execute_analyzer_threads(arguments,
                              command_manager,
                              config,
                              out_dir,
                              err_dir):
    con.trace('Executing multi-thread static analyzer.')

    thread_mgr = tm.ThreadManager()
    num_of_jobs = max(arguments.jobs, config.get_number_of_jobs())

    job_args = (command_manager, config, out_dir, err_dir)
    for _ in range(num_of_jobs):
        thread_mgr.add_thread(threading.Thread(target=cm.CommandManager.job,
                                               args=job_args))

    thread_mgr.start_all_threads()

    # Print progress.
    last_idx = len(command_manager)

    _print_progress(command_manager, last_idx, 0.5)

    thread_mgr.join_all_threads()
    thread_mgr.remove_all_threads()

    if last_idx == command_manager.get_current_index():
        con.error('All commands processed successfully!')
        return 0

    con.error('Some commands failed to process!')
    return 1


def _create_directory(directory):
    error_code = _check_and_make_directory(directory)

    if error_code < 0:
        con.error(f'{directory} must be a directory.')

    return error_code


def _create_command_manager(arguments, config):
    compile_commands_pkl = arguments.compile_commands_pkl
    if compile_commands_pkl == '':
        compile_commands_pkl = config.get_compile_commands_pkl()

    if compile_commands_pkl == '':
        compile_commands_json = arguments.compile_commands
        if compile_commands_json == '':
            compile_commands_json = config.get_compile_commands()
        return cm.CommandManager.create_from_json(compile_commands_json)

    return cm.CommandManager.create_from_pkl(compile_commands_pkl)


def _check_directories(arguments, config):
    output_directory = arguments.output_directory
    if output_directory == '':
        output_directory = config.get_output_directory()
    out_dir = plib.Path(output_directory).as_posix()

    # Create output directory.
    error_code = _create_directory(out_dir)
    if error_code == 0:
        con.trace(f'Using existing {out_dir} as output directory.')

    error_directory = arguments.error_directory
    if error_directory == '':
        error_directory = config.get_error_directory()
    err_dir = error_directory
    if err_dir == '':
        err_dir = out_dir + '/errors'

    # Create output directory.
    error_code = _create_directory(err_dir)
    if error_code == 0:
        con.trace(f'Using existing {err_dir} as error directory.')

    return out_dir, err_dir


def _check_directory_for_clang_diagnostics(config):
    if not config.is_clang_enabled():
        return

    diag_dir = config.get_clang_diagnostic_directory()
    diag_dir_posix = plib.Path(diag_dir).as_posix()
    error_code = _create_directory(diag_dir_posix)
    if error_code == 0:
        con.trace(f'Using {diag_dir} as diagnostic directory for clang.')


def _create_config(arguments) -> cfg.Config:
    config_yaml = arguments.configuration_file
    config = cfg.Config(config_yaml)

    # Override clang-tidy if available.
    if arguments.enable_clang_tidy:
        config.set_clang_tidy_enabled(True)
    if arguments.disable_clang_tidy:
        config.set_clang_tidy_enabled(False)

    # Override clang static analyzer if available.
    if arguments.enable_clang_analyzer:
        config.set_clang_enabled(True)
    if arguments.disable_clang_analyzer:
        config.set_clang_enabled(False)

    return config


def _execute_analyzer(arguments) -> int:
    config = _create_config(arguments)

    command_manager = _create_command_manager(arguments, config)

    if arguments.export_to_pkl != '':
        command_manager.export_to_pkl(arguments.export_to_pkl)
        con.trace(f'Compile commands exported to {arguments.export_to_pkl}.')
        return 0

    _check_directory_for_clang_diagnostics(config)

    if arguments.input_file != '':
        return _analyze_single_file(arguments, command_manager, config)

    out_dir, err_dir = _check_directories(arguments, config)

    return _execute_analyzer_threads(arguments,
                                     command_manager,
                                     config,
                                     out_dir,
                                     err_dir)


def _execute_dump_configurations() -> int:
    """ Dump configurations. """
    cfg.Config.write_default_config_to_stdout()
    return 0


def run(arguments) -> int:
    """ Main function. """

    # Define verbosity.
    if arguments.verbosity == 0:
        con.set_debug(con.DebugFlag.QUIET)
    elif arguments.verbosity == 2:
        con.set_debug(con.DebugFlag.DEBUG)
    else:
        con.set_debug(con.DebugFlag.INFO)

    if arguments.dump_configurations:
        return _execute_dump_configurations()

    # Search for YAML file.
    if arguments.configuration_file == '':
        arguments.configuration_file = \
            cfg.Config.search_for_config_file(os.getcwd())

    return _execute_analyzer(arguments)


def _check_file(path, parser, arg: str, allow_empty=False):
    """ Check if a file exist at specific path. """
    if path == '':
        if not allow_empty:
            con.trace(f'{arg}: No available path.')
        return ''
    if not fpath.isfile(path):
        con.trace('File check failed.')
        parser.error(f'File {path} not found.')
        return ''
    return path


def create_argument_parser():
    """ Create argument parser. """
    parser = argparse.ArgumentParser(description='C/C++ static analyzer '
                                     'using clang-tidy.')

    # Dump configurations.
    parser.add_argument('-dc', '--dump_configurations',
                        help='Print configurations to console.',
                        action='store_true')

    # Export compile commands.
    parser.add_argument('-exp', '--export_to_pkl',
                        type=str,
                        help='Export to pickle.',
                        default='')

    # Absolute path to YAML configuration file.
    parser.add_argument('-cfg', '--configuration_file',
                        type=lambda
                        file_path: _check_file(file_path, parser,
                                               'Configuration file'),
                        help='Path YAML configuration file.',
                        default='')
    # Set output directory for writing results.
    parser.add_argument('-o', '--output_directory',
                        type=str,
                        help='Output directory.',
                        default='')
    # Set output directory for writing results.
    parser.add_argument('-err', '--error_directory',
                        type=str,
                        help='Error directory.',
                        default='')
    # Specify number of jobs to run static analyzer.
    parser.add_argument('-j', '--jobs',
                        type=int,
                        help='Number of jobs.',
                        default=1)
    # Path to compile_commands.json.
    parser.add_argument('-cdb', '--compile_commands',
                        type=lambda
                        file_path: _check_file(file_path, parser,
                                               'Compile commands',
                                               True),
                        help='Path to compile_commands.json.',
                        default='')
    # Path to pickle file.
    parser.add_argument('-pkl', '--compile_commands_pkl',
                        type=lambda
                        file_path: _check_file(file_path, parser,
                                               'Compile commands',
                                               True),
                        help='Path to compile commands PKL file.',
                        default='')
    # Enable/disable clang-tidy.
    clang_tidy_group = parser.add_mutually_exclusive_group(required=False)
    clang_tidy_group.add_argument('--enable_clang_tidy',
                                  help='Enable clang-tidy',
                                  action='store_true')
    clang_tidy_group.add_argument('--disable_clang_tidy',
                                  help='Disable clang-tidy',
                                  action='store_true')
    # Enable/disable clang static analyzer.
    clang_analyzer_group = parser.add_mutually_exclusive_group(required=False)
    clang_analyzer_group.add_argument('--enable_clang_analyzer',
                                      help='Enable clang static analyzer',
                                      action='store_true')
    clang_analyzer_group.add_argument('--disable_clang_analyzer',
                                      help='Disable clang static analyzer',
                                      action='store_true')
    # Set logging verbosity.
    parser.add_argument('-v', '--verbosity',
                        type=int,
                        help='Log to stderr. 0: Quiet, 1: Information, \
                        2: Output debug logs.',
                        default=1)
    # Analyze single file.
    parser.add_argument('-f', '--input_file',
                        type=lambda
                        file_path: _check_file(file_path, parser,
                                               'Input file.',
                                               True),
                        help='Single file to analyze.',
                        default='')

    return parser


def execute():
    """Begin execution."""
    parser = create_argument_parser()

    try:
        args = parser.parse_args()
    except SystemExit as e:
        return e.code

    # Execute main function and return exit code to system.
    return run(arguments=args)
