from earthcare_utils import earthcare_utils_functional as ec_utils

#ec_utils.explore_earthcare_file("data/ECA_EXBA_AC__TC__2B_20250731T235647Z_20250801T022318Z_06676A.h5")

ds = ec_utils.open_earthcare_file("data/ECA_EXBA_AC__TC__2B_20250723T235458Z_20250724T020508Z_06551E.h5")


ds = ec_utils.plot(ds)