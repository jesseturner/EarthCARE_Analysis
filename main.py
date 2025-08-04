from earthcare_utils import earthcare_utils_functional as ec_utils
from datetime import datetime

#ec_utils.explore_earthcare_file("data/ECA_EXBA_AC__TC__2B_20250731T235647Z_20250801T022318Z_06676A.h5")

ds = ec_utils.open_earthcare_file("data/ECA_EXAD_AC__TC__2B_20250627T194648Z_20250627T231800Z_06144C.h5")

#ds = ec_utils.slice_time_section(ds, start_dt=datetime(2025, 8, 1, 0, 4), end_dt=datetime(2025, 8, 1, 0, 6))

#ds = ec_utils.plot(ds)

ds = ec_utils.plot_groundtrack(ds)