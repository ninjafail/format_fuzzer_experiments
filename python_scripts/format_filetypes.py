res = []
with open("filetypes.txt", "r") as f:
    input = f.readlines()

for x in input:
    x = x.replace("\t","").replace("\n", "")
    if ".bt" in x:
        res.append(x+"\n")
with open("../filetypes_actual.txt", "w") as f:
    f.writelines(res)
