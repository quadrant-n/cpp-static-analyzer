# Main function.

import os.path as fpath
import argparse
import command_manager as cm
import thread_manager as tm
import threading
import time

def main(compile_commands_json: str):
    cmd_mgr = cm.CommandManager(compile_commands_json)
    thread_mgr = tm.ThreadManager()

    for ii in range(4):
        thread_mgr.add_thread(threading.Thread(target=cm.CommandManager.job,
                                               args=(cmd_mgr,)))

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
    else:
        print('Some commands failed to process!')

def check_file(path, parser):
    if not fpath.isfile(path):
        parser.error('File {path} not found.')
    else:
        return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='C/CPP static analyzer using clang-tidy.')
    parser.add_argument('input_file',
                        type=lambda file_path: check_file(file_path, parser),
                        help='Compile commands to load.')

    args = parser.parse_args()

    main(args.input_file)
