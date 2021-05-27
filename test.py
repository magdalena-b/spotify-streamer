from os import walk

from os import listdir
from os.path import isfile, join

f = files = [f for f in listdir("faces") if isfile(join("faces", f))]
print(f)
x = walk('faces')
print(walk("faces"))
for x in walk("faces"):

    print(x)
    break
