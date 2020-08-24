from opensky_api import OpenSkyApi
import numpy as np

api = OpenSkyApi()

states = api.get_states(bbox=(-90, 90, -180, 180))
lats = []
longs = []
alts = []
callsigns = []
for s in states.states:
    lats += [str(s.latitude * np.pi / 180)]
    longs += [str((s.longitude + 180) * np.pi / 180)]
    alts += [str(s.baro_altitude)]
    callsigns += [str(s.callsign)]

lats = ",".join(lats)
longs = ",".join(longs)
alts = ",".join(alts)
callsigns = ",".join(callsigns)

final = lats + "$" + longs + "$" + alts + "$" + callsigns

f = open("static/flightdata.txt", "w")
f.write(final)
f.close()