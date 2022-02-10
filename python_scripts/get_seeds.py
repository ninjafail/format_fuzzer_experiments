import subprocess
import os
import itertools


LIB_PATH = "/home/forian/uni/test_run_5"
EXPERIMENT_NAME = LIB_PATH[LIB_PATH.rfind("/")+1:]
DEBUG = False
# when printing there are more variables to control, whether to print to an output file or not, marked with TODO

fail = {}


def debug_print(x):
    if DEBUG:
        print(x, end='')


def insert_into_fail_dict(lib_name: str, fuzz_target: str, date: str):
    x = fail.get(lib_name)
    if x:
        ft = x[0]
        ft.append(fuzz_target)
        fail[lib_name] = (ft, date)
    else:
        fail[lib_name] = ([fuzz_target], date)


def get_fuzzing_exp():
    libs = [d for d in os.listdir(LIB_PATH) if not os.path.isfile(os.path.join(LIB_PATH, d))]
    c = 0
    ascii, others = [], []

    print(LIB_PATH)
    print("Searching all seeds in the out directories ... ", end='')
    for lib in libs:
        has_worked = False
        lib_name = lib[0:lib.find('__')]
        fuzz_target = lib[lib.find('__') + 2:lib.rfind('__')]
        date = lib[lib.rfind('__') + 2:]
        debug_print(f'{lib_name}: ({fuzz_target}, {date})\n')

        log_path = os.path.join(LIB_PATH, lib, "logs")
        if not os.path.exists(log_path):
            insert_into_fail_dict(f"DeepFail:{lib_name}", fuzz_target, date)
            continue
        with open(f"{log_path}/out", "r") as f:
            x = f.readlines()
            for line in x:
                if "Entering queue cycle 1" in line:
                    has_worked = True

        if not has_worked:
            insert_into_fail_dict(f"{lib_name}", fuzz_target, date)
        else:
            out_path = os.path.join(LIB_PATH, lib, "out")

            # if out_dir does not exist -> fail (should always exist)
            if not os.path.exists(out_path):
                insert_into_fail_dict(lib_name, fuzz_target, date)
                continue

            # get all directories inside of out
            outs = [d for d in os.listdir(out_path) if not os.path.isfile(os.path.join(out_path, d))]
            # if empty -> fail
            if not outs:
                insert_into_fail_dict(lib_name, fuzz_target, date)
                continue

            # for every out directory, that contains something
            for o in outs:
                # get all seed files
                seed_path = os.path.join(out_path, o, 'seeds')
                if os.path.isdir(seed_path):
                    seeds = [seed for seed in os.listdir(seed_path) if os.path.isfile(os.path.join(seed_path, seed))]
                    file_types = []
                    # for every seed file get the output of the file command
                    for seed in seeds:
                        try:
                            p = subprocess.run(['file', f"{seed}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               cwd=seed_path)
                            file_types.append(p.stdout.decode()[42:].replace('\n', ''))  # ignore the hash
                        except Exception as e:
                            print(e)
                    if seeds:
                        c += 1
                        # check if file type is interesting
                        ascii_amount = sum([1 if "ASCII" in ft else 0 for ft in file_types])
                        # if it's just ascii, append to ascii list otherwise to others
                        if ascii_amount >= len(seeds) - 1:
                            ascii.append((lib_name, fuzz_target, date))
                        else:
                            others.append((lib_name, fuzz_target, date, file_types))
                        continue
                # if neither seed path, nor is a directory or there were no seeds -> fail
                insert_into_fail_dict(lib_name, fuzz_target, date)
    print("Done.")

    print("\nIterated through all libs. Writing to files now ... ")
    print("\tWriting all failed libs ... ", end='')
    should_write_fail = True  # TODO
    with open('../results/oss-fuzz_fail_test', 'a') as f:
        f.write(f"\n\n\n-----------------------------------------------------{EXPERIMENT_NAME}---------------------------------------------------------\n")
        for lib_name, (fuzz_targets, date) in fail.items():
            x = f"'{lib_name}': ({list(set(fuzz_targets))}, '{date}'), \n"
            if should_write_fail:
                f.write(x)
            debug_print(x)
    print("Done.")

    print("\tWriting all ascii libs ... ", end='')
    ascii = list(set(ascii))
    should_write_ascii = True  # TODO
    with open('../results/oss-fuzz_ascii_test', 'a') as f:
        f.write(f"\n\n\n-----------------------------------------------------{EXPERIMENT_NAME}---------------------------------------------------------\n")
        for lib_name, fuzz_target, date in ascii:
            x = f"'{lib_name}': ('{fuzz_target}', '{date}'), \n"
            if should_write_ascii:
                f.write(x)
            debug_print(x)
    print("Done.")

    print("\tWriting all others libs ... ", end='')
    others.sort()
    others = list(others for others, _ in itertools.groupby(others))
    should_write_others = True  # TODO
    with open('../results/oss-fuzz_others_test', 'a') as f:
        f.write(f"\n\n\n-----------------------------------------------------{EXPERIMENT_NAME}---------------------------------------------------------\n")
        for lib_name, fuzz_target, date, file_types in others:
            x = f"'{lib_name}': ('{fuzz_target}', '{date}', [\n"
            if should_write_others:
                f.write(x)
            debug_print(x)
            for ft in list(set(file_types)):
                x = f"\t'{ft}'\n"
                if should_write_others:
                    f.write(x)
                debug_print(x)
            if should_write_others:
                f.write("]),\n\n")
            debug_print("]),\n")
    print("Done.")
    print("Done.")

    print('Amount of libraries: {}'.format(len(libs)))
    print('Amount with seed: {}'.format(c))
    print(f"Failed libs: {len(fail.items())}")
    print(f"Ascii libs: {len(ascii)}")
    print(f"Other libs: {len(others)}")


def main():
    libs = [d for d in os.listdir(LIB_PATH) if not os.path.isfile(os.path.join(LIB_PATH, d))]
    c = 0
    ascii, others = [], []

    print(LIB_PATH)
    print("Searching all seeds in the out directories ... ", end='')
    for lib in libs:
        lib_name = lib[0:lib.find('__')]
        fuzz_target = lib[lib.find('__')+2:lib.rfind('__')]
        date = lib[lib.rfind('__')+2:]
        debug_print(f'{lib_name}: ({fuzz_target}, {date})\n')

        out_path = os.path.join(LIB_PATH, lib, "out")

        # if out_dir does not exist -> fail (should always exist)
        if not os.path.exists(out_path):
            insert_into_fail_dict(lib_name, fuzz_target, date)
            continue

        # get all directories inside of out
        outs = [d for d in os.listdir(out_path) if not os.path.isfile(os.path.join(out_path, d))]
        # if empty -> fail
        if not outs:
            insert_into_fail_dict(lib_name, fuzz_target, date)
            continue

        # for every out directory, that contains something
        for o in outs:
            # get all seed files
            seed_path = os.path.join(out_path, o, 'seeds')
            if os.path.isdir(seed_path):
                seeds = [seed for seed in os.listdir(seed_path) if os.path.isfile(os.path.join(seed_path, seed))]
                file_types = []
                # for every seed file get the output of the file command
                for seed in seeds:
                    try:
                        p = subprocess.run(['file',  f"{seed}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=seed_path)
                        file_types.append(p.stdout.decode()[42:].replace('\n', ''))  # ignore the hash
                    except Exception as e:
                        print(e)
                if seeds:
                    c += 1
                    # check if file type is interesting
                    ascii_amount = sum([1 if "ASCII" in ft else 0 for ft in file_types])
                    # if it's just ascii, append to ascii list otherwise to others
                    if ascii_amount >= len(seeds)-1:
                        ascii.append((lib_name, fuzz_target, date))
                    else:
                        others.append((lib_name, fuzz_target, date, file_types))
                    continue
            # if neither seed path, nor is a directory or there were no seeds -> fail
            insert_into_fail_dict(lib_name, fuzz_target, date)
    print("Done.")

    print("\nIterated through all libs. Writing to files now ... ")
    print("\tWriting all failed libs ... ", end='')
    should_write_fail = True   # TODO
    with open('../results/oss-fuzz_fail', 'a') as f:
        for lib_name, (fuzz_targets, date) in fail.items():
            x = f"'{lib_name}': ({list(set(fuzz_targets))}, '{date}'), \n"
            if should_write_fail:
                f.write(x)
            debug_print(x)
    print("Done.")

    print("\tWriting all ascii libs ... ", end='')
    ascii = list(set(ascii))
    should_write_ascii = True  # TODO
    with open('../results/oss-fuzz_ascii', 'a') as f:
        for lib_name, fuzz_target, date in ascii:
            x = f"'{lib_name}': ('{fuzz_target}', '{date}'), \n"
            if should_write_ascii:
                f.write(x)
            debug_print(x)
    print("Done.")

    print("\tWriting all others libs ... ", end='')
    others.sort()
    others = list(others for others, _ in itertools.groupby(others))
    should_write_others = True  # TODO
    with open('../results/oss-fuzz_others', 'a') as f:
        for lib_name, fuzz_target, date, file_types in others:
            x = f"'{lib_name}': ('{fuzz_target}', '{date}', [\n"
            if should_write_others:
                f.write(x)
            debug_print(x)
            for ft in list(set(file_types)):
                x = f"\t'{ft}'\n"
                if should_write_others:
                    f.write(x)
                debug_print(x)
            if should_write_others:
                f.write("]),\n\n")
            debug_print("]),\n")
    print("Done.")
    print("Done.")

    print('Amount of libraries: {}'.format(len(libs)))
    print('Amount with seed: {}'.format(c))
    print(f"Failed libs: {len(fail.items())}")
    print(f"Ascii libs: {len(ascii)}")
    print(f"Other libs: {len(others)}")


# main()
get_fuzzing_exp()
