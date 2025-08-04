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
        })

    return ds
    
def _set_time(time_data):
    ref_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
    time_data_dt = np.array([ref_time + datetime.timedelta(seconds=sec) for sec in time_data])
    
    return time_data_dt

def plot(ds):

    time_grid, height_grid = np.meshgrid(ds.time, ds.height, indexing='ij')

    custom_colors = [
        '#c5c9c7', '#a2653e', '#ffffff', '#ff474c', '#0504aa', '#009337', '#840000',
        '#042e60', '#d8dcd6', '#ffff84', '#f5bf03', '#f97306', '#ff000d', '#5539cc',
        '#2976bb', '#0d75f8', '#014182', '#017b92', '#06b48b', '#aaff32', '#6dedfd',
        '#01f9c6', '#7bc8f6', '#d7fffe', '#a2cffe', '#04d9ff', '#7a9703', '#b2996e',
        '#ffbacd', '#d99b82', '#947e94', '#856798', '#ac86a8', '#59656d', '#76424e',
        '#363737'
    ]

    fig, ax = plt.subplots(figsize=(9, 4))

    cmap = ListedColormap(custom_colors)

    pcm = ax.pcolormesh(time_grid, ds.pixel_height, ds.classification, cmap=cmap, shading='auto')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    fig.autofmt_xdate()

    ax.set_title("")
    ax.set_xlabel("Time")
    ax.set_ylabel("Height (km)")
    ax.set_ylim(0,20)

    
    dt = ds.time.values[0].astype('datetime64[ms]').astype('O')
    dt_formatted = f"d{dt:%Y%m%d}_t{dt:%H%M}"


    output_dir = "plot_earthcare/"
    os.makedirs(output_dir, exist_ok=True)
    save_path = f"{output_dir}AC__TC__2B_{dt_formatted}"
    fig.savefig(save_path, dpi=200, bbox_inches='tight')
    print(f"Plot saved at {save_path}.")

    return ds

#--------------------- OLD FUNCTIONS



def _filter_data(self, start_dt=None, end_dt=None):
    if start_dt and end_dt:
            self.start_dt, self.end_date = start_dt, end_dt
    else:
        print(f"Using full {self.product_type} swath.")
    
    height_km = self.height_data/1000 # convert to km
    time = self._set_time()

    if start_dt is not None and end_dt is not None:
        time_mask = (time >= start_dt) & (time <= end_dt)
        filtered_time = time[time_mask]
        filtered_data = self.class_data[time_mask, :]
        filtered_height = height_km[time_mask, :]

    else: 
        filtered_time = time
        filtered_data = self.class_data
        filtered_height = height_km

    return filtered_time, filtered_data, filtered_height
    

    
    def plot_groundtrack(self):

        time = self._set_time()
        step_size = 150
        abbr_lon = self.longitude[::step_size]
        abbr_lat = self.latitude[::step_size]
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

        ax.set_title(f"Satellite Ground Track ({datetime.datetime.strftime(self.start_dt, '%Y-%m-%d')})")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True)
        fig.tight_layout()

        output_dir = "plot_earthcare/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = f"{output_dir}{self.product_type}_{datetime.datetime.strftime(self.start_dt, '%Y%m%d%H%M')}_ground_track"
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
        print(f"Plot saved at {save_path}.")
