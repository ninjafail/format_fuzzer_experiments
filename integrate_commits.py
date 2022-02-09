# enumerate for loops
# generators for large arrays (uses () brackets instead of [])
# not dict[key], use dict.get(key) --> returns none instead of exception
# count hashable objects with collections.counter
# concat swtring with .join("seperator")
# merge 2 dictionaries with {**dict1, **dict2} or dict1 | dict2


import copy
import os
import subprocess
from typing import IO
import integrate_all_libs

COMMIT_HASH = 'c34c308faad86d154b52586ff66de8d77187cafd'
RUN_NAME = "test_run_5"
SAVE_DIRECTORY = f"/home/forian/uni/{RUN_NAME}"
FUZZBENCH_DIRECTORY = "/home/forian/uni/fuzzbench"
TEST_RUN_TIMEOUT = 300              # the time a single experiment has building
DEBUG = True                        # checks whether the logged errors should be printed aswell
OSS_LIBRARIES = integrate_all_libs.current_libs     # OSS_LIBRARIES to run

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


def run(cmd: str, out: IO = subprocess.PIPE, err: IO = subprocess.PIPE, timeout: int = TEST_RUN_TIMEOUT) -> subprocess.CompletedProcess:
    """Runs the command as a subprocess.run in a new shell and exits it after the execution

    :param cmd: The unix command to execute
    :param out: file to write the stdout to (Default is PIPE)
    :param err: file to write the stderr to (Default is PIPE)
    :param timeout: Timeout in seconds (Default is global TEST_RUN_TIMEOUT)
    :return: subprocess.CompletedProcess
    """
    return subprocess.run(f"{cmd}", stdout=out, stderr=err, cwd=FUZZBENCH_DIRECTORY, shell=True,
                          timeout=timeout)


def cleanup():
    """Removes all docker containers and all images except the base image.

    :return: None
    """
    # get base_image_id
    p = run('docker images -a')
    x = p.stdout.decode().split('\n')
    base_image_id = ""
    for i in x:
        if "gcr.io/fuzzbench/base-image" in i:
            base_image_id = i.replace('\n', '')
    base_image_id = base_image_id.replace(' ', '').replace('gcr.io/fuzzbench/base-image', '').replace('latest', '')[:12]

    # get all images and sort out the base image, based on its id
    p = run('docker images -aq')
    all_images = p.stdout.decode().split('\n')
    if base_image_id in all_images:
        all_images.remove(base_image_id)
        all_images = list(set(all_images))

    # remove all images except the base-image
    for i in all_images:
        cmd = 'docker image rm -f ' + i.replace('\n', ' ')
        run(cmd)

    # remove all containers
    run('docker rm -vf $(docker ps -aq)')

    # remove all build cache
    # p = Popen('echo y | docker builder prune -a')


def run_experiment(project: str, fuzz_target: str, date: str, commit_hash: str, timeout: int) -> bool:
    """Integrates and runs a single oss-fuzz experiment. Uses cleanup() in the end.

    :param project: The name of the OSS-fuzz project
    :param fuzz_target: The fuzz target
    :param date: The date of the commit, that should be used.
    :param timeout: The time a experiment should be run. Note that the experiment only stops if it fails or after
    having fuzzed for 24 hours.
    :return: True if the experiment was probably successful. False otherwise.
    """
    successful = True

    # path names
    project_name = "{}__{}__{}".format(project, fuzz_target, date)
    project_path = os.path.join(SAVE_DIRECTORY, project_name)
    project_logs_path = os.path.join(project_path, "logs")
    project_out_path = os.path.join(project_path, "out")

    # initialize directories
    init_directory(project_path)
    init_directory(project_logs_path)
    init_directory(project_out_path)

    # run experiment, while writing to logs
    with open(os.path.join(project_logs_path, 'err'), 'w')as err, \
            open(os.path.join(project_logs_path, 'out'), 'w') as out:

        # integrate the experiment
        try:
            cmd = f"PYTHONPATH=. python3 benchmarks/oss_fuzz_benchmark_integration.py " \
                   f"-p {project} " \
                   f"-f {fuzz_target} " \
                   f"-d {date} " \
                   f"-c {commit_hash} && " \
                   f"make test-run-afl-{project}_{fuzz_target}"
            run(cmd, out=out, err=err, timeout=timeout)
        except Exception as e:
            log(f'\n ERROR: {project} \n{e}')
            successful = False

        # test the experiment
        try:
            cmd = f'source .venv/bin/activate; ' \
                  f'make test-run-afl-{project}_{fuzz_target}'
            run(cmd, out, err)
        except TimeoutError as e:
            log(f'\nNormal Timeout: {project} : {e}')
        except Exception as e:
            log(f'\n{project} did not time out -> Likely Error: \n{e}')
            successful = False

        # save the docker container on hard disk
        try:
            # list all containers
            cmd = 'docker ps -aq'
            p1 = run(cmd)
            containers = p1.stdout.decode().split('\n')
            if not containers:
                successful = False
            log(f'\nAll available containers: {containers}')

            # copy the /out directory on hard disk
            for c in containers:
                c = c.replace('\n', "")
                cmd = f'docker cp {c}:/out {project_out_path}/{c}'
                run(cmd)
        except TimeoutError as e:
            log(f"\n   ERROR: Timeout while copying files: {project_name} : {e}")
        except Exception as e:
            log(f"\n   ERROR: Wasn't able to write this project to disk: {project_name} : {e}")

    # Remove all docker containers and all images except the base image
    cleanup()

    return successful


def save_leftover_libs(libs: dict):
    """Stores all libs in the dict (should be the ones that have not yet been fuzzed) to integrate_all_libs.py,
    formatted as a dictionary

    :param libs: The OSS-fuzz libraries to be saved.
    :return: None
    """
    with open('integrate_all_libs.py', 'w') as f:
        f.write("current_libs = { \n")
        for k, v in libs.items():
            f.write(f"\t'{k}': {v},\n")
        f.write("}\n")


def main() -> int:
    # create directory, if they don't already exist
    init_directory(SAVE_DIRECTORY)

    oss_libraries = copy.deepcopy(OSS_LIBRARIES)
    if not oss_libraries:
        return 1
    exception_list = []
    timeout_list = []
    system_pruned = True
    n = 0

    # start of the main loop
    for project, (fuzz_target_list, date) in OSS_LIBRARIES.items():
        for fuzz_target in fuzz_target_list:
            n += 1
            experiment_name = f'{project}__{fuzz_target}__{date}'
            log(f'\n\n{n}. running {experiment_name}')

            # if the system has been pruned give more time, since the base image needs to be reinstalled
            if system_pruned:
                res = run_experiment(project, fuzz_target, date, COMMIT_HASH, 2*TEST_RUN_TIMEOUT)
                system_pruned = False
            else:
                res = run_experiment(project, fuzz_target, date, COMMIT_HASH, TEST_RUN_TIMEOUT)

            if res:
                timeout_list.append(experiment_name)
            else:
                exception_list.append(experiment_name)

            # every x-th run prune the system
            # if n % 25 == 0:
            #     p1 = run('docker system prune -f')
            #     log(str(p1.stdout.decode()))
            #     system_pruned = True

        # pop the experiment from the list and save all libraries still to do (in case of crash)
        oss_libraries.pop(project)
        save_leftover_libs(oss_libraries)
        if n > 30:
            break

    log("------------------------------------------ Finished ------------------------------------------")
    log(f"Exception list: {exception_list}")
    log(f"Timeout list: {timeout_list}")
    return 0


if __name__ == "__main__":
    print("Starting the experiment ...")
    x = main()
    exit(x)
