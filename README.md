# EarthCARE_Analysis
(currently only set up for the AC__TC__2B product)

EarthCARE data: https://ec-pdgs-dissemination2.eo.esa.int/oads/access/collection/EarthCAREL2Validated/tree

Example usage: 
```
from earthcare_plot import EarthCarePlot

ec = EarthCarePlot("ECA_EXAD_AC__TC__2B_20250708T030802Z_20250708T043331Z_06304F.h5")

print(ec.info())

ec.plot()

ec.plot_groundtrack()
```
