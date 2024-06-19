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
        print(f'Output {out_dir} must be a directory.')
        return -1
    else:
        print(f'Using existing {out_dir} as output directory.')

    # Check error directory.
    if fpath.exists(err_dir) == False:
        os.mkdir(err_dir)
    elif fpath.isfile(err_dir):
        print(f'Error {err_dir} must be a directory.')
        return -1
    else:
        print(f'Using existing {err_dir} as error directory.')

    cmd_mgr = cm.CommandManager(compile_commands_json)
    thread_mgr = tm.ThreadManager()
    config = cfg.Config(config_yaml)

    job_args = (cmd_mgr, config, out_dir)
    for ii in range(num_of_jobs):
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
            for ii in range(prev_msg_len):
                del_line += ' '
            print(del_line, end='\r')

        if current_idx < last_idx:
            print(msg, end='\r')
            current_idx = cmd_mgr.get_current_index()
        else:
            print(msg)
            break

        time.sleep(0.5)

    thread_mgr.join_all_threads()
    thread_mgr.remove_all_threads()

    if len(cmd_mgr) == cmd_mgr.get_current_index():
        print('All commands processed successfully!')
        return 0

    print('Some commands failed to process!')
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
    with open(dump_compile_commands, 'w') as output_file:
        print(json.dumps(compile_commands, indent=2), file=output_file)

    return 0

def main(arguments) -> int:
    ''' Main function. '''
    dump_compile_commands = arguments.dump_compile_commands

    if(dump_compile_commands != ''):
        return _execute_dump_compile_commands(arguments)

    return _execute_analyzer(arguments)

def _check_file(path, parser):
    if path == '':
        return ''
    if not fpath.isfile(path):
        parser.error('File {path} not found.')
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
                        type=lambda file_path: _check_file(file_path, parser),
                        help='Path YAML config file.',
                        default='')
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        help='Output directory',
                        default='./out')
    parser.add_argument('-j', '--jobs',
                        type=int,
                        help='Number of jobs.',
                        default=1)
    parser.add_argument('input_file',
                        type=lambda file_path: _check_file(file_path, parser),
                        help='Compile commands to load.')

    args = parser.parse_args()

    sys.exit(main(arguments=args))
