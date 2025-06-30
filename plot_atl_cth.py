import glob, sys, os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, time
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

#=====================================================

def main():

    date = '20250625' # YYYYMMDD
    start_time = time(5, 57, 00) # HH:mm:ss
    end_time = time(5, 59, 0)

    height_data, time_data = getData(date)
    height_data, time_data = convertData(height_data, time_data)
    time_data, height_data = filterData(time_data, height_data, start_time, end_time)
    plotData(time_data, height_data, date)

    return

#=====================================================

def getData(date):

    data_directory = f'data_ATL_CTH_2A/'

    search_pattern = f"{data_directory}/*{date}*"
    matching_files = glob.glob(search_pattern)

    if matching_files:
        file_to_open = matching_files[0]
        height_data, time_data = openFile(file_to_open)
    else: 
        print(f'No file containing {date} found.')
        sys.exit(1)

    return height_data, time_data

#-----------------------------------------------------

def openFile(filepath): 
    with h5py.File(filepath, 'r') as f:
        dataset_path = 'ScienceData/ATLID_cloud_top_height'
        height_data = np.array(f[dataset_path][()])

        time_path = 'ScienceData/time'
        time_data = np.array(f[time_path][()])

    return height_data, time_data

#-----------------------------------------------------

def convertData(height_data, time_data):
    
    height_data_km = height_data/1000 # convert to km

    ref_time = datetime(2000, 1, 1, 0, 0, 0)
    time_data_dt = [ref_time + timedelta(seconds=sec) for sec in time_data]

    return height_data_km, time_data_dt

#-----------------------------------------------------

def filterData(time_data, height_data, start_time, end_time):

    mask = np.array([start_time <= dt.time() <= end_time for dt in time_data])
    time_data_filtered = np.array(time_data)[mask]
    height_data_filtered = np.array(height_data)[mask]

    return time_data_filtered, height_data_filtered

#-----------------------------------------------------

def plotData(time_data, height_data, date):

    plt.figure()
    fig, ax = plt.subplots(figsize=(9, 4))

    ax.scatter(time_data, height_data, c='#87CEEB', marker='x', s=10)

    # Format axes
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()
    ax.set_ylim(0, 30)

    ax.set_title(f"EarthCARE Lidar Cloud Top Height ({date})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Height (km)")

    output_dir = "earthcare_atl_cth_image/"
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(f"{output_dir}atl_tc_{date}", dpi=200, bbox_inches='tight')

#-----------------------------------------------------

#=====================================================

if __name__ == '__main__':
    main()