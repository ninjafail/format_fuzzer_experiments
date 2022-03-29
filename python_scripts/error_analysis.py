import os

logs_path = '/home/forian/uni/integrate_all_aflplusplus_4'

libs = [d for d in os.listdir(logs_path) if not os.path.isfile(os.path.join(logs_path, d))]
if '.idea' in libs:
    libs.remove('.idea')


c_err = 0
c_not_found_err = 0
c_fuzz_target_binary_not_found = 0
c_executor_failed_running = 0
c_no_stats = 0
c_pull_access_denied = 0
c_invalid_response_status = 0

for i,d in enumerate(libs):
    print(f'{i}:')
    l = os.path.join(logs_path, d, 'logs')
    with open(os.path.join(l, 'err'), 'r') as err:
        x = err.read().split('\n')

    err = False
    not_found_err = False
    fuzz_target_binary_not_found = False
    executor_failed_running = False
    no_stats = False
    pull_access_denied = False
    invalid_response_status = False

    for line in x:
        if "ERROR: gcr.io/fuzzbench/builders/" in line and "not found" in line:
            print(line)
            not_found_err = True
        if "ERROR:root:Fuzz target binary not found" in line:
            # print(line)
            fuzz_target_binary_not_found = True
        if "ERROR: executor failed running" in line:
            executor_failed_running = True
        if "No such file or directory: \\'/out/corpus/fuzzer_stats\\'\\n'}" in line:
            no_stats = True
        if "ERROR: pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed" in line:
            pull_access_denied = True
        if "ERROR: invalid response status" in line:
            invalid_response_status = True

        if "ERROR:" in line:
            err = True
            # if not (not_found_err or fuzz_target_binary_not_found or executor_failed_running or no_stats or pull_access_denied or invalid_response_status): print(line)
        if 'error:' in line:
            if 'did not match any file(s) known to git' in line:
                continue
            if 'no such file or directory' in line:
                continue
            print('\t', line)

    if err:
        c_err += 1
    if not_found_err:
        c_not_found_err += 1
    if fuzz_target_binary_not_found:
        c_fuzz_target_binary_not_found += 1
    if executor_failed_running:
        c_executor_failed_running += 1
    if no_stats:
        c_no_stats += 1
    if pull_access_denied:
        c_pull_access_denied += 1
    if invalid_response_status:
        c_invalid_response_status += 1


print()
print('err: ', c_err)
print('not_found_err: ', c_not_found_err)
print('executor_failed_running: ', c_executor_failed_running)
print('no_stats: ', c_no_stats)
print('fuzz_target_binary_not_found: ', c_fuzz_target_binary_not_found)
print('pull_access_denied: ', c_pull_access_denied)
print('invalid_response_status: ', c_invalid_response_status)
