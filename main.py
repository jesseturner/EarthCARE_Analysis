from earthcare_utils import earthcare_utils as ec_utils
from datetime import datetime

#ec_utils.explore_earthcare_file("data/ECA_EXBA_AC__TC__2B_20250731T235647Z_20250801T022318Z_06676A.h5")

ds = ec_utils.open_earthcare_file("data/ECA_EXBA_AC__TC__2B_20250731T235647Z_20250801T022318Z_06676A.h5")

ds = ec_utils.slice_time_section(ds, start_dt=datetime(2025, 7, 31, 23, 0), end_dt=datetime(2025, 8, 1, 0, 0))

ds = ec_utils.plot(ds)

ds = ec_utils.plot_groundtrack(ds)