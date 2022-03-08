This repository is supposed to work with fuzzbench. 

# ExperimentRunner
The main purpose of the experiment runner is to integrate and run OSS-fuzz experiments. 
You can use 
It basically runs the 2 commands

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

path_of_ghostscript = '/home/florian/uni/cysec_project/fuzzbench/third_party/oss-fuzz/projects/ghostscript'
print(get_fuzz_targets(path_of_ghostscript))

```

```python
import ExperimentRunner as er
from integrate_test_commits import get_one_commit, 

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