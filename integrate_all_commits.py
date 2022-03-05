import time

import copy
import os
from integrate_all_commits_libs import current_libs
from ExperimentRunner import Logger, save_leftover_libs, init_directory, ExpRunner

RUN_NAME = "test_run_1"
SAVE_DIRECTORY = f"/home/forian/uni/{RUN_NAME}"
FUZZBENCH_DIRECTORY = "/home/forian/uni/fuzzbench"
TEST_RUN_TIMEOUT = 300              # the time a single experiment has building
DEBUG = False                        # checks whether the logged errors should be printed aswell
OSS_LIBRARIES = current_libs     # OSS_LIBRARIES to run
# The libraries should have the format: {'project': [ ([fuzz_targets], commit1, date1), ... ]}


def main() -> int:
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
    n = 0

    # start of the main loop
    for project, values in OSS_LIBRARIES.items():
        for (fuzz_target_list, commit_hash, date) in values:
            for fuzz_target in fuzz_target_list:
                n += 1
                experiment_name = f'{project}__{fuzz_target}__{commit_hash}__{date}'
                logger.log(f'\n\n{n}. running {experiment_name}')
                logger.log(f'{time.ctime()}')
                # if the system has been pruned give more time, since the base image needs to be reinstalled
                if system_pruned:
                    res = exp_runner.run_experiment(project, fuzz_target, date, commit_hash, cleanup=True,
                                                    timeout=2*TEST_RUN_TIMEOUT)
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
        if n > 25:
            break
        # pop the experiment from the list and save all libraries still to do (in case of crash)
        oss_libraries.pop(project)
        save_leftover_libs('integrate_all_commits_libs.py', oss_libraries)

    logger.log("------------------------------------------ Finished ------------------------------------------")
    logger.log(f"Exception counter: {exception_counter}")
    logger.log(f"Timeout counter: {timeout_counter}")
    logger.log(f"Total counter: {n}")
    return 0


if __name__ == "__main__":
    print("Starting the experiment ...")
    x = main()
    exit(x)
