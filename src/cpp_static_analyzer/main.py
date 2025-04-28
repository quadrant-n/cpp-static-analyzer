"""Main functions."""

import os
import os.path as fpath
import argparse
import threading
import time
import sys
import pathlib as plib

import cpp_static_analyzer.command_manager as cm
import cpp_static_analyzer.compile_db as cdb
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


def _execute_analyzer_threads(arguments,
                              compile_commands_json,
                              config,
                              out_dir,
                              err_dir):
    cmd_mgr = cm.CommandManager(compile_commands_json)
    thread_mgr = tm.ThreadManager()

    num_of_jobs = max(arguments.jobs, config.get_number_of_jobs())

    job_args = (cmd_mgr, config, out_dir, err_dir)
    for _ in range(num_of_jobs):
        thread_mgr.add_thread(threading.Thread(target=cm.CommandManager.job,
                                               args=job_args))

    thread_mgr.start_all_threads()

    # Print progress.
    last_idx = len(cmd_mgr)

    _print_progress(cmd_mgr, last_idx, 0.5)

    thread_mgr.join_all_threads()
    thread_mgr.remove_all_threads()

    if last_idx == cmd_mgr.get_current_index():
        con.error('All commands processed successfully!')
        return 0

    con.error('Some commands failed to process!')
    return 1


def _create_directory(directory):
    error_code = _check_and_make_directory(directory)

    if error_code < 0:
        con.error(f'{directory} must be a directory.')

    return error_code


def _execute_analyzer(arguments) -> int:
    config_yaml = arguments.configuration_file
    config = cfg.Config(config_yaml)

    output_directory = arguments.output_directory
    if output_directory == '':
        output_directory = config.get_output_directory()
    out_dir = plib.Path(output_directory).as_posix()

    # Check output directory.
    error_code = _create_directory(out_dir)
    if error_code == 0:
        con.trace(f'Using existing {out_dir} as output directory.')

    error_directory = arguments.error_directory
    if error_directory == '':
        error_directory = config.get_error_directory()
    err_dir = error_directory
    if err_dir == '':
        err_dir = out_dir + '/errors'

    # Check error directory.
    error_code = _create_directory(err_dir)
    if error_code == 0:
        con.trace(f'Using existing {err_dir} as error directory.')

    compile_commands_json = arguments.compile_commands
    if compile_commands_json == '':
        compile_commands_json = config.get_compile_commands()

    return _execute_analyzer_threads(arguments,
                                     compile_commands_json,
                                     config,
                                     out_dir,
                                     err_dir)


def _process_commands(commands, config):
    compile_commands = []
    for command in commands:
        entry = cdb.Entry(command)
        entry_dict = {}

        directory = entry.get_directory()
        path_converter = config.get_path_converter()

        entry_dict['directory'] = cdb.convert_path(directory,
                                                   path_converter)

        command_str = ''
        arguments = entry.get_arguments()
        for arg in arguments:
            if command_str != '':
                command_str += ' '
            command_str += cdb.convert_path(arg, path_converter)

        entry_dict['command'] = command_str

        input_path = entry.get_input_path()
        if input_path != '':
            entry_dict['file'] = cdb.convert_path(input_path,
                                                  path_converter)

        output_path = entry.get_output_path()
        if output_path != '':
            entry_dict['output'] = cdb.convert_path(output_path,
                                                    path_converter)

        compile_commands.append(entry_dict)

    return compile_commands


def _execute_dump_configurations() -> int:
    """ Dump configurations. """
    cfg.Config.write_default_config_to_stdout()
    return 0


def main(arguments) -> int:
    """ Main function. """
    if arguments.dump_configurations:
        return _execute_dump_configurations()

    # Search for YAML file.
    if arguments.configuration_file == '':
        arguments.configuration_file = \
            cfg.Config.search_for_config_file(os.getcwd())

    return _execute_analyzer(arguments)


def _check_file(path, parser, arg: str):
    """ Check if a file exist at specific path. """
    if path == '':
        con.trace(f'{arg}: No available path.')
        return ''
    if not fpath.isfile(path):
        con.trace('File check failed.')
        parser.error(f'File {path} not found.')
        return ''
    return path


def execute():
    """Begin execution."""
    parser = argparse.ArgumentParser(description='C/C++ static analyzer \
    using clang-tidy.')

    # Dump configurations.
    parser.add_argument('-dc', '--dump_configurations',
                        help='Print configurations to console.',
                        action='store_true')
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
                        type=str,
                        help='Path to compile_commands.json.',
                        default='')
    # Path to pickle file.
    parser.add_argument('-pkl', '--compile_commands_pkl',
                        type=str,
                        help='Path to compile commands PKL file.'
                        default='')
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
                                               'Input file.'),
                        help='Single file to analyze.',
                        default='')

    args = parser.parse_args()

    # Define verbosity.
    if args.verbosity == 0:
        con.set_debug(con.DebugFlag.QUIET)
    elif args.verbosity == 2:
        con.set_debug(con.DebugFlag.DEBUG)
    else:
        con.set_debug(con.DebugFlag.INFO)

    # Execute main function and return exit code to system.
    sys.exit(main(arguments=args))
