import string

with open('crypto.txt', 'rt') as f:
    data_string = f.read()

for punk in " .?,'":
    data_string = data_string.replace(punk, punk * 2)

def chunks(s, n):
    for start in range(0, len(s), n):
        yield s[start:start+n]

message = list(chunks(data_string, 2))[:-1]

ucases = string.uppercase

punks = list(chunks("..,,  ??''", 2))

n_set = sorted([x for x in set(message) if x not in punks])

l_map = dict([(n,u) for n,u in zip(n_set, ucases)])
for punk in punks:
    l_map[punk] = punk[0]

output = ''.join([l_map[x] for x in message])
print output

with open('cryptext.txt', 'wt') as f:
    f.write(output)