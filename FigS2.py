# -*- coding: utf-8 -*-
"""
Created on Tue May 25 16:02:14 2021

@author: tgrassi, Roberto
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import pymannkendall as mk

'''
qus = ['precipitation', 'evaporation']
oases is a list with the oases order and names
years_ba is a list with the names of the years in the baseline. CAUTION: So far we have been using 30 years 1990-2019. Now it's 70 years 1951-2020. The end year is different!
years_rcp is a list with the names of the remaining years in the 2021-2100
months: A list of the 3-letter month names
models: A list of the 9 CORDEX models
cordex_ba: 'ba' for baseline. A numpy array with the climatological data. Its dimensions are [len(qus), len(oases), len(years), len(months), len(models)].
cordex_85: The same as cordex_ba, but the years are now the 80 years starting from 2021 for the rcp85 scenario
cordex_26 : Same as cordex_85, but for rcp2.6. It has a lot of np.nan because we only have 3 cordex models running the rcp2.6 scenario
'''

path_abs = "/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Oasis_paper/data_pr_evap.pkl"
path_rel = "data/data_pr_evap.pkl"

if os.path.exists(path_abs):
  path_save = '/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Figure/FigS2.png'
  path = path_abs
else:
  path_save = "FigS2.png"
  path = path_rel

with open(path, 'rb') as f:
  qus, oases, years_ba, years_rcp, months, models, cordex_ba, cordex_85, cordex_26 = pickle.load(f)

idx_eva = qus.index("evaporation")
idx_pre = qus.index("precipitation")

# average data on months, obtain [qus, oases, years, models]
data_ba = np.mean(cordex_ba, axis=3)
data_26 = np.mean(cordex_26, axis=3)
data_85 = np.mean(cordex_85, axis=3)


# concatenate baseline data and models data to have 1951-2100, [qus, oases, years, models]
data_all = np.append(data_ba, data_85, axis=2)

# concatenate years
years_all = np.append(years_ba, years_rcp)

# baseline is years averaged, obtain [qus, oases, models]
baseline = np.mean(data_ba, axis=2)

# prepare grid for the multi-panel
ncols = 4  # number of columns
fig = plt.figure(figsize=(8,7))

gs = gridspec.GridSpec(ncols, len(oases) // ncols + 1, hspace=0, wspace=0)

#axs = gs.subplots(sharex='col', sharey='row')

# loop on oases
i = 0
for ioasis, o in enumerate(oases):

  if ioasis == 8:
    i += 1

  # subtract baseline and slice oases and qus, obtain [years, models]
  data_eva = data_ba[idx_eva, ioasis, ...]-0 #- baseline[idx_eva, i]
  data_pre = data_ba[idx_pre, ioasis, ...]-0 #- baseline[idx_pre, i]
  data_eva_all = data_all[idx_eva, ioasis, ...]-0 #- baseline[idx_eva, i]
  data_pre_all = data_all[idx_pre, ioasis, ...]-0 #- baseline[idx_pre, i]

  ax = plt.subplot(gs[i % ncols, i // ncols])

  # evaporation - precipitation, [years, models]
  data_diff = data_pre - data_eva

  data_diff_all=data_pre_all-data_eva_all

  # count models
  _, nmodels = data_diff_all.shape

  # flatten data to have [years*models]
  data_diff = data_diff.flatten()
  data_diff_all = data_diff_all.flatten()
  # tile to have the corresponding years
  data_years = np.tile(years_all, nmodels)
  #data_years_ba=years_ba


  # remove NaNs
  data_years = data_years[~np.isnan(data_diff_all)]
  data_diff_all = data_diff_all[~np.isnan(data_diff_all)]

  # divide roughly into decades for debug
  nbins = (max(data_years) - min(data_years)) // 10

  # get the 5th percentile of the difference
  a = np.percentile(data_diff, 5)

  # get the years in the first 5 percentiles
  yy = data_years[data_diff_all <= a]


  # histogram counting years per decade (dry)
  hist, bins = np.histogram(yy, bins=nbins, range=[min(data_years), max(data_years)])
  bins_center = (bins[1:] + bins[:-1]) / 2.

  # MK test wet
  mk_result = mk.original_test(hist[bins_center >= 2020])
  print("dry %s %s %+f    %e" % (o.ljust(20), mk_result.trend.ljust(10), mk_result.slope, mk_result.p))

  # plot corresponding bars (dry)
  ax.bar(bins_center - 2, hist, width=4, color="tab:red", label="dry")

  # get the 95th percentile of the difference
  a = np.percentile(data_diff, 95)
  # get the years in the last 95 percentiles
  yy = data_years[data_diff_all >= a]


  # histogram counting years per decade (wet)
  hist, bins = np.histogram(yy, bins=nbins, range=[min(data_years), max(data_years)])
  bins_center = (bins[1:] + bins[:-1]) / 2.

  # MK test wet
  mk_result = mk.original_test(hist[bins_center >= 2020])
  print("wet %s %s %+f    %e" % (o.ljust(20), mk_result.trend.ljust(10), mk_result.slope, mk_result.p))

  # plot corresponding bars (wet)
  ax.bar(bins_center + 2, hist, width=4, color="xkcd:bright sky blue", label="wet")

  # oases name text label
  ax.text(2100, 17, o,fontsize=12, ha="right", va="top")

  # rotate years on x axis for readability
  plt.setp(ax.get_xticklabels(), rotation=40, ha='right', rotation_mode="anchor")
  ax.xaxis.set_major_locator(MultipleLocator(30))
  ax.xaxis.set_minor_locator(MultipleLocator(10))
  ax.yaxis.set_minor_locator(MultipleLocator(1))

  # set plot limit to have the same in each panel
  ax.set_ylim(0, 18)
  # leftmost panels have xlabel
  if i // ncols == 0:
    ax.set_ylabel("Model-years/\n decade", fontsize=10)
  else:
    ax.set_yticks([])

  # only last row as xlabels
  if i % ncols < len(oases) / ncols:
    ax.set_xticks([])

  # only first plot has legend
  if i == 0:
    ax.legend(loc="upper left", fontsize=9)

  # use this variable to skip the upper right corner
  i += 1


# remove spines and labels from the dummy plot in the bottom-right corner
#ax = plt.subplot(gs[-1, -1])
#ax.set_visible(False)

plt.savefig(path_save, bbox_inches='tight', dpi=800)
print("Figure saved to " + path_save)

