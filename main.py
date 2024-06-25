# Main function.

import os.path as fpath
import argparse
import command_manager as cm
import compile_db as cdb
import thread_manager as tm
import threading
import time
import config as cfg
import sys
import os
import pathlib as plib
import json
import console as con

def _execute_analyzer(arguments) -> int:
    compile_commands_json = arguments.input_file
    config_yaml = arguments.config_file
    num_of_jobs = arguments.jobs
    out_dir = plib.Path(arguments.output_dir).as_posix()
    err_dir = out_dir + '/errors'

    # Check output directory.
    if fpath.exists(out_dir) == False:
        os.mkdir(out_dir)
    elif fpath.isfile(out_dir):
        con.error(f'Output {out_dir} must be a directory.')
        return -1
    else:
        con.trace(f'Using existing {out_dir} as output directory.')

    # Check error directory.
    if fpath.exists(err_dir) == False:
        os.mkdir(err_dir)
    elif fpath.isfile(err_dir):
        con.error(f'Error {err_dir} must be a directory.')
        return -1
    else:
        con.trace(f'Using existing {err_dir} as error directory.')

    cmd_mgr = cm.CommandManager(compile_commands_json)
    thread_mgr = tm.ThreadManager()
    config = cfg.Config(config_yaml)

    job_args = (cmd_mgr, config, out_dir)
    for _ in range(num_of_jobs):
        thread_mgr.add_thread(threading.Thread(target=cm.CommandManager.job,
                                               args=job_args))

    thread_mgr.start_all_threads()

    # Print progress.
    current_idx = cmd_mgr.get_current_index()
    last_idx = len(cmd_mgr)
    msg_len = 0

    while current_idx <= last_idx:
        rate = current_idx / last_idx * 100

        prev_msg_len = msg_len
        msg = f'Processing files: {rate:.1f}%'
        msg_len = len(msg)

        if msg_len < prev_msg_len:
            del_line = ''
            for _ in range(prev_msg_len):
                del_line += ' '
            con.error(del_line, end='\r')

        if current_idx < last_idx:
            con.error(msg, end='\r')
            current_idx = cmd_mgr.get_current_index()
        else:
            con.error(msg)
            break

        time.sleep(0.5)

    thread_mgr.join_all_threads()
    thread_mgr.remove_all_threads()

    if len(cmd_mgr) == cmd_mgr.get_current_index():
        con.error('All commands processed successfully!')
        return 0

    con.error('Some commands failed to process!')
    return 1

def _execute_dump_compile_commands(arguments) -> int:
    compile_commands_json = arguments.input_file
    commands = cdb.load_compile_commands(compile_commands_json)

    config_yaml = arguments.config_file
    config = cfg.Config(config_yaml)

    compile_commands = []
    for command in commands:
        entry = cdb.Entry(command)
        entry_dict = {}

        entry_dict['directory'] = cdb.convert_path(entry.directory,
                                                   config.path_converter)

        command_str = ''
        for arg in entry.arguments:
            if command_str != '':
                command_str += ' '
            command_str += cdb.convert_path(arg, config.path_converter)

        entry_dict['command'] = command_str

        if entry.input_path != '':
            entry_dict['file'] = cdb.convert_path(entry.input_path,
                                                  config.path_converter)

        if entry.output_path != '':
            entry_dict['output'] = cdb.convert_path(entry.output_path,
                                                    config.path_converter)

        compile_commands.append(entry_dict)

    dump_compile_commands = arguments.dump_compile_commands

    con.error(f'Dumping compile commands to {dump_compile_commands}.')

    try:
        with open(dump_compile_commands, 'w') as output_file:
            print(json.dumps(compile_commands, indent=2), file=output_file)
    except Exception as e:
        con.trace('Failed dumping compile commands.')
        con.error(f'Error: {e}.')
        return -2

    return 0

def main(arguments) -> int:
    ''' Main function. '''
    dump_compile_commands = arguments.dump_compile_commands

    if(dump_compile_commands != ''):
        return _execute_dump_compile_commands(arguments)

    return _execute_analyzer(arguments)

def _check_file(path, parser, arg: str):
    if path == '':
        con.trace(f'{arg}: No available path.')
        return ''
    if not fpath.isfile(path):
        con.trace('File check failed.')
        parser.error(f'File {path} not found.')
        return ''
    else:
        return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='C/C++ static analyzer using clang-tidy.')

    parser.add_argument('-dcc', '--dump-compile-commands',
                        type=str,
                        help='Dump compile commands to a file.',
                        default='')
    parser.add_argument('-cfg', '--config-file',
                        type=lambda file_path: _check_file(file_path, parser, 'Config file'),
                        help='Path YAML config file.',
                        default='')
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        help='Output directory',
                        default='')
    parser.add_argument('-j', '--jobs',
                        type=int,
                        help='Number of jobs.',
                        default=1)
    parser.add_argument('-f', '--file',
                        type=str,
                        help='Analyze single file.',
                        default='')
    parser.add_argument('-v', '--verbosity',
                        type=int,
                        help='Log to stderr. 0: Quiet - 2: Output debug logs.',
                        default=1)
    parser.add_argument('input_file',
                        type=lambda file_path: _check_file(file_path, parser, 'Input file'),
                        help='Compile commands to load.',
                        default='')

    args = parser.parse_args()

    if args.verbosity == 0:
        con.set_debug(con.DebugFlag.Quiet)
    elif args.verbosity == 2:
        con.set_debug(con.DebugFlag.Debug)
    else:
        con.set_debug(con.DebugFlag.Info)

    if args.input_file == '' and args.config_file == '':
        args.config_file = cfg.search_for_config_file(os.getcwd())

    sys.exit(main(arguments=args))
