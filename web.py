from flask import Flask
from flask import render_template
from flask import request
import sys
import time
import os
import numpy as np
import codecs
import ephem
import datetime
import pytz
import pandas as pd

def get_phase_on_day(year,month,day):
  """Returns a floating-point number from 0-1. where 0=new, 0.5=full, 1=new"""
  #Ephem stores its date numbers as floating points, which the following uses
  #to conveniently extract the percent time between one new moon and the next
  #This corresponds (somewhat roughly) to the phase of the moon.

  #Use Year, Month, Day as arguments
  date=ephem.Date(datetime.date(year,month,day))

  nnm = ephem.next_new_moon    (date)
  pnm = ephem.previous_new_moon(date)

  lunation=(date-pnm)/(nnm-pnm)

  #Note that there is a ephem.Moon().phase() command, but this returns the
  #percentage of the moon which is illuminated. This is not really what we want.

  return lunation

def process_ra(ra_dat):
    for i in range(len(ra_dat)):
        temp = ra_dat[i].split(":")
        num = 0
        for j in range(len(temp)):
            if j == 0:
                num = num + ( float(temp[j]) * 15)
            if j == 1:
                num = num + ( float(temp[j]) * 0.25)
            if j == 2:
                num = num + ( float(temp[j]) * (1/240))

        ra_dat[i] = num * np.pi / 180
    return ra_dat

def process_dec(dec_dat):
    for i in range(len(dec_dat)):
        temp = dec_dat[i].split(":")
        num = 0
        for j in range(len(temp)):
            num = num + ( float(temp[j]) / (60**j) )
            
        dec_dat[i] = num * np.pi / 180
    return dec_dat

atnf_data = open("psrcat.db")
atnf_data = atnf_data.read()
atnf_data = atnf_data.split('@-----------------------------------------------------------------')

data_to_plot = {}

ra_dat = []
dec_dat = []
dm_dat = []
name_dat = []

for i in range(len(atnf_data)):
    item = atnf_data[i]
    item = item.split('\n')
    data_to_plot[i] = ['', '', '', '']
    for j in range(len(item)):
        if item[j].startswith('RAJ'):
            ra = item[j].split(' ')
            while '' in ra:
                ra.pop(ra.index(''))
            ra = ra[1]
            data_to_plot[i][0] = ra
            

        if item[j].startswith('DECJ'):
            dec = item[j].split(' ')
            while '' in dec:
                dec.pop(dec.index(''))
            dec = dec[1]
            data_to_plot[i][1] = dec

        if item[j].startswith('DIST_DM1 '):
            dm = item[j].split(' ')
            while '' in dm:
                dm.pop(dm.index(''))
            dm = dm[1]

            data_to_plot[i][2] = dm

        if item[j].startswith('PSRJ'):
            name = item[j].split(' ')
            while '' in name:
                name.pop(name.index(''))
            name = name[1]

            data_to_plot[i][3] = str(name)


    #print(data_to_plot[i])
            
    if data_to_plot[i][0] == '' or data_to_plot[i][1] == '' or data_to_plot[i][2] == '' or data_to_plot[i][3] == '':
        del data_to_plot[i]

    try:
        ra_dat += [data_to_plot[i][0]]
        dec_dat += [data_to_plot[i][1]]
        dm_dat += [float(data_to_plot[i][2])]
        name_dat += [name]
    except KeyError:
        pass

atnf_ra_dat = process_ra(ra_dat)
atnf_dec_dat = process_dec(dec_dat)
atnf_name_dat = name_dat

##get data for the FRBCAT
##########

frb_data = open("frbcat.csv")
frb_data = frb_data.read()
frb_data = frb_data.replace('''"''', '')
frb_data = frb_data.split("\n")
frb_data = frb_data[1:]

frb_ra_dat = []
frb_dec_dat = []


for i in range(len(frb_data)-1):
    frb_data[i] = frb_data[i].split(",")
    frb_ra_dat += [frb_data[i][3]]
    frb_dec_dat += [frb_data[i][4]]

frb_ra_dat = process_ra(frb_ra_dat)
frb_dec_dat = process_dec(frb_dec_dat)

messier_data = open("messiercatalog.txt")
messier_data = messier_data.read()
messier_data = messier_data.split("\n")
#messier_data.remove('')
messier_ras = []
messier_decs = []
for i in range(len(messier_data)):
    messier_data[i] = messier_data[i].split(" ")

for i in range(len(messier_data)):
    while '' in messier_data[i]:
        messier_data[i].remove('')

for i in range(len(messier_data)):
    messier_ras += [messier_data[i][5] + ":" + messier_data[i][6]]
    messier_decs += [messier_data[i][7] + ":" + messier_data[i][8] + ":" + "00"]

for i in range(len(messier_ras)):
    part2 = messier_ras[i].split(".")[1]
    while part2 != '0' and part2[-1] == '0':
        part2 = part2.replace(part2[-1], '')
    messier_ras[i] = messier_ras[i].split(".")[0] + ":" + str(float(part2)*6)

messier_ras = process_ra(messier_ras)
messier_decs = process_dec(messier_decs)



rrat_ras = process_ra(open("rrat_ras.txt").read().split("\n"))
rrat_decs = process_dec(open("rrat_decs.txt").read().split("\n"))

nvss_ras = process_ra(open("nvss_ras.txt").read().split("\n"))
nvss_decs = process_ra(open("nvss_decs.txt").read().split("\n"))
nvss_lum = open("nvss_lum.txt").read().split("\n")
for i in range(len(nvss_lum)):
    nvss_lum[i] = float(nvss_lum[i].replace(" ", ''))
print(nvss_lum[:10])

r = 10

#Take care of some TLE stuff...
f = open('static/origtle.txt')
f = f.read()
f = f.split('\n0')
def checkforstarlink(s):
    if "STARLINK" in s:
        return True
    else:
        return False

for i in range(len(f)):
    f[i] = "0 " + f[i]

sat_data = filter(checkforstarlink, f)

with open('static/newtle.txt', 'w') as f:
    f.write('\n'.join(sat_data))

app = Flask(__name__)

@app.route('/')
def startup():
    return render_template('startup.html')

@app.route('/main')
def gui():
    ip = request.remote_addr

    if os.path.isfile('visitors/'+str(ip)+'.txt'):
        with open('visitors/'+str(ip)+'.txt', 'a+') as f:
            f.write(str(datetime.datetime.utcnow())+'\n')
    else:
        with open('visitors/'+str(ip)+'.txt', 'w') as f:
            f.write(str(datetime.datetime.utcnow())+'\n')

    utcdate = str(datetime.datetime.utcnow()).split(" ")[0]

    if os.path.isfile('logs/'+utcdate+'.txt'):
        with open('logs/'+utcdate+'.txt', 'a+') as f:
            f.write(str(datetime.datetime.utcnow())+"\t"+str(ip)+'\n')
    else:
        with open('logs/'+utcdate+'.txt', 'w') as f:
            f.write(str(datetime.datetime.utcnow())+"\t"+str(ip)+'\n')        

    declination = 0
    longitude = 0
    loc = request.args.get('loc')
    draw_atnf = request.args.get('drawatnf')
    draw_frb = request.args.get('drawfrb')
    if loc == "Allen Telescope Array":
        declination = 40.8178049
        longitude = -121.47173
        abbr = "ATA"
    elif loc == "Green Bank Observatory":
        declination = 38.4329869
        longitude = -79.8398566
        abbr = "GBO"
    elif loc == "Parkes Radio Telescope":
        declination = -32.9980473
        longitude = 148.2626028
        abbr = "PRT"
    elif loc == "Atacama Large Millimeter Array":
        declination = -23.023556
        longitude = -67.7548021
        abbr = "ALMA"
    else:
        declination = request.args.get("latitude")
        longitude = request.args.get("longitude")
        abbr = "--"

    moon = ephem.Moon(datetime.datetime.utcnow())
    moon_ra = str(moon.ra)
    moon_dec = str(moon.dec)
    moon_ra = process_ra([moon_ra])
    moon_dec = process_dec([moon_dec])

    utcdate = datetime.datetime.utcnow()

    return render_template('main.html', atnf_ra_dat_here = atnf_ra_dat,
                                        atnf_dec_dat_here = atnf_dec_dat,
                                        atnf_name_dat_here = atnf_name_dat,
                                        declination_here = str(declination),
                                        longitude_here = str(longitude),
                                        loc_here = str(loc),
                                        abbr_here = str(abbr),
                                        draw_atnf = draw_atnf,
                                        draw_frb = draw_frb,
                                        frb_ra_dat_here = frb_ra_dat,
                                        frb_dec_dat_here = frb_dec_dat,
                                        messier_ra_dat_here = messier_ras,
                                        messier_dec_dat_here = messier_decs,
                                        rrat_ra_dat_here = rrat_ras,
                                        rrat_dec_dat_here = rrat_decs,
                                        nvss_ra_dat_here = nvss_ras,
                                        nvss_dec_dat_here = nvss_decs,
                                        nvss_lum_dat_here = nvss_lum,
                                        moon_dec_here = moon_dec,
                                        moon_ra_here = moon_ra,
                                        lunation_here = get_phase_on_day(utcdate.year, utcdate.month, utcdate.day ))

    # f = codecs.open("main.html", 'r')
    # mainhtml = f.read()
    # mainhtml = mainhtml.replace('atnf_ra_dat_here', str(ra_dat))
    # mainhtml = mainhtml.replace('atnf_dec_dat_here', str(dec_dat))
    # mainhtml = mainhtml.replace('declination_here', str(declination))
    # mainhtml = mainhtml.replace('loc_here', str(loc))
    # mainhtml = mainhtml.replace('abbr_here', str(abbr))

    # return mainhtml

@app.route('/atnfdata')
def displayatnfdata():
    return str(atnf_ra_dat)+"$"+str(atnf_dec_dat)

@app.route('/messierdata')
def displaymessierdata():
    return str(messier_ras)+"$"+str(messier_decs)

@app.route('/frbdata')
def displayfrbdata():
    return str(frb_ra_dat)+"$"+str(frb_dec_dat)

@app.route('/redo')
def submain():
    return render_template('redo.html')

try:
    app.run(host = sys.argv[1], debug = True, port = int(sys.argv[2])) 
except IndexError:
    raise IndexError("Please enter the target IP as the first argument, and the target port as the second.")
