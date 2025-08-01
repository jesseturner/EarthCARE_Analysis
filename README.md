# EarthCARE_Analysis
(currently only set up for the AC__TC__2B product)

EarthCARE data: https://ec-pdgs-dissemination2.eo.esa.int/oads/access/collection/EarthCAREL2Validated/tree

Install using: `pip install git+https://github.com/jesseturner/EarthCARE_Analysis/`

#--- Update this with a functional programming version
Example usage: 
```
from earthcare_plot import EarthCarePlot

ec = EarthCarePlot("ECA_EXAD_AC__TC__2B_20250708T030802Z_20250708T043331Z_06304F.h5")

ec.info()

ec.plot()

ec.plot_groundtrack()
```
