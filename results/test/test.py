from oss_fuzz_others import others
from oss_fuzz_others_test import test

for k, v in test.items():
    others.pop(k)

for k, v in others.items():
    ft, d, seeds = v
    print(f"'{k}': ('{ft}', '{d}', [")
    for s in seeds:
        print(f'\"\"\"{s}\"\"\",')
    print(']),\n')


others, working = {}, {}
