from earthcare_plot import EarthCarePlot

def test_plot():
    ec = EarthCarePlot("ECA_EXAD_AC__TC__2B_20250708T030802Z_20250708T043331Z_06304F.h5")
    print(ec.info())
    #assert add(2, 3) == 5