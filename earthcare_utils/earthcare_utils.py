import h5py, os, datetime, re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates
import cartopy.crs as ccrs, cartopy.feature as cfeature
import xarray as xr

def _print_info(name, obj):
    obj_type = 'Group' if isinstance(obj, h5py.Group) else 'Dataset'
    print(f"\n{name} ({obj_type})")

    for key, val in obj.attrs.items():
        print(f"  Attr: {key} = {val}")

    if isinstance(obj, h5py.Dataset):
        print(f"  Shape: {obj.shape}")
        print(f"  Dtype: {obj.dtype}")

def explore_earthcare_file(file_path):
    with h5py.File(file_path, 'r') as f:
        print("=== File-level Attributes ===")
        for key, val in f.attrs.items():
            print(f"  {key} = {val}")

        print("\n=== Structure and Metadata ===")
        f.visititems(_print_info)
    
    return
    
def open_earthcare_file(file_path):

    data_type = _get_data_type(file_path)
    
    with h5py.File(file_path, 'r') as f:
        class_data = np.array(f['ScienceData/synergetic_target_classification'][()])
        pixel_height_data = np.array(f['ScienceData/height'][()])
        time_data = np.array(f['ScienceData/time'][()])
        latitude = np.array(f['ScienceData/latitude'][()])
        longitude = np.array(f['ScienceData/longitude'][()])

    height_data = np.arange(np.shape(class_data)[1])

    ds = xr.Dataset(
        data_vars={
            'latitude': (['time'], latitude),
            'longitude': (['time'], longitude),
            'pixel_height': (['time', 'height'], pixel_height_data/1000), # converting from m to km
            'classification': (['time', 'height'], class_data),
        },
        coords={
            'time': _set_time(time_data),
            'height': height_data
        },
        attrs={
            'data_type': data_type
        }
            )

    return ds

def _get_data_type(file_path):
    filename = os.path.basename(file_path)
    data_type = filename[9:19]

    return data_type
    
def _set_time(time_data):
    ref_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
    time_data_dt = np.array([ref_time + datetime.timedelta(seconds=sec) for sec in time_data])
    
    return time_data_dt

def plot(ds):

    fig, ax = plt.subplots(figsize=(9, 4))
    time_grid, height_grid = np.meshgrid(ds.time, ds.height, indexing='ij')
    cmap = _create_cmap()
    pcm = ax.pcolormesh(time_grid, ds.pixel_height, ds.classification, cmap=cmap, shading='auto')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    fig.autofmt_xdate()

    ax.set_title("")
    ax.set_xlabel("Time")
    ax.set_ylabel("Height (km)")
    ax.set_ylim(0,20)

    dt_formatted = _get_datetime_str(ds)

    output_dir = "plot_earthcare/"
    os.makedirs(output_dir, exist_ok=True)
    save_path = f"{output_dir}{ds.data_type}_{dt_formatted}"
    fig.savefig(save_path, dpi=200, bbox_inches='tight')
    print(f"Plot saved at {save_path}.")

    return ds

def _create_cmap():
    custom_colors = [
        '#c5c9c7', '#a2653e', '#ffffff', '#ff474c', '#0504aa', '#009337', '#840000',
        '#042e60', '#d8dcd6', '#ffff84', '#f5bf03', '#f97306', '#ff000d', '#5539cc',
        '#2976bb', '#0d75f8', '#014182', '#017b92', '#06b48b', '#aaff32', '#6dedfd',
        '#01f9c6', '#7bc8f6', '#d7fffe', '#a2cffe', '#04d9ff', '#7a9703', '#b2996e',
        '#ffbacd', '#d99b82', '#947e94', '#856798', '#ac86a8', '#59656d', '#76424e',
        '#363737'
    ]
    cmap = ListedColormap(custom_colors)
    
    return cmap

def _get_datetime_str(ds):
    dt_start = ds.time.values[0].astype('datetime64[ms]').astype('O')
    dt_end = ds.time.values[-1].astype('datetime64[ms]').astype('O')
    dt_formatted = f"d{dt_start:%Y%m%d}_t{dt_start:%H%M}_t{dt_end:%H%M}"
    return dt_formatted


def slice_time_section(ds, start_dt=None, end_dt=None):
    if not isinstance(start_dt, datetime.datetime):
        raise TypeError(f"start_dt must be a datetime, but got {type(start_dt).__name__}")
    if not isinstance(end_dt, datetime.datetime):
        raise TypeError(f"end_dt must be a datetime, but got {type(end_dt).__name__}")
    if not (start_dt < end_dt):
        raise ValueError(f"start_dt must be before end_dt")
                         
    ds_filtered = ds.sel(time = ((ds.time >= np.datetime64(start_dt)) & (ds.time <= np.datetime64(end_dt))))

    return ds_filtered

def plot_groundtrack(ds):
        step_size = 150
        abbr_lon = ds.longitude[::step_size]
        abbr_lat = ds.latitude[::step_size]
        time = ds.time.values.astype('datetime64[ms]').astype('O') # convert to datetime
        abbr_time = time[::step_size]
        
        projection=ccrs.PlateCarree(central_longitude=0)
        fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

        ax.plot(abbr_lon, abbr_lat, color='red', marker='o', linewidth=1, transform=ccrs.PlateCarree())

        for lon, lat, t in zip(abbr_lon, abbr_lat, abbr_time):
            time_label = t.strftime('%H:%M')
            ax.text(lon + 0.5, lat, time_label, fontsize=8, transform=ccrs.PlateCarree())

        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        ax.gridlines(draw_labels=True)

        min_lon, max_lon, min_lat, max_lat = _set_ground_track_plot_limits(ds)
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True)
        fig.tight_layout()

        output_dir = "plot_earthcare/"
        os.makedirs(output_dir, exist_ok=True)
        dt_formatted = _get_datetime_str(ds)
        save_path = f"{output_dir}ground_track_{dt_formatted}"
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
        print(f"Plot saved at {save_path}.")

        return ds

def _set_ground_track_plot_limits(ds):
    lat_first = ds.latitude.values[0]
    lat_last = ds.latitude.values[-1]
    min_lat = min(lat_first, lat_last)
    max_lat = max(lat_first, lat_last)
    lat_diff = max_lat - min_lat
    buffer_value = 30
    if lat_diff < buffer_value:
        min_lat = min_lat - (buffer_value - lat_diff)/2
        max_lat = max_lat + (buffer_value - lat_diff)/2

    lon_first = ds.longitude.values[0]
    lon_last = ds.longitude.values[-1]
    min_lon = min(lon_first, lon_last)
    max_lon = max(lon_first, lon_last)
    lon_diff = max_lon - min_lon
    buffer_value = 30
    if lon_diff < buffer_value:
        min_lon = min_lon - (buffer_value - lon_diff)/2
        max_lon = max_lon + (buffer_value - lon_diff)/2

    return min_lon, max_lon, min_lat, max_lat

