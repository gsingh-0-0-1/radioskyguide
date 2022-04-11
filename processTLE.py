f = open('static/origtle.txt')
d = f.read()
f.close()

d = d.split('\n0')

def checkForStarlink(s):
    if "STARLINK" in s:
        return True
    else:
        return False

for i in range(len(d)):
    d[i] = "0 " + d[i]

sat_data = filter(checkForStarlink, d)

with open('static/newtle.txt', 'w') as f:
    f.write('\n'.join(sat_data))
