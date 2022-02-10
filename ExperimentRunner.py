import subprocess
import os
from typing import IO


class Logger(object):
    def __init__(self, save_directory: str, debug: bool = True):
        """A Logger class to log and optionally print statements.

        :param save_directory: Path to the file where the log should be stored
        :param debug: If true the logger prints out the logs.
        """
        self.debug = debug
        self.save_dir = save_directory

    def log(self, obj: object) -> None:
        """Logs a message to the specified save directory and optionally prints debug statements.

        :param obj: the content/message to be logged
        :return: None
        """
        if self.debug:
            print(obj)
        with open(self.save_dir, 'a') as f:
            f.write(f"{obj}\n")


def init_directory(d: str) -> None:
    """Creates a directory if it doesn't exist yet

    :param d: the path and name of the directory to create
    :return: None
    """
    if not os.path.exists(d):
        os.mkdir(d)


class ExpRunner(object):
    def __init__(self, test_run_timeout: int, fuzzbench_path: str, save_path: str, debug: bool = False,
                 logger: Logger = None):
        """Creates an experiment runner, which can be used to integrate and run oss-fuzz experiments into fuzzbench.

        :param test_run_timeout: The time an experiment should be tried to be run. Note that sometimes the experiment
         hangs and doesn't exit alone.
        :param fuzzbench_path: The path of the fuzzbench directory.
        :param save_path: The path, where to store the experiment results.
        :param debug: If True, prints all logs. Can be overwritten by logger
        :param logger: A logger that should be used instead of one based on the debug param
        """
        self.timeout = test_run_timeout
        self.fuzzbench_path = fuzzbench_path
        self.save_path = save_path
        if not logger:
            self.logger = Logger(os.path.join(self.save_path, 'log'), debug=debug)
        else:
            self.logger = logger

    def run(self, cmd: str, out: IO = subprocess.PIPE, err: IO = subprocess.PIPE, timeout: int = None) -> \
            subprocess.CompletedProcess:
        """Runs the command as a subprocess.run in a new shell and exits it after the execution

        :param cmd: The unix command to execute
        :param out: file to write the stdout to (Default is PIPE)
        :param err: file to write the stderr to (Default is PIPE)
        :param timeout: the timeout to use instead of self.timeout
        :return: subprocess.CompletedProcess
        """
        if not timeout:
            timeout = self.timeout
        return subprocess.run(f"{cmd}; exit", stdout=out, stderr=err, cwd=self.fuzzbench_path, shell=True,
                              timeout=timeout)

    def cleanup(self):
        """Removes all docker containers and all images except the base image.

        :return: None
        """
        # get base_image_id
        p = self.run('docker images -a')
        x = p.stdout.decode().split('\n')
        base_image_id = ""
        for i in x:
            if "gcr.io/fuzzbench/base-image" in i:
                base_image_id = i.replace('\n', '')
        base_image_id = base_image_id.replace(' ', '').replace('gcr.io/fuzzbench/base-image', '').replace('latest', '')[:12]

        # get all images and sort out the base image, based on its id
        p = self.run('docker images -aq')
        all_images = p.stdout.decode().split('\n')
        if base_image_id in all_images:
            all_images.remove(base_image_id)
            all_images = list(set(all_images))

        # remove all images except the base-image
        for i in all_images:
            cmd = 'docker image rm -f ' + i.replace('\n', ' ')
            self.run(cmd)

        # remove all containers
        self.run('docker rm -vf $(docker ps -aq)')

        # remove all build cache
        # p = Popen('echo y | docker builder prune -a')

    def run_experiment(self, project: str, fuzz_target: str, date: str, commit_hash: str, timeout: int = None) -> bool:
        """Integrates and runs a single oss-fuzz experiment. Uses cleanup() in the end.

        :param project: The name of the OSS-fuzz project
        :param fuzz_target: The fuzz target
        :param date: The date of the commit, that should be used.
        :param commit_hash: The hash of the oss-fuzz commit, which should be used.
        :param timeout: the timeout to use instead of self.timeout
        :return: True if the experiment was probably successful. False otherwise.
        """
        successful = True

        # path names
        project_name = "{}__{}__{}".format(project, fuzz_target, date)
        project_path = os.path.join(self.save_path, project_name)
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
                self.run(cmd, out=out, err=err, timeout=timeout)
            except Exception as e:
                self.logger.log(f'\nERROR: Couldn\'t integrate experiment: {project} \n{e}')
                successful = False

            # test the experiment
            try:
                cmd = f'source .venv/bin/activate; ' \
                      f'make test-run-afl-{project}_{fuzz_target}'
                self.run(cmd, out, err)
            except TimeoutError as e:
                self.logger.log(f'\nNormal Timeout: {project} : {e}')
            except Exception as e:
                self.logger.log(f'\nERROR: An error occurred, while doing the test-run: {project} \n{e}')
                successful = False

            # save the docker container on hard disk
            try:
                # list all containers
                cmd = 'docker ps -aq'
                p1 = self.run(cmd)
                containers = p1.stdout.decode().split('\n')
                if not containers:
                    successful = False
                self.logger.log(f'\nAll available containers: {containers}')

                # copy the /out directory on hard disk
                for c in containers:
                    c = c.replace('\n', "")
                    cmd = f'docker cp {c}:/out {project_out_path}/{c}'
                    self.run(cmd)
            except TimeoutError as e:
                self.logger.log(f"\nERROR: Timeout while copying files: {project_name}: \n{e}")
            except Exception as e:
                self.logger.log(f"\nERROR: Wasn't able to write this project to disk: {project_name}: \n{e}")

        # Remove all docker containers and all images except the base image
        self.cleanup()

        return successful


def save_leftover_libs(save_path: str, libs: dict):
    """Stores all libs in the dict (should be the ones that have not yet been fuzzed) to save_path,
    formatted as a dictionary

    :param save_path: The path, where the libs should be stored
    :param libs: The OSS-fuzz libraries to be saved.
    :return: None
    """
    with open(save_path, 'w') as f:
        f.write("current_libs = { \n")
        for k, v in libs.items():
            f.write(f"\t'{k}': {v},\n")
        f.write("}\n")