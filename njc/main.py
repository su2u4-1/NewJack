from lexer import lexer


path = input("Enter the path of the file: ")
with open(path, "r") as f:
    code = f.readlines()
tokens = lexer(code, path)
for i in tokens:
    print(i)
with open(".nj", "w") as f:
    for i in tokens:
        if i.type != "comment":
            f.write(str(i.constant) + "\n")
