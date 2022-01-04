# -*- coding: utf-8 -*-
"""
Created on Fri May 14 15:05:25 2021

@author: Roberto
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pickle
import datetime
import os
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import matplotlib.dates as mdates
import pymannkendall as mk


path_data = "/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Oasis_paper/newdata.pkl"

if os.path.exists(path_data):
  path_save = '/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Figure/Fig2.png'
else:
  path_data = "data/newdata.pkl"
  path_save = "Fig2.png"


with open(path_data, 'rb') as f:
      dates, grace, graceerr, oases, prec, temp = pickle.load(f)

# average
temp_ann = np.nanmean(temp, axis=2)
temp_ann_1dec = temp_ann[:, :10]
temp_ann_lastdec = temp_ann[:, -10:]

temp_1dec_mean=np.nanmean(temp_ann_1dec, axis=1)
temp_lastdec_mean=np.nanmean(temp_ann_lastdec, axis=1)

temp_diff = temp_lastdec_mean - temp_1dec_mean

prec_ann = np.nanmean(prec,axis=2)
prec_ann_1dec = prec_ann[:, :10]
prec_ann_lastdec = prec_ann[:, -10:]

prec_1dec_mean = np.nanmean(prec_ann_1dec, axis=1)
prec_lastdec_mean = np.nanmean(prec_ann_lastdec, axis=1)

prec_diff = (prec_lastdec_mean - prec_1dec_mean) * 12
# select plot mode, precipitation or temperature
mode = "temperature"

if mode == "temperature":
  year_ref = 1983  # starting reference year
  yoff = 4  # offset year for decades, year_ref + yoff, e.g. 1983+4 starts from 1987
  cdata = temp  # dataset to use
  mult = 1  # multiplication factor (12 for precipitation bc average on months)
  wbar = 0.25  # width of the bars
  ylabel = "Temperature change from 1983-2012 avg (°C)"  # label on the y axsis
elif mode == "precipitation":
  year_ref = 1981
  yoff = 0
  cdata = prec
  mult = 12
  wbar = 0.2
  ylabel = "Precipitation change from 1981-2010 avg (mm/yr)"

figsize = (9, 6)

fig = plt.figure(figsize=figsize)

ax1 = fig.add_subplot(1, 1, 1)

cmap = matplotlib.cm.get_cmap('tab20')
colors = [cmap(k) for k in np.linspace(0, 1, 20)]

# sort lines using the last value
#idx = np.argsort(grace[:, -1])
#grace = grace[idx, :]

# size of the average in months
navg = 12

# loop on oases to plot
for i, o in enumerate(oases):
  # slice data for current oasis
  ydata = grace[i, :]
  # dates as x axis
  xdata = dates
  # plot data
  plt.plot(xdata, ydata, color=colors[i], alpha=0.2)

  # moving average
  avg = np.convolve(ydata, np.ones(navg)/navg, mode='full')[:-navg+1]
  plt.plot(xdata, avg, color=colors[i], label=o.split()[0])

  # Mann-Kendall Test (trend)
  mk_result = mk.original_test(avg)
  print("%s %s %+f    %e" % (o.ljust(30), mk_result.trend.ljust(30), mk_result.slope, mk_result.p))

# legend
plt.legend(loc="best", ncol=2, fontsize=12)
plt.ylabel('Liquid Water Equivalent change \n from 2002-2008 avg (cm)', labelpad=-1, fontsize=14)

# horizontal line y=0
plt.axhline(0e0, zorder=-99, ls="-", alpha=0.5, color="k")

# define minor ticks locator
plt.gca().yaxis.set_minor_locator(MultipleLocator(1))
plt.gca().xaxis.set_minor_locator(mdates.YearLocator(1))

# set left value in xlim
plt.gca().set_xlim(right=datetime.date(2021, 12, 1))

plt.subplots_adjust(wspace=0.25)
plt.savefig(path_save, bbox_inches='tight', dpi=900)
print("Figure saved to " + path_save)


