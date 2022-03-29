import ExperimentRunner as er

# logger = er.Logger(debug=True, save_directory=)

runner = er.ExpRunner(test_run_timeout=600,
                      fuzzbench_path='/home/forian/uni/fuzzbench',
                      save_path='/home/forian/uni/testing',
                      debug=True)
#for i in range(30):
#    print(i, runner.get_one_commit(project='ghostscript', counter=i, before='2020-03-27T13:32:10-07:00'))
#    print(-i, runner.get_one_commit(project='ghostscript', counter=-i, before='2020-03-27T13:32:10-07:00'))

x = {'ghostscript': [(['gstoraster_fuzzer'], 'ed1c6e38', '2020-12-04T07:30:03-08:00'),
                    (['gstoraster_fuzzer'], '9b715c91', '2019-06-27T09:59:20-07:00'),
                    (['gstoraster_fuzzer'], 'cd848bbd', '2020-03-27T13:32:10-07:00')],
     'tinyxml2': [(['xmltest'], '1d5a2cd8', '2020-12-09T21:52:40-08:00')],
}

x = {
    'boost': [(['boost_ptree_jsonread_fuzzer'], 'fe09bda7', '2021-08-20T05:16:38+00:00'),
              (['boost_boost_regex_fuzzer'], 'fe09bda7', '2021-08-20T05:16:38+00:00')],
}
for p, v in x.items():
    for (fs, c, d) in v:
        for f in fs:
            runner.run_experiment(p, f, c, d, fuzzer='aflplusplus')
