import subprocess
import os

LIB_PATH = "/home/florian/uni/test_run_3"


def write_to_file(filename, lib_name, fuzz_target, date, file_types):
    with open(f'../{filename}', 'a') as f:
        f.write(f"'{lib_name}': ('{fuzz_target}', '{date}')\n")
        for ft in file_types:
            f.write(f'{ft}')
        f.write('\n\n')


def write_to_file_list(filename, lib_name, fuzz_target, date):
    with open(f'../{filename}', 'a') as f:
        f.write(f"'{lib_name}': ('{fuzz_target}', '{date}'),\n")


def main():
    libs = [d for d in os.listdir(LIB_PATH) if not os.path.isfile(os.path.join(LIB_PATH, d))]
    c = 0
    ascii, fail, others = [], [], []

    for lib in libs:
        lib_name = lib[0:lib.find('__')]
        fuzz_target = lib[lib.find('__')+2:lib.rfind('__')]
        date = lib[lib.rfind('__')+2:]

        out_path = os.path.join(LIB_PATH, lib, "out")

        if not os.path.exists(out_path):
            fail.append(f"'{lib_name}': ('{fuzz_target}', '{date}'),\n")
            continue

        outs = [d for d in os.listdir(out_path) if not os.path.isfile(os.path.join(out_path, d))]
        if not outs:
            fail.append(f"'{lib_name}': ('{fuzz_target}', '{date}'),\n")
        print(f'{lib_name}: ({fuzz_target}, {date})')
        for o in outs:
            seed_path = os.path.join(out_path, o, 'seeds')
            if os.path.isdir(seed_path):
                seeds = [seed for seed in os.listdir(seed_path) if os.path.isfile(os.path.join(seed_path, seed))]
                file_types = ["", ]
                for seed in seeds:
                    try:
                        p = subprocess.run(['file',  f"{seed}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=seed_path)
                        file_types.append(p.stdout.decode())
                    except Exception as e:
                        print(e)
                if seeds:
                    c+=1
                    # check if file type is interesting
                    ascii_amount = sum([1 if "ASCII" in ft else 0 for ft in file_types])
                    if ascii_amount >= len(seeds)-1:
                        #write_to_file_list('oss-fuzz_ascii', lib_name, fuzz_target, date)
                        pass
                    else:
                        write_to_file('oss-fuzz_others', lib_name, fuzz_target, date, file_types)
                        pass
                    continue
            fail.append(f"'{lib_name}': ('{fuzz_target}', '{date}'),\n")

    print("iterated through all libs \n")
    fail.sort()
    with open('../oss-fuzz_fail', 'a') as f:
        for i in fail:
            #f.write(i)
            print(i)

    print('Amount of libraries: {}'.format(len(libs)))
    print('Amount with seed: {}'.format(c))


main()
