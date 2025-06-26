import glob, sys, os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

#=====================================================

def main():

    date, class_data, height_data, time_data = getData()
    height_data, time_data = convertData(height_data, time_data)
    time_grid = createGrid(height_data, time_data)
    plotData(time_grid, height_data, class_data, date)

    return

#=====================================================

def getData():

    date = '20250625' # YYYYMMDD
    data_directory = f'data_ATL_TC_2A/'

    search_pattern = f"{data_directory}/*{date}*"
    matching_files = glob.glob(search_pattern)

    if matching_files:
        file_to_open = matching_files[0]
        class_data, height_data, time_data = openFile(file_to_open)
    else: 
        print(f'No file containing {date} found.')
        sys.exit(1)

    return date, class_data, height_data, time_data

#-----------------------------------------------------

def openFile(filepath): 
    with h5py.File(filepath, 'r') as f:
        dataset1_path = 'ScienceData/classification'
        class_data = np.array(f[dataset1_path][()])

        dataset2_path = 'ScienceData/height'
        height_data = np.array(f[dataset2_path][()])

        time_path = 'ScienceData/time'
        time_data = np.array(f[time_path][()])

    return class_data, height_data, time_data

#-----------------------------------------------------

def convertData(height_data, time_data):
    
    height_data_km = height_data/1000 # convert to km

    ref_time = datetime(2000, 1, 1, 0, 0, 0)
    time_data_dt = [ref_time + timedelta(seconds=sec) for sec in time_data]

    return height_data_km, time_data_dt

#-----------------------------------------------------

def createGrid(height_data, time_data): 
    time_grid, height_grid = np.meshgrid(time_data, np.arange(height_data.shape[1]), indexing='ij')

    return time_grid

#-----------------------------------------------------

def plotData(time_grid, height_data, class_data, date):

    plt.figure()
    fig, ax = plt.subplots(figsize=(9, 4))

    cmap, norm, tick_values, tick_labels = setColormap()
    mesh = ax.pcolormesh(time_grid, height_data, class_data, cmap=cmap, norm=norm, shading='auto')

    # Colorbar
    cbar = plt.colorbar(mesh, ax=ax, ticks=tick_values)
    cbar.ax.set_yticklabels(tick_labels)

    # Format axes
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    ax.set_ylim(0, 30)

    ax.set_title(f"EarthCARE Lidar Type Classification ({date})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Height (km)")

    output_dir = "earthcare_atl_tc_image/"
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(f"{output_dir}atl_tc_{date}", dpi=200, bbox_inches='tight')

#-----------------------------------------------------

def setColormap():

    class_labels = {
    -3: 'Missing Data',
    -2: 'Surface',
    -1: 'Noise',
     0: 'Clear',
     1: 'Liquid Cloud (Warm)',
     2: 'Liquid Cloud (Supercooled)',
     3: 'Ice Cloud',
    10: 'Dust',
    11: 'Sea Salt',
    12: 'Pollution',
    13: 'Smoke',
    14: 'Dusty Smoke',
    15: 'Dusty Mix',
    20: 'STS (supercooled ternary solution)',
    21: 'NAT (nitric acid trihydrate)',
    22: 'Strat. Ice',
    25: 'Strat. Ash',
    26: 'Strat. Sulfate',
    27: 'Strat. Smoke',
    }

    class_values = list(class_labels.keys())

    colors = [
        '#808080',  # -3 Missing Data
        '#4B3621',  # -2 Surface
        '#A9A9A9',  # -1 Noise
        '#FFFFFF',  #  0 Clear
        '#ADD8E6',  #  1 Warm Liquid
        '#75bbfd',  #  2 Supercooled Liquid
        "#80f5fd",  #  3 Ice Cloud
        "#e3b79c",  # 10 Dust
        "#C1F710",  # 11 Sea Salt
        "#bf9ec6",  # 12 Pollution
        "#AF2222",  # 13 Smoke
        "#d5bd97",  # 14 Dusty Smoke
        "#bab3ba",  # 15 Dusty Mix
        "#8aeebc",  # 20 STS
        "#A1FC93",  # 21 NAT
        "#3dc613",  # 22 Strat. Ice
        "#d6adad",  # 25 Strat. Ash
        "#f8f896",  # 26 Strat. Sulfate
        "#E12D2D",  # 27 Strat. Smoke
    ]

    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(class_values, ncolors=len(colors))

    tick_values = list(class_labels.keys())
    tick_labels = list(class_labels.values())

    return cmap, norm, tick_values, tick_labels

#=====================================================

if __name__ == '__main__':
    main()