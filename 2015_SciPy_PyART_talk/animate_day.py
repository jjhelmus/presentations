#! /usr/bin/env python
""" Create an animation of the KEWX NEXRAD radar near Austin, TX """

import ftplib
import datetime
import urllib

import matplotlib.pyplot as plt
from matplotlib import animation

import pyart


SUBDIR = 'SL.us008001/DF.of/DC.radar/DS.p19r0/SI.kewx/'


def get_time_and_name(line):
    """ Parse time and filename from a FTP directory listing. """
    words = line.split()
    ts = '%s-%s-2015 %s' % (words[5], words[6], words[7])
    dt = datetime.datetime.strptime(ts, '%b-%d-%Y %H:%M')
    fname = words[-1]
    return fname, dt


if __name__ == "__main__":

    # log into the FTP site
    ftp = ftplib.FTP('tgftp.nws.noaa.gov')
    ftp.login()

    # parse directory listing
    dir_data = []
    ftp.cwd(SUBDIR)
    ftp.dir(dir_data.append)

    # sort files by time and limit
    file_data = [get_time_and_name(line) for line in dir_data]
    file_data.sort(key=lambda x: x[1])
    file_data = file_data[:-1]   # remove last sn.last from list

    def animate(nframe):
        """ Animate a single frame. """
        plt.clf()
        fname = file_data[nframe][0]
        url = 'ftp://tgftp.nws.noaa.gov/' + SUBDIR + fname
        print "Frame:", nframe, "File:", fname
        fh = urllib.urlopen(url)
        radar = pyart.io.read_nexrad_level3(fh)
        display = pyart.graph.RadarMapDisplay(radar)
        display.plot_ppi_map(
            'reflectivity', vmin=-32, vmax=80, cmap='pyart_NWSRef',
            resolution='c', title=display.time_begin.isoformat(),
            embelish=False)
        display.basemap.drawcounties()
        display.basemap.plot([-97.75], [30.25], 'k*', ms=15, latlon=True)
        return

    # generate animation
    fig = plt.figure(figsize=(10, 8))
    anim = animation.FuncAnimation(fig, animate, frames=len(file_data))
    anim.save('kewx_animation.gif', writer='imagemagick', fps=20)
