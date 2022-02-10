# enumerate for loops
# generators for large arrays (uses () brackets instead of [])
# not dict[key], use dict.get(key) --> returns none instead of exception
# count hashable objects with collections.counter
# concat swtring with .join("seperator")
# merge 2 dictionaries with {**dict1, **dict2} or dict1 | dict2
import copy
import os
import integrate_all_libs
from help import Logger, save_leftover_libs, init_directory, ExpRunner

COMMIT_HASH = 'c34c308faad86d154b52586ff66de8d77187cafd'
RUN_NAME = "test_run_5"
SAVE_DIRECTORY = f"/home/forian/uni/{RUN_NAME}"
FUZZBENCH_DIRECTORY = "/home/forian/uni/fuzzbench"
TEST_RUN_TIMEOUT = 300              # the time a single experiment has building
DEBUG = True                        # checks whether the logged errors should be printed aswell
OSS_LIBRARIES = integrate_all_libs.current_libs     # OSS_LIBRARIES to run

def main() -> int:
    # create directory, if they don't already exist
    init_directory(SAVE_DIRECTORY)
    logger = Logger(save_directory=os.path.join(SAVE_DIRECTORY, 'log'), debug=DEBUG)
    exp_runner = ExpRunner(test_run_timeout=TEST_RUN_TIMEOUT, fuzzbench_path=FUZZBENCH_DIRECTORY,
                           save_path=SAVE_DIRECTORY, logger=logger)

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
            logger.log(f'\n\n{n}. running {experiment_name}')

            # if the system has been pruned give more time, since the base image needs to be reinstalled
            if system_pruned:
                res = exp_runner.run_experiment(project, fuzz_target, date, COMMIT_HASH, timeout=2*TEST_RUN_TIMEOUT)
                system_pruned = False
            else:
                res = exp_runner.run_experiment(project, fuzz_target, date, COMMIT_HASH)

            if res:
                timeout_list.append(experiment_name)
            else:
                exception_list.append(experiment_name)

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
    logger.log(f"Exception list: {exception_list}")
    logger.log(f"Timeout list: {timeout_list}")
    return 0


if __name__ == "__main__":
    print("Starting the experiment ...")
    x = main()
    exit(x)
