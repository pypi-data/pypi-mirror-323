import toml

with open('config.toml','r') as f:
    data = toml.load(f)

class String():
    def __init__(self,value=None,file=None):
        if not file == None:
            self.file = file
            with open(file,'r') as f:
                self.value = f.readlines()
        elif not value == None:
            self.value = value
        else:
            raise SyntaxError('invalid syntax')

def countstr(st):
    output = {}
    for i in st:
        if i in output:
            output[i] += 1
        else:
            output[i] = 1
    return output

def save_add(filepath,string):
    with open(filepath,'a') as f:
        f.write(string)
    with open(filepath,'r') as f:
        content = f.readlines()
    return content