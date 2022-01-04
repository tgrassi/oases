import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pickle
import seaborn as sns
import pandas as pd
import os
import sys
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
#from test_word_table import do_table


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


path_data = '/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Oasis_paper/data2.pkl'
path_save = "/Users/Roberto/Desktop/Varie/Lavoro/Dottorato_Canada/PhD_Project/Figure/Fig3.png"

if not os.path.exists(path_data):
  path_data = 'data/data2.pkl'
  path_save = "Fig3.png"

path_bootstrap = "bootstrap_results.npy"

if not os.path.isfile(path_bootstrap):
  sys.exit("ERROR: bootstrap data are missing, run FigS3.py script first!")

data_bootstrap = np.load(path_bootstrap, allow_pickle=True)
print(data_bootstrap)

with open(path_data, 'rb') as f:
  qus, oases, years, months, models, cordex_ba, cordex_85, cordex_26 = pickle.load(f)


# get GEM data
idx_gem = models.index("GEM")
gem_ba = cordex_ba[..., idx_gem]
gem_85 = cordex_85[..., idx_gem]
gem_26 = cordex_26[..., idx_gem]

# remove GEM data
cordex_ba = np.delete(cordex_ba, idx_gem, axis=4)
cordex_85 = np.delete(cordex_85, idx_gem, axis=4)
cordex_26 = np.delete(cordex_26, idx_gem, axis=4)

# monthly and annual average of the baseline
cordex_ba = np.mean(cordex_ba, axis=3)
cordex_ba = np.mean(cordex_ba, axis=2)

# monthly and annual average of GEM
gem_ba = np.mean(gem_ba, axis=3)
gem_ba = np.mean(gem_ba, axis=2)

# remove baseline from data
def remove_ba(data, data_ba):
  data_xx = np.mean(data, axis=1)
  diff = (data_xx - data_ba.reshape(-1)).flatten()
  return diff


t_data = []
p_data = []
o_data = []
m_data = []
t_gem_data = []
p_gem_data = []
# loop on oases
for o in oases:
  idx_oases = oases.index(o)
  idx_o = o

  if "Ghizlane" in o:
    o = "M'hamid E."
  if "Archei" in o:
    o = "Guelta d'A."

  # TEMPERATURE DATA
  idx_qus = qus.index("temperature")

  # temperature: RCP 2.6
  diff = remove_ba(cordex_26[idx_qus, idx_oases, ...], cordex_ba[idx_qus, idx_oases, ...])
  t_data = np.append(t_data, diff)
  ndata = len(diff)

  # temperature: RCP 8.5
  diff = remove_ba(cordex_85[idx_qus, idx_oases, ...], cordex_ba[idx_qus, idx_oases, ...])
  t_data = np.append(t_data, diff)

  # temperature: GEM
  diff = remove_ba(gem_85[idx_qus, idx_oases, ...], gem_ba[idx_qus, idx_oases, ...])
  t_gem_data.append(np.mean(diff))


  # PRECIPITATIONs DATA
  idx_qus = qus.index("precipitation")

  # precipitation: RCP 2.6
  diff = remove_ba(cordex_26[idx_qus, idx_oases, ...], cordex_ba[idx_qus, idx_oases, ...])
  p_data = np.append(p_data, diff*12)

  # precipitation: RCP 8.5
  diff = remove_ba(cordex_85[idx_qus, idx_oases, ...], cordex_ba[idx_qus, idx_oases, ...])
  p_data = np.append(p_data, diff*12)

  # precipitation: GEM
  diff = remove_ba(gem_85[idx_qus, idx_oases, ...], gem_ba[idx_qus, idx_oases, ...])
  p_gem_data.append(np.mean(diff*12))


  # store model name in model column (for pandas)
  m_data += ["RCP2.6"]*ndata + ["RCP8.5"]*ndata

  # store oases name in oases column (for pandas)
  o_data += [idx_o]*(ndata*2)


# prepare pandas dataframe
data = pd.DataFrame(data={"oases": o_data, "Model": m_data, "temperature": t_data, "precipitation": p_data})

# *************************
# QUARTILES, MEAN, MEDIAN TABLES
def print_table(model, qty):
  print("***********")
  print(model, qty)
  print("%30s %17s %17s %17s %17s" % ("", "q25", "q75", "mean", "median"))

  tab_label = qty.title() + " " + model
  dtab = [[tab_label, "Q25", "Q75", "Mean", "Median"]]
  for o in oases:
    data_o = data.loc[(data['oases'] == o) & (data['Model'] == model)]
    q25 = data_o.quantile(q=0.25)
    q75 = data_o.quantile(q=0.75)
    qmean = data_o.mean()
    qmedian = data_o.median()
    row = [o, q25[qty], q75[qty], qmean[qty], qmedian[qty]]
    row[1:] = ["%.2f" % x for x in row[1:]]
    print(row)
    dtab.append(row)
  print("\n\n")
  return dtab

data_table = [print_table("RCP2.6", "temperature"),
              print_table("RCP8.5", "temperature"),
              print_table("RCP2.6", "precipitation"),
              print_table("RCP8.5", "precipitation")]

#do_table(data_table, "table_fig3.docx")

# ******************+
# FIGURES
# figure
fig = plt.figure(figsize=(10, 8))


# function to define the style of the quartile lines
def set_quartile_style(data_bstrap, what, models, oases):
  seq = []
  # loop on oases names to search for bootstrap data
  for o in oases:
    # loop models
    for m in models:
      for b in data_bstrap:
        # find given model and quantity
        if m in b["model"] and b["what"] == what:
          # store boolean if model is outside 3 sigma
          seq.append(b["oases"][o])

  # quartiles lines
  for l in ax.lines:
      l.set_linestyle(':')
      l.set_linewidth(1.1)
      l.set_color('k')
      l.set_alpha(0.6)
      l.set_solid_capstyle("butt")
      l.set_solid_joinstyle("miter")

  # mean lines
  lcount = 0
  for l in ax.lines[1::3]:
      l.set_linestyle('-')
      l.set_color('k')
      # change style according to bootstrap results
      if seq[lcount]:
        l.set_linewidth(1.6)
        l.set_alpha(0.9)
      else:
        l.set_linewidth(0.8)
        l.set_color('white')
        l.set_alpha(0.9)
      lcount += 1

flatui = ["#3eacd4", "#ed5858"]
sns.set_palette(flatui)

# **************
# UPPER PANEL (temperature)
fig.add_subplot(211)
ax = sns.violinplot(x="oases", y="temperature", data=data, hue="Model", split=True, inner="quartile")
ax.legend_.remove()

ax.yaxis.set_minor_locator(MultipleLocator(1))

# add GEM models
plt.scatter(np.arange(len(t_gem_data))+.1, t_gem_data, marker="*", color="w", alpha=1., s=50)

# finalize upper panel style
set_quartile_style(data_bootstrap, "temperature", ["2.6", "8.5"], oases)
plt.xlabel("")
plt.ylabel("Temperature Change\nfrom 90-19 avg (°C)", labelpad=26)
plt.tick_params(labelright=False, right=True)
plt.gca().get_xaxis().set_visible(False)


# **************
# LOWER PANEL (precipitation zoom)
fig.add_subplot(212)

data_sub = data.loc[data['precipitation'] < 200]
ax = sns.violinplot(x="oases", y="precipitation", data=data_sub, hue="Model", split=True, inner="quartile")
ax.yaxis.set_minor_locator(MultipleLocator(50))
#ax = sns.catplot(x="oases", y="precipitation", data=data_sub, hue="Model")

# plt.ylim(-250, 200)

# add GEM MODELS
plt.scatter(np.arange(len(p_gem_data))+.1, p_gem_data, marker="*", color="w", alpha=1., s=50)


# finalize lower panel style
set_quartile_style(data_bootstrap, "precipitation", ["2.6", "8.5"], oases)
plt.xlabel("")
plt.ylabel("Precipitation Change\nfrom 90-19 avg (mm/yr)")
plt.xticks(rotation=30, ha="right")
plt.tick_params(labelright=False, right=True)
plt.legend(loc='lower left',fontsize=12)



# **************
# general figure style
plt.tight_layout()
plt.subplots_adjust(hspace=0e0)
plt.savefig(path_save, bbox_inches='tight', dpi=800)
print("Figure saved to " + path_save)

