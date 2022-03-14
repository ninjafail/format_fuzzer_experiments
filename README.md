This repository adds a class that lets you automatically integrate and test OSS-Fuzz experiments into fuzzbench. This 
is especially useful, when you want to integrate and run multiple experiments. The file ExperimentRunner.py adds all 
main functionalities. The initial purpose was to integrate all experiments and examine the seed files. This is why 
there are many other files. 

Before you can use any of this, you need to clone the [fuzzbench directory](https://github.com/google/fuzzbench) and have docker installed. Also, your user should have the necessary docker permissions. If you want to check whether you installed everything correctly go and follow the instructions of [the fuzzbench documentation on integrating an OSS-Fuzz experiment](https://google.github.io/fuzzbench/developing-fuzzbench/adding-a-new-benchmark/). You can test whether you integrated the experiment correctly by running `make test-run-$FUZZER_NAME-$BENCHMARK_NAME` (e.g. `make test-run-afl-ghostscript_gstoraster_fuzzer`) in the fuzzbench directory with its virtual environment is activated.

# Introduction Example
You can integrate and run an oss-fuzz experiment with `ExperimentRunner.run_experiment()`. 
Whenever you run this command, you need to first activate the virtual environment of fuzzbench, by using:
```shell
source /path/to/fuzzbench/.venv/bin/activate
```
See the simple example:
```python
# run this inside of the virtual environment of fuzzbench
import ExperimentRunner as ExpRun

# define the experiment runner, which defines the timeout for trying to integrate the experiment, the path of the 
# fuzzbench directory, and the path where to store the log files for each run experiment
runner = ExpRun.ExpRunner(test_run_timeout=300, 
                          fuzzbench_path='/home/florian/uni/cysec_project/fuzzbench',
                          save_path='/home/florian/experiments')

# integrate and run the experiment "ghostscript" using the fuzz target "gstoraster_fuzzer" at commit "ed1c6e38" which 
# date is the "2020-12-04T07:30:03-08:00"
runner.run_experiment('ghostscript', 'gstoraster_fuzzer', '2020-12-04T07:30:03-08:00', 'ed1c6e38')
```

# ExpRunner
The main purpose of the experiment runner is to integrate and run OSS-Fuzz experiments. `ExpRunner()` takes 3 necessary arguments and one optional argument. 
- `test_run_timeout`: This is the standard timeout of one experiment. Sometimes the experiment hangs and doesn't exit alone, thus this timeout is necessary.
- `fuzzbench_path`: This should be the path of the fuzzbench directory. To integrate the experiments the runner executes scripts from the fuzzbench directory.
- `save_path`: The path, where to store the experiment results. In the end the runner saves the contents of the out directory to the specified `save_path`.
- (optional) debug: If True, prints all logs. Can be overwritten by `logger`. If `logger` is specified this will be ignored.
- (optional) logger: The custom logger class that should be used to log stuff. 

### `run_experiment`
Integrates and runs a single oss-fuzz experiment. It basically runs the necessary commands from fuzzbench to integrate and test an OSS-Fuzz experiment and copies the contents of the `/out` directory from the docker to your hard disk.

:param project: The name of the OSS-fuzz project
:param fuzz_target: The fuzz target, use the name of the project, if the project has no fuzz targets
:param date: The date of the commit, that should be used.
:param commit_hash: The hash of the oss-fuzz commit, which should be used.
:param timeout: the timeout to use instead of self.timeout
:param cleanup: Controls whether docker should be cleaned up in the end. Warning: This removes all containers
and images, except the base image!
:return: True if the experiment was probably successful. False otherwise.

## Further examples
Example: 
```python
import ExperimentRunner as er

logger = er.Logger(debug=True, save_directory='/home/florian/experiments')

runner = er.ExpRunner(test_run_timeout=300,
                      fuzzbench_path='/home/florian/uni/cysec_project/fuzzbench',
                      save_path='/home/florian/experiments',
                      logger=logger)

experiments = {'ghostscript': [(['gstoraster_fuzzer'], 'ed1c6e38', '2020-12-04T07:30:03-08:00'),
                    (['gstoraster_fuzzer'], '9b715c91', '2019-06-27T09:59:20-07:00'),
                    (['gstoraster_fuzzer'], 'cd848bbd', '2020-03-27T13:32:10-07:00')],}

logger.log('Starting the experiment')
for project, targets in experiments.items():
    for t in targets:
        fuzz_targets, commit_hash, date = t[0], t[1], t[2]
        for fuzz_target in fuzz_targets:
            runner.run_experiment(project, fuzz_target, date, commit_hash)
```

```python
from ExperimentRunner import get_fuzz_targets

path_of_ghostscript = '/path/to/fuzzbench/third_party/oss-fuzz/projects/ghostscript'
print(get_fuzz_targets(path_of_ghostscript))

```

```python
import ExperimentRunner as er
from integrate_test_commits import get_one_commit

logger = er.Logger(debug=True, save_directory='/home/florian/experiments')

runner = er.ExpRunner(test_run_timeout=300,
                      fuzzbench_path='/home/florian/uni/cysec_project/fuzzbench',
                      save_path='/home/florian/experiments',
                      logger=logger)

experiments = {'ghostscript': ['gstoraster_fuzzer']}
counter = 0

logger.log('Starting the experiment')
while counter < 20:
    for project, fuzz_targets in experiments.items():
        fuzz_targets, commit_hash, date = get_one_commit(counter, project, fuzz_targets)
        for fuzz_target in fuzz_targets:
            runner.run_experiment(project, fuzz_target, date, commit_hash)
            
    counter += 1

```