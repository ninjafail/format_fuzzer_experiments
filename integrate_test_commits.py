from typing import List, Tuple
import time
import subprocess
import copy
import os
from integrate_test_commits_libs import interesting, counter
from ExperimentRunner import Logger, save_leftover_libs, init_directory, ExpRunner, get_fuzz_targets

RUN_NAME = "test_run_1"
SAVE_DIRECTORY = f"/home/forian/uni/{RUN_NAME}"
FUZZBENCH_DIRECTORY = "/home/forian/uni/fuzzbench"
OSS_FUZZ_BENCHMARKS_PATH = FUZZBENCH_DIRECTORY + '/third_party/oss-fuzz/projects'
TEST_RUN_TIMEOUT = 300              # the time a single experiment has building
DEBUG = False                        # checks whether the logged errors should be printed aswell
OSS_LIBRARIES = interesting     # OSS_LIBRARIES to run
# The libraries should have the format: {'project': ([fuzz_targets], date, [seeds]), ...}


def get_one_commit(counter: int, project: str, fuzz_targets: List[str] = None) -> Tuple[List[str], str, str]:
    """ get fuzz targets, commit and date for one oss-fuzz project
    :param counter: the number of the commit to be taken (0: newest commit, 1: one older, ...)
    :param project: The name of the oss-fuzz project
    :param fuzz_targets: The fuzz_targets of the oss-fuzz project

    :return: Tuple, consisting of: list of fuzz targets, commit hash, date
    """
    # set default of fuzz target
    if fuzz_targets is None:
        fuzz_targets = [project]

    # define the path of the project
    project_path = os.path.join(OSS_FUZZ_BENCHMARKS_PATH, project)

    # checkout to master to get all possible commits
    subprocess.run(f'git checkout master', shell=True, cwd=OSS_FUZZ_BENCHMARKS_PATH,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # get all possible commits and choose the right one, depending on counter
    p = subprocess.run('git --no-pager log --pretty=format:"%h" -- .', shell=True, cwd=project_path,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    commit_hashes = p.stdout.decode().split()
    if counter >= len(commit_hashes):
        return [], '', ''
    commit_hash = commit_hashes[-counter]

    # get all fuzz targets from the available fuzz targets
    subprocess.run(f'git checkout {commit_hash}', shell=True, cwd=project_path,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    avail_fuzz_targets = get_fuzz_targets(project_path)
    if not avail_fuzz_targets:
        avail_fuzz_targets = [project]
    for fuzz_target in copy.deepcopy(fuzz_targets):
        if fuzz_target not in avail_fuzz_targets:
            fuzz_targets.remove(fuzz_target)

    # get the date
    p = subprocess.run(f'git --no-pager log -1 {commit_hash} --format=%cd --date=iso-strict', shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=project_path)
    date = p.stdout.decode().replace('\n', '')

    return fuzz_targets, commit_hash, date


def save_leftover_libs_counter(save_path: str, libs: dict, counter: int):
    """Stores all libs in the dict (should be the ones that have not yet been fuzzed) to save_path,
    formatted as a dictionary. Also stores the current counter

    :param save_path: The path, where the libs should be stored
    :param libs: The OSS-fuzz libraries to be saved.
    :param counter: the counter to be saved
    :return: None
    """
    save_leftover_libs(save_path, libs)
    with open(save_path, 'a') as f:
        f.write(f'\ncounter = {counter}\n')



def test_commits() -> int:
    """idea:
    for each interesting library do one test run with latest commit,
    then increase the counter of latest commit, to test whether the next commit works

    :return:
    """
    # create directory, if they don't already exist
    init_directory(SAVE_DIRECTORY)

    # define logger and Experiment runner
    logger = Logger(save_directory=os.path.join(SAVE_DIRECTORY, 'log'), debug=DEBUG)
    exp_runner = ExpRunner(test_run_timeout=TEST_RUN_TIMEOUT, fuzzbench_path=FUZZBENCH_DIRECTORY,
                           save_path=SAVE_DIRECTORY, logger=logger)

    # copy libraries, so they don't interfere with the loop items
    oss_libraries = copy.deepcopy(OSS_LIBRARIES)
    if not oss_libraries:
        logger.log("I'm done ... There are no experiments left to integrate and test.")
        return 1
    exception_counter = 0
    timeout_counter = 0
    system_pruned = True
    current_counter = counter
    n = 0

    # start of the main loop
    while n < 20:
        for project, values in OSS_LIBRARIES.items():
            fuzz_targets, _, _ = values
            fuzz_targets, commit_hash, date = get_one_commit(current_counter, project, fuzz_targets)

            # if there are no fuzz targets, the experiment was unsuccessful
            if not fuzz_targets:
                val = oss_libraries.pop(project)
                with open('unsuccessful', 'a') as f:
                    f.write(f"'{project}': {val} \n\n")
                save_leftover_libs_counter('integrate_test_commits_libs.py', oss_libraries, current_counter)
                continue

            # otherwise, iterate over all fuzz_targets
            for fuzz_target in fuzz_targets:
                n += 1
                experiment_name = f'{project}__{fuzz_target}__{commit_hash}__{date}'
                logger.log(f'\n\n{n}. running {experiment_name}')
                logger.log(f'{time.ctime()}')
                # if the system has been pruned give more time, since the base image needs to be reinstalled
                if system_pruned:
                    res = exp_runner.run_experiment(project, fuzz_target, date, commit_hash, cleanup=True,
                                                    timeout=2 * TEST_RUN_TIMEOUT)
                    system_pruned = False
                else:
                    res = exp_runner.run_experiment(project, fuzz_target, date, commit_hash, cleanup=True)

                if res:
                    timeout_counter += 1
                else:
                    exception_counter += 1

                # every x-th run prune the system
                # if n % 25 == 0:
                #     p1 = run('docker system prune -f')
                #     log(DEBUG, str(p1.stdout.decode()))
                #     system_pruned = True

                # check whether the fuzz_target is successful
                log_path = os.path.join(SAVE_DIRECTORY, f"{project}__{fuzz_target}__{commit_hash}", "logs")
                with open(f"{log_path}/out", "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if "Entering queue cycle 1" in line:
                            # if the target is successful, add it to successful and remove the fuzz_target
                            oss_libraries.get(project)[0].remove(fuzz_target)
                            # if the project now is empty -> remove it from the queue
                            if not oss_libraries.get(project)[0]:
                                oss_libraries.pop(project)
                            with open('successful', 'a') as successful:
                                successful.write(f"'{project}': ('{fuzz_target}', '{commit_hash}', '{date}'), \n\n")
                            save_leftover_libs_counter('integrate_test_commits_libs.py', oss_libraries, current_counter)
                            continue

        # save all left libraries and the current counter (in case of crash)
        current_counter += 1
        save_leftover_libs_counter('integrate_test_commits_libs.py', oss_libraries, current_counter)

    logger.log("------------------------------------------ Finished ------------------------------------------")
    logger.log(f"Exception counter: {exception_counter}")
    logger.log(f"Timeout counter: {timeout_counter}")
    logger.log(f"Total counter: {n}")
    return 0

def main() -> int:
    return test_commits()

if __name__ == "__main__":
    print("Starting the experiment ...")
    x = main()
    exit(x)
