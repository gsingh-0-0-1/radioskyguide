HOMEDIR = '/home/gurmeharsingh/radioskyguide/'

f = open(HOMEDIR + 'static/origtle.txt')
d = f.read()
f.close()

d = d.split('\n0')

def checkForStarlink(s):
    if "STARLINK" in s or "GOES" in s:
        return True
    else:
        return False

for i in range(len(d)):
    d[i] = "0 " + d[i]

sat_data = filter(checkForStarlink, d)

with open(HOMEDIR + 'static/newtle.txt', 'w') as f:
    f.write('\n'.join(sat_data))
