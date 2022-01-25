import subprocess

project = 'lzo'
fuzz_target = 'all_lzo_compress'
pwd = 'werdasliestkannhacken'   # not my actual password


c = 0
with open('../libs_todo', 'r') as f:
    x = f.read()

all = x.split(')')
for l in all:
    print(f"'{l[:l.find('(')-1]}': {l[l.find('('):]}),")

print(all)
