import copy
import os
import subprocess
import signal
import typing

from typing import Tuple

import integrate_all_libs as ld


pwd = 'werdasliestkannhacken'

RUN_NAME = "test_run_3"
SAVE_DIRECTORY = "/home/florian/uni/{}".format(RUN_NAME)
TEST_RUN_TIMEOUT = 300

# OSS_LIBRARIES to run
OSS_LIBRARIES = ld.current_libs


# Timeout handler
def handler(signum, frame):
    raise TimeoutError("end of time")


def log(msg):
    print(msg)
    with open(os.path.join(SAVE_DIRECTORY, "log"), 'a') as f:
        f.write(msg + '\n')


def init_directory(d):
    if not os.path.exists(d):
        os.mkdir(d)


def call(cmd: str, out: typing.IO = subprocess.PIPE, err: typing.IO = subprocess.PIPE) -> int:
    return subprocess.call(cmd, stdout=out, stderr=err, universal_newlines=True, shell=True,
                           cwd='/home/florian/uni/cysec_project/fuzzbench', executable='/bin/bash')


def popen(cmd: str, out: typing.IO = subprocess.PIPE, err: typing.IO = subprocess.PIPE, ) -> subprocess.Popen:
    p = subprocess.Popen(cmd, stdout=out, stderr=err, universal_newlines=True, shell=True,
                            cwd='/home/florian/uni/cysec_project/fuzzbench', executable='/bin/bash')
    return p


def kill(proc: subprocess.Popen):
    # os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    # proc.wait(TEST_RUN_TIMEOUT-10)
    pass


def cleanup() -> typing.List[subprocess.Popen]:
    # --> CLEAN UP
    p1 = popen('docker images -a')
    x = p1.stdout.readlines()
    kill(p1)

    # get base_image_id
    base_image_id = ""
    for i in x:
        if "gcr.io/fuzzbench/base-image" in i:
            base_image_id = i.replace('\n', '')
    base_image_id = base_image_id.replace(' ', '').replace('gcr.io/fuzzbench/base-image', '').replace('latest', '')[:12]

    p2 = popen('docker images -aq')
    all_images = p2.stdout.readlines()
    kill(p2)

    if base_image_id in all_images:
        all_images.remove(base_image_id + "\n")
        all_images = list(set(all_images))

    # remove all containers
    p3 = popen('docker rm -vf $(docker ps -aq)')
    kill(p3)

    # remove all images except the base-image
    p4 = None
    for i in all_images:
        cmd = 'docker image rm -f ' + i.replace('\n', ' ')
        p4 = popen(cmd)
        kill(p4)

    # remove all build cache
    # p = Popen('echo y | docker builder prune -a')
    # kill(p)
    return [p1, p2, p3, p4]


def run_experiment(project: str, fuzz_target: str, date: str, timeout: int) -> Tuple[bool, typing.List[
    subprocess.Popen]]:
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
        signal.alarm(timeout)

        # integrate the experiment
        try:
            cmd = f'source .venv/bin/activate; ' \
                  f'PYTHONPATH=. python3 benchmarks/oss_fuzz_benchmark_integration.py ' \
                  f'-p {project} -f {fuzz_target} -c master -d {date}'
            call(cmd, out, err)
        except Exception as e:
            log(f'\n ERROR: {project} \n{e}')
            successful = False
        # kill(p)

        # testing the experiment
        try:
            cmd = f'source .venv/bin/activate; echo {pwd} | sudo make test-run-afl-{project}_{fuzz_target}'
            call(cmd, out, err)
        except TimeoutError as e:
            log(f'\nNormal Timeout: {project} : {e}')
        except Exception as e:
            log(f'\n{project} did not time out -> Likely Error: \n{e}')
            successful = False
        # kill(p)
        p1, p2 = None, None
        # save the docker container on hard disk
        signal.alarm(timeout)
        try:
            # list all containers
            cmd = 'docker ps -aq'
            p1 = popen(cmd)
            containers = p1.stdout.readlines()
            kill(p1)
            if not containers:
                successful = False
            log(f'\nAll available containers: {containers}')

            for c in containers:
                c = c.replace('\n', "")
                cmd = f'echo {pwd} | sudo -S docker cp {c}:/out {project_out_path}/{c}'
                p2 = popen(cmd)
                # kill(proc)

        except TimeoutError as e:
            log(f"\n   ERROR: Timeout while copying files: {project_name} : {e}")
        except Exception as e:
            log(f"\n   ERROR: Wasn't able to write this project to disk: {project_name} : {e}")

        # reset alarm
        signal.alarm(0)
    # cleanup
    procs = cleanup()
    procs.extend([p1, p2])
    return successful, procs


def save_leftover_libs(libs: dict):
    with open('integrate_all_libs.py', 'w') as f:
        f.write("current_libs = { \n")
        for k, v in libs.items():
            f.write(f"\t'{k}': {v},\n")
        f.write("}\n")


def main() -> Tuple[int, dict]:
    # signal for timeout
    signal.signal(signal.SIGALRM, handler)
    processes = []

    # create directory, if they don't already exist
    init_directory(SAVE_DIRECTORY)

    oss_libraries = copy.deepcopy(OSS_LIBRARIES)
    if not oss_libraries:
        return 1, {}
    exception_list = []
    timeout_list = []
    system_pruned = True
    n = 0
    p1 = None
    # start of the main loop
    for project, (fuzz_targets, date) in OSS_LIBRARIES.items():
        for fuzz_target in fuzz_targets:
            n += 1
            experiment_name = f'{project}__{fuzz_target}__{date}'
            log(f'\n\n{n}. running {experiment_name}')

            # if the system has been pruned give more time, since base image needs to be reinstalled
            if system_pruned:
                res, processes = run_experiment(project, fuzz_target, date, 2*TEST_RUN_TIMEOUT)
                system_pruned = False
            else:
                res, processes = run_experiment(project, fuzz_target, date, TEST_RUN_TIMEOUT)

            if res:
                timeout_list.append(experiment_name)
            else:
                exception_list.append(experiment_name)

            # every 50th run prune the system
            if n % 25 == 0:
                p1 = popen('echo y | docker system prune')
                log(str(p1.stdout.readlines()))
                kill(p1)
                system_pruned = True
                p1.communicate()
                p1.terminate()

        # pop the experiment from the list and save all libraries still to do (in case of crash)
        oss_libraries.pop(project)
        save_leftover_libs(oss_libraries)
        for p in processes:
            try:
                if p:
                    p.terminate()
            except Exception as e:
                log(f"Error while trying to terminate the processes: \n {e}")

    log("------------------------------------------ Finished ------------------------------------------")
    log("Exception list: {}".format(exception_list))
    log("Timeout list: {}".format(timeout_list))
    return 0, oss_libraries


x, libs = main()
if x == 0:
    save_leftover_libs(libs)
exit(x)
