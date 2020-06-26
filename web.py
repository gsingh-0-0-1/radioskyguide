from flask import Flask
from flask import render_template
from flask import request
import sys
import time
import os
import numpy as np
import codecs
import ephem
from datetime import datetime
import pytz

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

for i in range(len(atnf_data)):
    item = atnf_data[i]
    item = item.split('\n')
    data_to_plot[i] = ['', '', '']
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

    #print(data_to_plot[i])
            
    if data_to_plot[i][0] == '' or data_to_plot[i][1] == '' or data_to_plot[i][2] == '':
        del data_to_plot[i]

    try:
        ra_dat += [data_to_plot[i][0]]
        dec_dat += [data_to_plot[i][1]]
        dm_dat += [float(data_to_plot[i][2])]
    except KeyError:
        pass

atnf_ra_dat = process_ra(ra_dat)
atnf_dec_dat = process_dec(dec_dat)

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

r = 10

app = Flask(__name__)

@app.route('/')
def startup():
    return render_template('startup.html')

@app.route('/main')
def gui():
    declination = 0
    longitude = 0
    loc = request.args.get('loc')
    draw_atnf = request.args.get('drawatnf')
    draw_frb = request.args.get('drawfrb')
    if loc == "Allen Telescope Array":
        declination = 40.8178049
        abbr = "ATA"
    if loc == "Green Bank Observatory":
        declination = 38.4329869
        abbr = "GBO"
    if loc == "Parkes Radio Telescope":
        declination = -32.9980473
        abbr = "PRT"
    if loc == "Atacama Large Millimeter Array":
        declination = -23.023556
        abbr = "ALMA"



    if loc == "Celestial North Pole":
        declination = 90
        abbr = "CNP"
    if loc == "Celestial South Pole":
        declination = -90
        abbr = "CSP"
    if loc == "Celestial Equator":
        declination = 0
        abbr = "CE"

    if draw_atnf == None:
        draw_atnf = 'false'

    if draw_frb == None:
        draw_frb = 'false'

    return render_template('main.html', atnf_ra_dat_here = atnf_ra_dat,
                                        atnf_dec_dat_here = atnf_dec_dat,
                                        declination_here = str(declination),
                                        loc_here = str(loc),
                                        abbr_here = str(abbr),
                                        draw_atnf = draw_atnf,
                                        draw_frb = draw_frb,
                                        frb_ra_dat_here = frb_ra_dat,
                                        frb_dec_dat_here = frb_dec_dat)

    # f = codecs.open("main.html", 'r')
    # mainhtml = f.read()
    # mainhtml = mainhtml.replace('atnf_ra_dat_here', str(ra_dat))
    # mainhtml = mainhtml.replace('atnf_dec_dat_here', str(dec_dat))
    # mainhtml = mainhtml.replace('declination_here', str(declination))
    # mainhtml = mainhtml.replace('loc_here', str(loc))
    # mainhtml = mainhtml.replace('abbr_here', str(abbr))

    # return mainhtml

@app.route('/sidtime')
def sidtime():
    longitude = 0

    loc = request.args.get('loc')

    if loc == "Allen Telescope Array":
        longitude = -121.4695413
    if loc == "Green Bank Observatory":
        longitude = -79.8398566
    if loc == "Parkes Radio Telescope":
        longitude = 148.2626028

    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    days_since_j2000 = 0
    datenow = datetime.now()
    datenow = list(datenow.timetuple())

    #get the years * 365
    days_since_j2000 += (datenow[0] - 2000) * 365

    #add leap days
    days_since_j2000 += int((datenow[0]-2000)/4)

    #add days in months
    for rep in range(datenow[1]-1):
        days_since_j2000 += month_days[rep]

    days_since_j2000 += datenow[2]

    day_frac = datenow
    day_frac = day_frac[3] + day_frac[4]/60 + day_frac[5]/3600
    day_frac = day_frac / 24

    days_since_j2000 += day_frac

    hours_passed = list(datetime.utcnow().timetuple())
    hours_passed = hours_passed[3] + hours_passed[4]/60 + hours_passed[5]/3600

    sidereal = 100.46
    sidereal += (0.985647 * days_since_j2000)
    sidereal += longitude
    sidereal += 15*hours_passed

    sidereal = sidereal%360
    sidereal = sidereal/15

    sidereal_h = int(sidereal)
    sidereal_m = sidereal - sidereal_h
    sidereal_m = (sidereal_m * 60)
    sidereal_s = sidereal_m - int(sidereal_m)
    sidereal_m = int(sidereal_m)

    sidereal_s = int(sidereal_s * 60)

    if len(str(sidereal_h)) < 2:
        sidereal_h = "0" + str(sidereal_h)

    if len(str(sidereal_m)) < 2:
        sidereal_m = "0" + str(sidereal_m)

    if len(str(sidereal_s)) < 2:
        sidereal_s = "0" + str(sidereal_s)

    return str(sidereal_h)+":"+str(sidereal_m)+":"+str(sidereal_s)

app.run(host = '0.0.0.0', debug = True, port = 80) 
