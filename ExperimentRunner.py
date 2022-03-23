import subprocess
import os
import copy
import dateutil.parser
import time
from typing import IO, List, Tuple


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

        :param obj: the object/message to be logged
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
        self.oss_fuzz_path = os.path.join(fuzzbench_path, 'third_party/oss-fuzz/projects')
        self.save_path = save_path
        init_directory(save_path)
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

    def run_experiment(self, project: str, fuzz_target: str, commit_hash: str, date: str, timeout: int = None,
                       fuzzer: str = 'afl', cleanup: bool = False) -> bool:
        """Integrates and runs a single oss-fuzz experiment. Uses cleanup() in the end.

        :param project: The name of the OSS-fuzz project
        :param fuzz_target: The fuzz target, use the name of the project, if the project has no fuzz targets
        :param date: The date of the commit, that should be used.
        :param commit_hash: The hash of the oss-fuzz commit, which should be used.
        :param timeout: The timeout to use instead of self.timeout
        :param fuzzer: The fuzzer to do the test run with.
        :param cleanup: Controls whether docker should be cleaned up in the end. Warning: This removes all containers
        and images, except the base image!
        :return: True if the experiment was probably successful. False otherwise.
        """
        successful = True

        # path names
        project_name = f"{project}__{fuzz_target}__{commit_hash}__{date}"
        project_path = os.path.join(self.save_path, project_name)
        project_logs_path = os.path.join(project_path, "logs")
        project_out_path = os.path.join(project_path, "out")

        self.logger.log(f'running {project_name}')
        self.logger.log(f'{time.ctime(time.time())}')

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
                       f"-c {commit_hash}"
                self.run(cmd, out=out, err=err, timeout=timeout)
            except Exception as e:
                self.logger.log(f'\nERROR: Couldn\'t integrate experiment: {project} \n{e}')
                successful = False

            # test the experiment
            try:
                cmd = f'make test-run-afl-{project}_{fuzz_target}'
                self.run(cmd, out=out, err=err, timeout=timeout)
            except TimeoutError as e:
                self.logger.log(f'\nNormal Timeout: {project} : {e}')
            except Exception as e:
                self.logger.log(f'\nERROR: An error occurred, while doing the test-run: {project} \n{e}')
                successful = False

            # save the docker container on hard disk
            try:
                # list all containers
                cmd = f'docker ps -a -f "ancestor=gcr.io/fuzzbench/runners/{fuzzer}/{project}_{fuzz_target}" --format' \
                      f'={{{{.ID}}}} '
                p1 = self.run(cmd)
                containers = p1.stdout.decode().split('\n')
                if not containers:
                    successful = False
                self.logger.log(f'\nAll available containers: {containers}')

                # copy the /out directory on hard disk
                for container in containers:
                    self.logger.log(f'\nCopying container {container} to {project_out_path}')
                    cmd = f'docker cp {container}:/out {project_out_path}'
                    self.run(cmd)
            except TimeoutError as e:
                self.logger.log(f"\nERROR: Timeout while copying files: {project_name}: \n{e}")
            except Exception as e:
                self.logger.log(f"\nERROR: Wasn't able to write this project to disk: {project_name}: \n{e}")

        # Remove all docker containers and all images except the base image
        if cleanup:
            self.cleanup()

        self.logger.log('\n')
        return successful

    def get_one_commit(self, project: str, counter: int = None, before: str = None, fuzz_targets: List[str] = None) \
            -> Tuple[List[str], str, str]:
        """ Given an oss-fuzz project, this function returns all (stated) fuzz targets, the commit hash and the commit
         date for the newest commit.
        :param project: The name of the oss-fuzz project
        :param counter: (Optional) The number of the commit to be taken (0: newest commit, 1: one older, ...). Takes
        the newest commit by default.
        :param before: (Optional) Given a date in iso-strict format, this function only returns a commit older than the
        given date. (iso-strict: <year>-<month>-<day>T<hours>:<minutes>:<seconds>)
        :param fuzz_targets: (Optional) The fuzz_targets of the oss-fuzz project, which should be returned.

        :return: Tuple, consisting of: list of fuzz targets, commit hash, date,
        If counter is bigger than the oldest commit, it returns [], '', ''.
        """

        # checkout to master to get all possible commits
        subprocess.run(f'git checkout master', shell=True, cwd=self.oss_fuzz_path,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # define the path of the project
        project_path = os.path.join(self.oss_fuzz_path, project)

        # set default of fuzz target
        if fuzz_targets is None:
            fuzz_targets = get_fuzz_targets(project_path)
        # set default for counter
        default_counter = False
        if counter is None:
            default_counter = True
            counter = 0
        # set default of date_before
        date_before = None
        if before is not None:
            try:
                date_before = dateutil.parser.isoparse(before)
            except Exception as e:
                raise AssertionError(f"The date in 'before' needs to be in iso-strict format. Run "
                                     f"'git --no-pager log -1 commit hash --format=%cd --date=iso-strict' in the git "
                                     f"repository to get an iso-strict formatted date. \n{e}")

        # get all possible commits and choose the right one, depending on counter

        # get the hash and date for all commits
        p = subprocess.run('git --no-pager log --pretty=format:"%h %cd" --date=iso-strict .', shell=True,
                           cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        commit_hashes = p.stdout.decode().split('\n')
        for i, c in enumerate(commit_hashes):
            commit_hashes[i] = c.split(' ')

        last_date = '0001-01-01T00:00:00+00:00'
        found_one = False
        #print(commit_hashes)
        #print(commit_hashes)

        if not default_counter:
            if counter not in range(-len(commit_hashes), len(commit_hashes)):
                self.logger.log(f'{project} does not have that many commits.')
                return [], '', ''
            commit_hash = commit_hashes[counter][0]
            commit_date = commit_hashes[counter][1]

        if date_before is not None:
            for i, (ch, cd) in enumerate(commit_hashes):
                parsed_cd = dateutil.parser.isoparse(cd)
                if dateutil.parser.isoparse(last_date) <= parsed_cd < date_before \
                        and (default_counter or (parsed_cd <= dateutil.parser.isoparse(commit_hashes[counter][1]))):
                        # i > counter or (i < 0 and len(commit_hashes)+i > counter)) and counter != 0):
                    commit_hash = ch
                    commit_date = cd
                    last_date = cd
                    found_one = True

        if not found_one:
            self.logger.log(f'{project} does not have a commit that is older than {date_before}.')
            return [], '', ''

        # get all fuzz targets from the available fuzz targets
        subprocess.run(f'git checkout {commit_hash}', shell=True, cwd=self.oss_fuzz_path,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not os.path.exists(project_path):
            self.logger.log(f'{project} did not exist before {date_before}.')
            return [], '', ''

        # remove all unnecessary fuzz targets
        avail_fuzz_targets = get_fuzz_targets(project_path)
        if not avail_fuzz_targets:
            avail_fuzz_targets = [project]
        for fuzz_target in copy.deepcopy(fuzz_targets):
            if fuzz_target not in avail_fuzz_targets:
                fuzz_targets.remove(fuzz_target)

        return fuzz_targets, commit_hash, commit_date


def save_leftover_libs(save_path: str, libs: dict):
    """Stores all libs in the dict (should be the ones that have not yet been fuzzed) to save_path,
    formatted as a dictionary, named "current_libs"

    :param save_path: The path, where the libs should be stored
    :param libs: The OSS-fuzz libraries to be saved.
    :return: None
    """
    with open(save_path, 'w') as f:
        f.write("current_libs = { \n")
        for k, v in libs.items():
            f.write(f"\t'{k}': {v},\n")
        f.write("}\n")


def get_fuzz_targets(dir_path: os.path) -> List[str]:
    """Given the directory of an oss-fuzz experiment, it returns all the fuzz targets of this oss-fuzz experiment.
    Returns an empty List, if none were found.

    :param dir_path: The path of the oss-fuzz experiment
    :return: List of fuzz targets
    """
    x = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    # get the targets
    fuzz_targets = []
    for f in x:
        if ".cc" in f or \
           ".cpp" in f or \
           ".C" in f or \
           ".c++" in f or \
           ".c" in f:
            fuzz_targets.append(f[:f.rindex('.')])
    return fuzz_targets
