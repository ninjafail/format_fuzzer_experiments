# enumerate for loops
# generators for large arrays (uses () brackets instead of [])
# not dict[key], use dict.get(key) --> returns none instead of exception
# count hashable objects with collections.counter
# concat swtring with .join("seperator")
# merge 2 dictionaries with {**dict1, **dict2} or dict1 | dict2


import copy
import os
import subprocess
import signal
import typing
import integrate_all_libs as ld


RUN_NAME = "test_run_3"
SAVE_DIRECTORY = f"/home/florian/uni/{RUN_NAME}"
FUZZBENCH_DIRECTORY = "/home/florian/uni/cysec_project/fuzzbench"
TEST_RUN_TIMEOUT = 300              # the time a single experiment has building
DEBUG = True                        # checks whether the logged errors should be printed aswell
OSS_LIBRARIES = ld.current_libs     # OSS_LIBRARIES to run

"""
Stuff I've learned in the first script:
 - subprocesses need to be quit/handled properly
 - logging is good
 - timeouts can be solved via the timeout in run
 - the directory structure is fine aswell
 - just make the code more readable
"""


def log(obj: object) -> None:
    """Logs a message in the text file "log"

    :param obj: the content/message to be logged
    :return: None
    """
    if DEBUG:
        print(obj)
    with open(os.path.join(SAVE_DIRECTORY, "log"), 'a') as f:
        f.write(f"{obj}\n")


def init_directory(d: str) -> None:
    """Creates a directory if it doesn't exist yet

    :param d: the path and name of the directory to create
    :return: None
    """
    if not os.path.exists(d):
        os.mkdir(d)


def run(cmd: str, out: typing.IO = subprocess.PIPE, err: typing.IO = subprocess.PIPE) -> subprocess.CompletedProcess:
    """runs the command as a subprocess.run in a new shell and exits it after the execution

    :param cmd: The unix command to execute
    :param out: file to write the stdout to (Default is PIPE)
    :param err: file to write the stderr to (Default is PIPE)
    :return: subprocess.CompletedProcess
    """
    return subprocess.run(f"{cmd}; exit", stdout=out, stderr=err, cwd=FUZZBENCH_DIRECTORY, shell=True,
                          timeout=TEST_RUN_TIMEOUT)
    pass



def main():
    c=0
    for project, (fuzz_target_list, date) in OSS_LIBRARIES.items():
        for fuzz_target in fuzz_target_list:
            c+=1
            try:
                cmd = f"PYTHONPATH=. .venv/bin/python3 benchmarks/oss_fuzz_benchmark_integration.py -p {project} -f {fuzz_target} -d {date} -c master"
                cmd2 = f"PYTHONPATH=. python3 benchmarks/oss_fuzz_benchmark_integration.py " \
                            f"-p {project} " \
                            f"-f {fuzz_target} " \
                            f"-d {date} " \
                            f"-c master && " \
                       f"make test-run-afl-{project}_{fuzz_target}"
                p = run(cmd2)
                if p:
                    if p.stdout: print(p.stdout.decode())
                    if p.stderr: print(p.stderr.decode())
                else:
                    print("error")
            except Exception as e:
                print(e)
            if c>5: return 0


if __name__ == "__main__":
    print("Starting the experiment ...")
    #main()
