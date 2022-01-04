import os

plots = ["FigS3.py", "Fig2.py", "Fig3.py", "FigS1.py", "FigS2.py"]

for plot in plots:
  print("Running " + plot)
  os.system("python3 " + plot)
