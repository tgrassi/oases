import pickle
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import os
from scipy import stats
from tqdm import tqdm
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator, FixedLocator


font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 14}

matplotlib.rc('font', **font)


'''

- qus: A list of the names of our climatological quantities. Temps are in Celsius, Precip and evaporation are in mm/month, wind speed is in m/s
- oases: A list of the names of our oases
- years: A list of the 30 baseline years. You probably won't need this
- months: A list of the 3-letter month names
- models: A list of the 9 CORDEX models + 'GEM' at the end (not a member
of CORDEX)
- cordex_ba: 'ba' for baseline. A numpy array with the climatological data. Its dimensions are [len(qus), len(oases), len(years), len(months), len(models)]. Let's say you want the dew point temperature from 'NOAA-GFDL-GFDL-ESM2M' for Skoura in Nov 1992. It would be cordex_ba[5, 3, 2, 10, 8].  5 is the index number of dew point, 3 is the index number of Skoura, 2 is the index number of 1992, 10 is the index number of Nov, 8 is the index number of the NOAA model.
- cordex_85: The same as cordex_ba, but the years are now the 30 years starting from 2071 for the rcp85 scenario
- cordex_26 : Same as cordex_85, but for rcp2.6. It has a lot of np.nan because we only have 3 cordex models running the rcp2.6 scenario
'''

path_save = "/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Figure/FigS3.png"
path_data = '/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Oasis_paper/data2.pkl'

if not os.path.exists(path_data):
  path_save = "FigS3.png"
  path_data = 'data/data2.pkl'


with open(path_data, 'rb') as f:
  qus, oases, years, months, models, cordex_ba, cordex_85, cordex_26 = pickle.load(f)

# remove GEM data index from axes=4 (i.e. models axes)
idx_gem = models.index("GEM")
cordex_ba = np.delete(cordex_ba, idx_gem, axis=4)
cordex_85 = np.delete(cordex_85, idx_gem, axis=4)
cordex_26 = np.delete(cordex_26, idx_gem, axis=4)

# averaging months to obtain cordex_*[qus, oases, years, models]
cordex_ba = np.mean(cordex_ba, axis=3)
cordex_26 = np.mean(cordex_26, axis=3)
cordex_85 = np.mean(cordex_85, axis=3)

# do log of data if necessary
do_log = False
if do_log:
  cordex_ba = np.log10(cordex_ba+1e-5)
  cordex_26 = np.log10(cordex_26+1e-5)
  cordex_85 = np.log10(cordex_85+1e-5)

print(cordex_ba.shape, cordex_26.shape)


def bootstrap(cordex, what, rcp_label, axs, idx, jdx, nboot=int(1e5)):

  # select ax to plot in
  ax = axs[idx, jdx]

  # first column has ylabels, otherwise no tick labels
  if jdx == 0:
    if what == "precipitation":
      ylabel = "Precipitation (mm/yr)"
      pad = 0
    if what == "temperature":
      ylabel = "Temperature (°C)"
      pad = 10
    ax.set_ylabel(ylabel, labelpad=pad)
  else:
    ax.yaxis.set_ticklabels([])

  # top row has titles
  if idx == 0:
    ax.set_title(rcp_label)

  # init arrays to store data during the bootstrap
  diff_boot = np.zeros((len(oases), nboot))
  diff = np.zeros(len(oases))

  print("bootstrapping %s temperatures with %d models..." % (rcp_label, nboot))
  # loop on oases to bootstrap
  for j, o in enumerate(tqdm(oases)):

    # oases and quantity index
    #idx_qus = qus.index("precipitation")
    idx_qus = qus.index(what)
    idx_oases = oases.index(o)

    # slice the data for the given quantity and oases, obtain data_*[years, models]
    data_ba = cordex_ba[idx_qus, idx_oases, ...]
    data_cdx = cordex[idx_qus, idx_oases, ...]

    # average baseline, obtain [models]
    data_ba_averaged = data_ba.mean(axis=0)

    # flatten the data
    data_ba_flat = data_ba.flatten()
    data_cdx_flat = data_cdx.flatten()

    data_ba_flat = data_ba_flat[~np.isnan(data_cdx_flat)]
    data_cdx_flat = data_cdx_flat[~np.isnan(data_cdx_flat)]

    # compute the difference of the averages for our data
    diff[j] = np.mean(data_cdx_flat) - np.mean(data_ba_flat)

    # number of data for later use
    ndata = len(data_ba_flat)

    # concatenate baseline and models
    data = np.concatenate((data_ba_flat, data_cdx_flat))

    # loop to shuffle the data
    for i in range(nboot):
      np.random.shuffle(data)

      # divide the shuffled data into baseline and models
      data_ba_flat_boot = data[:ndata]
      data_cdx_flat_boot = data[ndata:]

      # compute the difference between model and baseline
      diff_boot[j, i] = np.mean(data_cdx_flat_boot) - np.mean(data_ba_flat_boot)


  # compute averages and std, obtain array [oases]
  mean = diff_boot.mean(axis=1)
  std = diff_boot.std(axis=1)

  # number of oeases for later use
  noases = len(oases)

  # loop on sigmas
  for i in range(1, 4):
    # loop on oases to draw rectangles
    for j in range(noases):
      hx = Rectangle((j - 0.3, mean[j] - i*std[j]), 0.6, 2*i*std[j], alpha=0.2)
      ax.add_patch(hx)

  # loop on oases to plot means
  for j in range(noases):
    ax.plot([j-0.3, j+0.3], [mean[j], mean[j]], color="tab:blue")

  # plot the difference for the original data to compare with distributions
  ax.scatter(np.arange(noases), diff, color="tab:orange", zorder=999, marker="o")

  print("**********")
  print(rcp_label, what)
  result = {"oases": dict(), "model": rcp_label, "what": what}
  for j in range(noases):
    is_within_2sigma = mean[j] - 2*std[j] <= diff[j] <=  mean[j] + 2*std[j]
    print(oases[j].ljust(30), not is_within_2sigma)
    result["oases"][oases[j]] = not is_within_2sigma

  # shorten some names
  oases_name = []
  for o in oases:
    if "Ghizlane" in o:
      o = "M'hamid E."
    if "Archei" in o:
      o = "Guelta d'A."
    oases_name.append(o)

  # major locator at oases position, and replace with names
  ax.xaxis.set_major_locator(FixedLocator(range(noases)))
  ax.set_xticklabels(oases_name)

  # minor tick frequency
  ax.yaxis.set_minor_locator(MultipleLocator(1))

  # set y axis limits depending on the plot type
  if what == "precipitation":
    ax.set_ylim(-3, 3)
  if what == "temperature":
    ax.set_ylim(-1, 5)

  # rotate x labels to have more room
  plt.setp(ax.get_xticklabels(), rotation=40, ha='right', rotation_mode="anchor")

  return result

# create figure
fig, axs = plt.subplots(2, 2, sharex=True, figsize=(9, 6))

# panels

results = [bootstrap(cordex_26, "temperature", "RCP2.6", axs, 0, 0),
           bootstrap(cordex_85, "temperature", "RCP8.5", axs, 0, 1),
           bootstrap(cordex_26, "precipitation", "RCP2.6",axs, 1, 0),
           bootstrap(cordex_85, "precipitation", "RCP8.5", axs, 1, 1)]

np.save("bootstrap_results.npy", results)

plt.tight_layout()
plt.subplots_adjust(hspace=0, wspace=0)
plt.savefig(path_save, dpi=500)

print("Figure saved as " + path_save)

