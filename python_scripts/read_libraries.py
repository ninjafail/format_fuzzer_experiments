import os


OSS_FUZZ_BENCHMARKS_PATH = '/home/florian/uni/cysec_project/fuzzbench/third_party/oss-fuzz/projects'


def read_libraries():
    libs = [d for d in os.listdir(OSS_FUZZ_BENCHMARKS_PATH) if
            not os.path.isfile(os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d))]
    # the benchmarks with fuzztarget can be compared
    # benchmarks_with_fuzztarget = [d for d in os.listdir("with_fuzztarget") if not os.path.isfile(os.path.join("with_fuzztarget", d))]

    experiments = dict()

    for d in libs:
        dir_path = os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d)
        x = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        found = False
        for f in x:
            if ".cc" in f:
                experiments[d] = f.replace(".cc", "")
                found = True
                break
        if found:
            continue
        for f in x:
            if ".cpp" in f:
                experiments[d] = f.replace(".cpp", "")
                found = True
                break
        if found:
            continue
        for f in x:
            if ".C" in f:
                experiments[d] = f.replace(".C", "")
                break
        if found:
            continue
        for f in x:
            if ".c++" in f:
                experiments[d] = f.replace(".c++", "")
                break
        if found:
            continue
        for f in x:
            if ".c" in f:
                experiments[d] = f.replace(".c", "")
                break

    print("number of included experiments: ", len(experiments), "\n")

    # getting the date
    for d, fuzz_target in experiments.items():
        os.chdir(os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d))
        stream = os.popen('git --no-pager log -1 master --format=%cd --date=iso-strict')
        output = stream.read()
        experiments[d] = (fuzz_target, output.replace("\n", ""))

    return experiments


def read_all_libraries():
    libs = [d for d in os.listdir(OSS_FUZZ_BENCHMARKS_PATH) if
            not os.path.isfile(os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d))]
    # the benchmarks with fuzztarget can be compared
    # benchmarks_with_fuzztarget = [d for d in os.listdir("with_fuzztarget") if not os.path.isfile(os.path.join("with_fuzztarget", d))]

    experiments = dict()

    for d in libs:
        dir_path = os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d)
        x = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

        # get the targets
        has_target = False
        fuzz_targets = []
        for f in x:
            if ".cc" in f or \
               ".cpp" in f or \
               ".C" in f or \
               ".c++" in f or \
               ".c" in f:
                has_target = True
                fuzz_targets.append(f[:f.rindex('.')])
        if not has_target:
            fuzz_targets.append(d)

        # get the git date
        os.chdir(os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d))
        stream = os.popen('git --no-pager log -1 master --format=%cd --date=iso-strict')
        output = stream.read()
        experiments[d] = (fuzz_targets, output.replace('\n', ''))

    print("number of included experiments: ", len(experiments), "\n")
    return experiments



def main():
    experiments = read_all_libraries()
    for k,v in experiments.items():
        print(f"'{k}': {v},")
    with open("all_libs.py", "a") as f:
        f.writelines(str(experiments))


main()