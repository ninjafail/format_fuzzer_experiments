import copy
import os
import sys
import integrate_all_libs

from ExperimentRunner import Logger, save_leftover_libs, init_directory, ExpRunner

only_before_date = "2021-8-25T00:00:00"  # TODO: date
RUN_NAME = "integrate_all_oss_1"
SAVE_DIRECTORY = f"/home/forian/uni/{RUN_NAME}"
FUZZBENCH_DIRECTORY = "/home/forian/uni/fuzzbench"
TEST_RUN_TIMEOUT = 600              # the time a single experiment has building
OSS_LIBRARIES = integrate_all_libs.current_libs     # OSS_LIBRARIES to run

def main() -> int:
    # create directory, if they don't already exist
    init_directory(SAVE_DIRECTORY)
    logger = Logger(save_directory=os.path.join(SAVE_DIRECTORY, 'main_log'), debug=True)
    runner = ExpRunner(test_run_timeout=TEST_RUN_TIMEOUT, fuzzbench_path=FUZZBENCH_DIRECTORY,
                           save_path=SAVE_DIRECTORY, logger=logger)

    oss_libraries = copy.deepcopy(OSS_LIBRARIES)
    if not oss_libraries:
        return 1
    system_pruned = True
    n = 0

    # start of the main loop
    for project in oss_libraries:
        fuzz_targets, commit_hash, commit_date = runner.get_one_commit(project=project, before=only_before_date)
        for fuzz_target in fuzz_targets:
            n += 1
            logger.log(n)

            # if the system has been pruned give more time, since the base image needs to be reinstalled
            if system_pruned:
                runner.run_experiment(project, fuzz_target, commit_hash, commit_date,
                                            timeout=2 * TEST_RUN_TIMEOUT)
                system_pruned = False
            else:
                runner.run_experiment(project, fuzz_target, commit_hash, commit_date)

            # every x-th run prune the system
            # if n % 25 == 0:
            #     p1 = run('docker system prune -f')
            #     log(DEBUG, str(p1.stdout.decode()))
            #     system_pruned = True

        # pop the experiment from the list and save all libraries still to do (in case of crash)
        oss_libraries.pop(project)
        save_leftover_libs('integrate_all_libs.py', oss_libraries)
        if n > 30:
            break

    logger.log("------------------------------------------ Finished ------------------------------------------")
    return 0


if __name__ == "__main__":
    print("Starting the experiment ...")
    x = main()
    exit(x)
