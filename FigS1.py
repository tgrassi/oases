# -*- coding: utf-8 -*-
"""
Created on Sat May 29 18:46:04 2021

@author: Roberto
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pickle
import os
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import pymannkendall as mk


path_data = '/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Oasis_paper/newdata.pkl'

if os.path.exists(path_data):
  path_save = '/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Figure/FigS1.png'
else:
  path_data = "data/newdata.pkl"
  path_save = 'FigS1.png'

with open(path_data, 'rb') as f:
      dates, grace, graceerr, oases, prec, temp = pickle.load(f)

# select plot mode, precipitation or temperature
mode = "temperature"


year_ref = 1983  # starting reference year
yoff = 4  # offset year for decades, year_ref + yoff, e.g. 1983+4 starts from 1987
cdata = temp  # dataset to use
mult = 1  # multiplication factor (12 for precipitation bc average on months)
wbar = 0.25  # width of the bars
ylabel = "Temperature change \n from 1983-2012 avg (°C)"  # label on the y axsis


#cmap = matplotlib.colors.ListedColormap(['xkcd:light royal blue','xkcd:yellow','xkcd:red'])
cmap = matplotlib.cm.get_cmap('coolwarm')
# colors for vertical shading
colors_shading = ["#eeeeec", "#ffffff"]

# average on months to have prec[oases, years(1981-2020)]
temp = np.mean(cdata, axis=2)*mult

# use first years as baseline, obtaining prec_ba[oases]
temp_ba = np.mean(temp[:, :30], axis=1)

# number of decades
ndecs = len(temp[0, :])//10

# store data per decade as average of the differences with the baseline, [decades, oases]
ydata = [[] for _ in range(ndecs)]
colors = []
# loop on oases
for i, o in enumerate(oases):
    for j in range(ndecs):
      d = np.mean(temp[i, yoff+j*10: yoff+(j+1)*10]) - temp_ba[i]
      ydata[j].append(d)

ydata = np.array(ydata)

print("\nTrend temperatures")
# MK test temperatures
for i, o in enumerate(oases):
  # Mann-Kendall Test (trend)
  mk_result = mk.original_test(temp[i, :])
  print("%s %s %+f    %e" % (oases[i].ljust(30), mk_result.trend.ljust(30), mk_result.slope, mk_result.p))


figsize = (11,7)
fig = plt.figure(figsize=figsize)
ax1 = fig.add_subplot(2,1,1)


# loop on data to plot
for j, y in enumerate(ydata):
  # range as big as the number of oases
  xdata = np.arange(len(y))
  # normalize decade to use the color of the colormap
  cnorm = j / (len(ydata) - 1) * 0.8 + 0.2
  # decade label for legend
  label = "%d-%d" % (yoff+year_ref+j*10, yoff+year_ref-1+(j+1)*10)

  # plot scatter points
  #plt.scatter(xdata+j*0.1-0.2, y, label="%d-%d" % (year_ref+j*10, year_ref-1+(j+1)*10), marker="s", color=cmap(cnorm))

  # plot the bar
  plt.bar(xdata+j*wbar-ndecs*wbar/2+wbar/2, y, color=cmap(cnorm), width=wbar, zorder=99, alpha=0.7, label=label)

# background vertical shading to divide oases
for i, o in enumerate(oases):
  plt.gca().axvspan(i-0.5, i+0.5 , color=colors_shading[i%2], zorder=-999)

# horizontal line y=0
plt.axhline(0, zorder=-99, alpha=1., color="k", ls="-", lw=.3)

# legend
plt.legend(loc="upper right",fontsize=7)

# add a tick for each oases position
plt.gca().set_xticks(xdata)

# plt.ylim(-0.75, 0.8)

plt.gca().yaxis.set_minor_locator(MultipleLocator(0.1))

plt.ylabel(ylabel,fontsize=12)

#plt.tight_layout()

# ************ PRECIPITATION ***************

mode = "precipitation"
year_ref = 1981
yoff = 0
cdata = prec
mult = 12
wbar = 0.2
ylabel = "Precipitation change \n from 1981-2010 avg (mm/yr)"

cmap = matplotlib.colors.ListedColormap(['xkcd:brown','xkcd:clay brown','xkcd:greenblue','xkcd:dark green blue'])
#cmap = matplotlib.cm.get_cmap('flag')
# colors for vertical shading
colors_shading = ["#eeeeec", "#ffffff"]

# average on months to have prec[oases, years(1981-2020)]
prec = np.mean(cdata, axis=2)*mult

# use first years as baseline, obtaining prec_ba[oases]
prec_ba = np.mean(prec[:, :30], axis=1)

# number of decades
ndecs = len(prec[0, :])//10

# store data per decade as average of the differences with the baseline, [decades, oases]
ydata = [[] for _ in range(ndecs)]
colors = []
# loop on oases
for i, o in enumerate(oases):
    for j in range(ndecs):
      d = np.mean(prec[i, yoff+j*10: yoff+(j+1)*10]) - prec_ba[i]
      ydata[j].append(d)

ydata = np.array(ydata)

# MK test precipitations
print("\nTrend precipitations")
for i, o in enumerate(oases):
  # Mann-Kendall Test (trend)
  mk_result = mk.original_test(prec[i, :])
  print("%s %s %+f    %e" % (oases[i].ljust(30), mk_result.trend.ljust(30), mk_result.slope, mk_result.p))


ax1 = fig.add_subplot(2,1,2)

# loop on data to plot
for j, y in enumerate(ydata):
  # range as big as the number of oases
  xdata = np.arange(len(y))
  # normalize decade to use the color of the colormap
  cnorm = j / (len(ydata) - 1) * 0.8 + 0.2
  # decade label for legend
  label = "%d-%d" % (yoff+year_ref+j*10, yoff+year_ref-1+(j+1)*10)

  # plot scatter points
  #plt.scatter(xdata+j*0.1-0.2, y, label="%d-%d" % (year_ref+j*10, year_ref-1+(j+1)*10), marker="s", color=cmap(cnorm))

  # plot the bar
  plt.bar(xdata+j*wbar-ndecs*wbar/2+wbar/2, y, color=cmap(cnorm), width=wbar, zorder=99, alpha=0.7, label=label)

# background vertical shading to divide oases
for i, o in enumerate(oases):
  plt.gca().axvspan(i-0.5, i+0.5 , color=colors_shading[i%2], zorder=-999)

# horizontal line y=0
plt.axhline(0, zorder=-99, alpha=1., color="k", ls="-", lw=.3)


# legend
plt.legend(loc="upper right", fontsize=7)

# add a tick for each oases position
plt.gca().set_xticks(xdata)

# replace numbers with oases names
oases_name = []
for o in oases:
  if "Ghizlane" in o:
    o = "M'hamid E."
  if "Archei" in o:
    o = "Guelta d'A."
  oases_name.append(o)

plt.gca().set_xticklabels(oases_name)
plt.xticks(rotation=30, ha="right")

plt.ylabel(ylabel,fontsize=12)
#plt.ylim(-35, 35)
#plt.tight_layout()
plt.subplots_adjust(hspace=0e0)
#plt.subplots_adjust(hspace=0.45)

plt.savefig(path_save, bbox_inches='tight', dpi=700)
print("Figure saved to " + path_save)



