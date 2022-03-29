import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
from integrate_all import all_libs_commits
from ExperimentRunner import get_fuzz_targets


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

        # get the targets
        fuzz_targets = get_fuzz_targets(dir_path)
        if not fuzz_targets:
            fuzz_targets = [d]

        # get the git date
        os.chdir(os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d))
        stream = os.popen(f'git --no-pager log -1 {commit_hash} --format=%cd --date=iso-strict')
        output = stream.read()
        experiments[d] = (fuzz_targets, output.replace('\n', ''))

    print("number of included experiments: ", len(experiments), "\n")
    return experiments


def read_commit_libs():
    libs = [d for d in os.listdir(OSS_FUZZ_BENCHMARKS_PATH) if
            not os.path.isfile(os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d))]
    experiments = dict()
    c = 0
    for d in libs:
        dir_path = os.path.join(OSS_FUZZ_BENCHMARKS_PATH, d)
        subprocess.run('git checkout master', shell=True, cwd=OSS_FUZZ_BENCHMARKS_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p = subprocess.run('git --no-pager log --pretty=format:"%h" -- .', shell=True, cwd=dir_path,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        commit_hashes = p.stdout.decode().split()
        commit_hashes = list(set([commit_hashes[i] for i in [0,len(commit_hashes)//2, -1]]))

        res = []
        for commit_hash in commit_hashes:
            p = subprocess.run(f'git checkout {commit_hash}', shell=True, cwd=dir_path,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            fuzz_targets = get_fuzz_targets(dir_path)
            if not fuzz_targets:
                fuzz_targets = [d]

            p = subprocess.run(f'git --no-pager log -1 {commit_hash} --format=%cd --date=iso-strict', shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dir_path)
            date = p.stdout.decode().replace('\n', '')
            res.append((fuzz_targets, commit_hash, date))
        experiments[d] = res
        print(f"\t'{d}': {res},")

    return experiments


def remove_ascii(all: dict, fail: dict):
    for f in fail.keys():
        if all.get(f): all.pop(f)
        else: print(f)

    print(all)

def main():
    # c34c308faad86d154b52586ff66de8d77187cafd: Commits on Jan 28, 2022 Submit Arrow-Java for inclusion (#7171)
    # experiments = read_all_libraries('c34c308faad86d154b52586ff66de8d77187cafd')

    remove_ascii(all_libs_commits.all_libs, all_libs_commits.ascii)
    experiments = read_commit_libs()

    with open("/integrate_all/all_libs_2022-01-28.py", "a") as f:
        #f.write("all_libs = {\n")
        for k, v in experiments.items():
            print(f"'{k}': {v},")
            #f.write(f"\t'{k}': {v},\n")
        #f.write('}\n')

# main()
x = read_all_libraries('43873069112a742fe9cdf8c0955098c1539aea7a')
print('{')
for k,v in x.items():
    print(f"'{k}': {v},")
print('}')
# Aug 19, 2021