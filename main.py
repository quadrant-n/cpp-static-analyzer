# Main function.

import os.path as fpath
import argparse
import command_manager as cm
import thread_manager as tm
import threading
import time
import config as cfg
import sys
import os

def main(arguments):
    ''' Main function. '''
    compile_commands_json = arguments.input_file
    config_yaml = arguments.config_file
    num_of_jobs = arguments.jobs
    out_dir = arguments.output_dir

    # Check output directory.
    if fpath.exists(out_dir) == False:
        os.mkdir(out_dir)
    elif fpath.isfile(out_dir):
        print(f'Output {out_dir} must be adirectory.')
        return -1
    else:
        print(f'Using existing {out_dir} as output directory.')

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

def _check_file(path, parser):
    if path == '':
        return ''
    if not fpath.isfile(path):
        parser.error('File {path} not found.')
    else:
        return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='C/CPP static analyzer using clang-tidy.')

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
