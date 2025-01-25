#!/usr/bin/env python3
import argparse
import sys
import os
from multiprocessing import Pool
from tqdm import tqdm
import time
import importlib.metadata

version = importlib.metadata.version("parallel_progress_bar")

def execute_command(id, command):
    """Executes a single command."""
    import subprocess
    try:
        e = os.environ.copy()
        e['PYPAR_JOBID'] = str(id)
        result = subprocess.run(command, shell=True, env=e, capture_output=True, text=True, check=True)
        res = result.stdout.strip()
        return res
    except subprocess.CalledProcessError as e:
        return f"Command failed: {command}\nError: {e.stderr}"
    except Exception as e:
        print('unhandled error: ', e)
        sys.exit(1)
      
def update_progress_bar(res, pbar, command, starttime):
    elapsed = time.time() - starttime
    s = elapsed % 60
    m = elapsed / 60
    h = m / 60
    pbar.set_description(f'{int(h)}h {int(m)}m {int(s)}s elapsed')
    print("\r\033[2K", end="") 
    print(res)
    pbar.update(1)
    pbar.refresh()

def main():
    """Reads commands from stdin, executes them in parallel, and displays progress."""
    starttime = time.time()
    parser = argparse.ArgumentParser(description="Parallel command executor")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count(), help="Number of parallel jobs (default: 4)")
    parser.add_argument("command", default='{}', type=str, help="Command to run, where '{}' is replaced with lines from stdin")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + str(version))

    args = parser.parse_args()
    command = args.command.replace('{}', '{0}')
    commands = [command.format(line.strip()) for line in sys.stdin]
    with Pool(processes=args.jobs) as pool:
        with tqdm(total=len(commands)) as pbar:
            for i, c in enumerate(commands):
                pool.apply_async(execute_command, args=(i,c,), callback=lambda res: update_progress_bar(res, pbar, c, starttime))
            pool.close()
            pool.join()

if __name__ == "__main__":
    main()
