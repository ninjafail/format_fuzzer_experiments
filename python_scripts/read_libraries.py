import os


OSS_FUZZ_BENCHMARKS_PATH = '/home/forian/uni/fuzzbench/third_party/oss-fuzz/projects'


def read_libraries(commit_hash: str = 'master') -> dict:
    """Reads the OSS_FUZZ libraries, that have a fuzz target specified. This might be buggy, use read_libraries_all.

    :param commit_hash: The commit hash, from which commit you want the experiments. (default=master)
    :return: A dictionary containing all projects, that have a fuzz_target specified. The format is:
    <project>: (<list_of_fuzz_targets>, <date>)
    """
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
        stream = os.popen(f'git --no-pager log -1 {commit_hash} --format=%cd --date=iso-strict')
        output = stream.read()
        stream.close()
        experiments[d] = (fuzz_target, output.replace("\n", ""))

    return experiments


def read_all_libraries(commit_hash: str = 'master') -> dict:
    """Reads all OSS-Fuzz projects and returns them with fuzz targen and commit date

    :param commit_hash: The commit hash, from which commit you want the experiments. (default=master)
    :return: A dictionary containing all projects, that have a fuzz_target specified. The format is:
    <project>: (<list_of_fuzz_targets>, <date>)
    """
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
        stream = os.popen(f'git --no-pager log -1 {commit_hash} --format=%cd --date=iso-strict')
        output = stream.read()
        experiments[d] = (fuzz_targets, output.replace('\n', ''))

    print("number of included experiments: ", len(experiments), "\n")
    return experiments



def main():
    # c34c308faad86d154b52586ff66de8d77187cafd: Commits on Jan 28, 2022 Submit Arrow-Java for inclusion (#7171)
    experiments = read_all_libraries('c34c308faad86d154b52586ff66de8d77187cafd')

    with open("/home/forian/uni/format_fuzzer_experiments/python_scripts/all_libs_2022-01-28.py", "a") as f:
        f.write("all_libs = {\n")
        for k, v in experiments.items():
            print(f"'{k}': {v},")
            f.write(f"\t'{k}': {v},\n")
        f.write('}\n')


main()
