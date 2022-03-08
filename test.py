import ExperimentRunner as er

# logger = er.Logger(debug=True, save_directory=)

runner = er.ExpRunner(test_run_timeout=300,
                      fuzzbench_path='/home/florian/uni/cysec_project/fuzzbench',
                      save_path='/home/florian/experiments',
                      debug=True)

x = {'ghostscript': [(['gstoraster_fuzzer'], 'ed1c6e38', '2020-12-04T07:30:03-08:00'),
                    (['gstoraster_fuzzer'], '9b715c91', '2019-06-27T09:59:20-07:00'),
                    (['gstoraster_fuzzer'], 'cd848bbd', '2020-03-27T13:32:10-07:00')],}

runner.run_experiment('ghostscript', 'gstoraster_fuzzer', '2020-03-27T13:32:10-07:00', 'cd848bbd')

