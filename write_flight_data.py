from opensky_api import OpenSkyApi
import numpy as np

api = OpenSkyApi()

states = api.get_states(bbox=(-90, 90, -180, 180))
lats = []
longs = []
alts = []
callsigns = []
for s in states.states:
	try:
		if s.baro_altitude > 15000:
			continue
	except TypeError: #check for NoneType in geo and baro altitude
		continue

	lats += [str(s.latitude)]
	longs += [str(s.longitude)]
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