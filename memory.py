from sys import argv, exit
from os import geteuid
from re import findall
from pprint import pprint


assert len(argv) == 4  # python file.py <pid> <term to search> <string to replace with>
assert argv[1].isdigit()  # must be integer
assert not geteuid()  # must be root

map_pattern = r"(?P<address>[0-9a-f\-]+) rw"
address_map = []

with open("/proc/%s/maps" % argv[1]) as maps:
    for line in maps:
        pats = findall(map_pattern, line)
        if not pats:
            continue
        address_map.append(line.rstrip())

address_map = [x.split()[0] for x in address_map]

with open("/proc/%s/mem" % argv[1], "r+b") as memory: 
    for address in address_map:
        try:
            memory.seek(int(address.split('-')[0], 16))
        except IOError:
            print("| IOError caught when reading memory at %s." % (hex(int(address.split('-')[0], 16))))
            continue
        
        data = memory.read(int(address.split('-')[1], 16) - int(address.split('-')[0], 16))
        if argv[2] in data:
            print("| Found %s in memory at %s" % (argv[2], hex(int(address.split('-')[0], 16))))
            index = data.index(argv[2])
            memory.seek(int(address.split('-')[0], 16) + index)
            try:
                memory.write(argv[3])
            except IOError:
                print("| IOError caught when writing to memory")
                continue
            print("| Wrote to memory successfully")
