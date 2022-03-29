# Automated OSS-Fuzz Integration to Fuzzbench

## Introduction
This repository adds a class that lets you automatically integrate and test OSS-Fuzz experiments into fuzzbench. This 
is especially useful, when you want to integrate and run multiple experiments. The file ExperimentRunner.py adds all 
main functionalities. The initial purpose was to integrate all experiments and examine the seed files. This is why 
there are many other files. 

Before you can use any of this, you need to [follow the instructions to get started with fuzzbench](https://google.github.io/fuzzbench/getting-started/prerequisites/)  
and have docker installed. Also, your user should have the necessary docker permissions. If you want to check whether 
you installed everything correctly go and follow the instructions of 
[the fuzzbench documentation on integrating an OSS-Fuzz experiment](https://google.github.io/fuzzbench/developing-fuzzbench/adding-a-new-benchmark/). 
You can test whether you integrated the experiment correctly by running `make test-run-$FUZZER_NAME-$BENCHMARK_NAME` 
(e.g. `make test-run-afl-ghostscript_gstoraster_fuzzer`) in the fuzzbench directory with its virtual environment is 
activated.


### Example
You can integrate and run an oss-fuzz experiment with `ExperimentRunner.run_experiment()`. 
Whenever you run this command, you need to first activate the virtual environment of fuzzbench, by using:
```shell
source /path/to/fuzzbench/.venv/bin/activate
```
See the simple example:

```python
# run this inside of the virtual environment of fuzzbench
import ExperimentRunner as ExpRun

# define the experiment runner, which defines the timeout for trying to integrate the experiment 
# (in seconds), the path of the fuzzbench directory, and the path where to store the log files 
# for each run experiment
runner = ExpRun.ExpRunner(test_run_timeout=300,
                          fuzzbench_path='/home/florian/uni/cysec_project/fuzzbench',
                          save_path='/home/florian/experiments')

# integrate and run the experiment "ghostscript" using the fuzz target "gstoraster_fuzzer" at 
# commit "ed1c6e38" which date is the "2020-12-04T07:30:03-08:00"
runner.run_experiment('ghostscript', 'gstoraster_fuzzer', 'ed1c6e38', '2020-12-04T07:30:03-08:00')
```

## ExpRunner
The main purpose of the experiment runner is to integrate and run OSS-Fuzz experiments. `ExpRunner()` takes 3 necessary arguments and one optional argument. 

**Arguments:**
- `test_run_timeout`: This is the standard timeout of one experiment. Sometimes the experiment hangs and doesn't exit alone, thus this timeout is necessary.
- `fuzzbench_path`: This should be the path of the fuzzbench directory. To integrate the experiments the runner executes scripts from the fuzzbench directory.
- `save_path`: The path, where to store the experiment results. In the end the runner saves the contents of the out directory to the specified `save_path`.
- (optional) debug: If True, prints all logs. Can be overwritten by `logger`. If `logger` is specified this will be ignored.
- (optional) logger: The custom logger class that should be used to log stuff. 

### `run_experiment`
This function integrates and tests a single oss-fuzz experiment. It basically runs the necessary commands from fuzzbench to integrate and test an OSS-Fuzz experiment and copies the contents of the `/out` directory from the docker to your hard disk. The necessary commands from fuzzbench are:
```shell
PYTHONPATH=. python3 benchmarks/oss_fuzz_benchmark_integration.py -p $PROJECT -f $FUZZ_TARGET -c $COMMIT_HASH -d $COMMIT_DATE

make test-run-afl-$PROJECT_$FUZZ_TARGET
```

**Arguments:**
- `project`: The name of the OSS-fuzz project you want to integrate.
- `fuzz_target`: The fuzz target of the OSS-fuzz project you want to integrate. Some projects don't have a fuzz target specified. In that case use the name of the project itself.
- `date`: The date of the commit, that should be used.
- `commit_hash`: The hash of the oss-fuzz commit, which should be used.
- `timeout`: The timeout to use instead of `self.timeout`.
- `cleanup`: Controls whether docker should be cleaned up in the end. If `True` it cleans all docker containers and images, except the base image which is needed for every test-run. **Warning**: This removes all containers and images, except the base image! 
- `returns`: False, if an exception was thrown or no container was created by the integration scripts. If it is true, this does not necessarily mean that the integration was successful.  

#### Examples:

```python
# basic usage
runner.run_experiment('ghostscript', 'gstoraster_fuzzer', 'ed1c6e38', '2020-12-04T07:30:03-08:00')
```

```python
# run an experiment with a timeout of 10 min and removes all docker containers and images 
# (except the base image)
runner.run_experiment('ghostscript', 'gstoraster_fuzzer', 'ed1c6e38', '2020-12-04T07:30:03-08:00', 
                      timeout=600, cleanup=True)
```

### `get_one_commit`
This function gives you all fuzz targets, the commit hash and the corresponding date for one oss-fuzz project. It takes a counter as an optional argument. The counter represents the age of the commit. Given a counter c, this function uses the c-th commit of the oss-fuzz project. If counter is 0, it takes the newest commit, 1 for the commit one before the newest commit, ad so on. You can use negative numbers to access the oldest commit, second-oldest commit, and so on.

**Arguments:**
`counter`: The number of the commit to be taken (0: newest commit, 1: one older, ..., -1: last commit, -2 second last, ...).
`project`: The name of the oss-fuzz project.
`fuzz_targets`: If you are only interested in a few fuzz_targets, you can specify them here. The function will then only return these.

`returns`: Tuple, consisting of: list of fuzz targets, commit hash, date, in the format `['fuzz_target_1', 'fuzz_target_2', ...], 'commit_hash', 'commit_date'`
If counter is bigger than the oldest commit, it returns [], '', ''.

#### Examples:
```python
# basic usage
runner.get_one_commit(project='ghostscript')
# returns: (['gstoraster_fuzzer'], 'ac38bd2e', '2021-12-14T10:22:01+00:00') 
# return might differ, since there are probably newer updates now
```
```python
# basic usage, with counter
runner.get_one_commit(project='ghostscript', counter=0)
# returns the same as above: (['gstoraster_fuzzer'], 'ac38bd2e', '2021-12-14T10:22:01+00:00')
```
```python
# get the oldest commit
runner.get_one_commit(project='ghostscript', counter=-1)
# returns (['gstoraster_fuzzer'], '9b715c91', '2019-06-27T09:59:20-07:00')
```

## Further examples
### Iterating over multiple experiments

```python
import ExperimentRunner as er

logger = er.Logger(debug=True, save_directory='/home/florian/experiments')

runner = er.ExpRunner(test_run_timeout=300,
                      fuzzbench_path='/home/florian/uni/cysec_project/fuzzbench',
                      save_path='/home/florian/experiments',
                      logger=logger)

experiments = {'ghostscript':
                   [(['gstoraster_fuzzer'], 'ed1c6e38', '2020-12-04T07:30:03-08:00'),
                    (['gstoraster_fuzzer'], '9b715c91', '2019-06-27T09:59:20-07:00'),
                    (['gstoraster_fuzzer'], 'cd848bbd', '2020-03-27T13:32:10-07:00')],
               'gnupg':
                   [(['fuzz_import', 'fuzz_decrypt', 'fuzz_list', 'fuzz_verify'],
                     '13aca530', '2018-05-24T08:58:52-07:00'),
                    (['fuzz_import', 'fuzz_decrypt', 'fuzz_list', 'fuzz_verify'],
                     '34a719c9', '2019-05-22T09:09:42-07:00'),
                    (['fuzz_import', 'fuzz_decrypt', 'fuzz_list', 'fuzz_verify'],
                     '84faf557', '2020-12-10T09:49:27+11:00')]
               }

logger.log('Starting the experiment')
for project, targets in experiments.items():
    for t in targets:
        fuzz_targets, commit_hash, date = t[0], t[1], t[2]
        for fuzz_target in fuzz_targets:
            runner.run_experiment(project, fuzz_target, commit_hash, date)
```

### Iterating over multiple experiments, while getting the necessary information from get_one_commit()

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
            runner.run_experiment(project, fuzz_target, commit_hash, date)
            counter += 1
```

### Using other helper functions
```python
from ExperimentRunner import get_fuzz_targets

path_of_ghostscript = '/path/to/fuzzbench/third_party/oss-fuzz/projects/ghostscript'
print(get_fuzz_targets(path_of_ghostscript))

```

