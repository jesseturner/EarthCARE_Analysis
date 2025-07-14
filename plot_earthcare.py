import h5py, os, datetime, re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.dates as mdates
import cartopy.crs as ccrs, cartopy.feature as cfeature

class EarthCarePlot:
    
    def __init__(self, file_path):
        
        filename = os.path.basename(file_path)

        if "AC__TC__2B" in filename: 
            self.product_type = "AC__TC__2B"
            self.start_dt = self._get_dates(filename)

            with h5py.File(file_path, 'r') as f:
                self.class_data = np.array(f['ScienceData/synergetic_target_classification'][()])
                self.height_data = np.array(f['ScienceData/height'][()])
                self.time_data = np.array(f['ScienceData/time'][()])
                self.latitude = np.array(f['ScienceData/latitude'][()])
                self.longitude = np.array(f['ScienceData/longitude'][()])

        else: 
            print("EarthCARE file type not added yet.")

    
    def _get_dates(self, filename):
        pattern = r"_(\d{8}T\d{6})Z_(\d{8}T\d{6})Z_"

        match = re.search(pattern, filename)
        if match:
            start_str = match.group(1)  # '20250525T234738'
            start_dt = datetime.datetime.strptime(start_str, "%Y%m%dT%H%M%S")
        
        return start_dt

    
    def plot(self, start_dt=None, end_dt=None):

        filtered_time, filtered_data, filtered_height = self._filter_data(start_dt, end_dt)

        time_grid, height_grid = np.meshgrid(filtered_time, np.arange(filtered_height.shape[1]), indexing='ij')

        custom_colors = [
            '#c5c9c7', '#a2653e', '#ffffff', '#ff474c', '#0504aa', '#009337', '#840000',
            '#042e60', '#d8dcd6', '#ffff84', '#f5bf03', '#f97306', '#ff000d', '#5539cc',
            '#2976bb', '#0d75f8', '#014182', '#017b92', '#06b48b', '#aaff32', '#6dedfd',
            '#01f9c6', '#7bc8f6', '#d7fffe', '#a2cffe', '#04d9ff', '#7a9703', '#b2996e',
            '#ffbacd', '#d99b82', '#947e94', '#856798', '#ac86a8', '#59656d', '#76424e',
            '#363737'
        ]

        plt.figure()
        fig, ax = plt.subplots(figsize=(9, 4))

        cmap = ListedColormap(custom_colors)

        pcm = ax.pcolormesh(time_grid, filtered_height, filtered_data, cmap=cmap, shading='auto')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        fig.autofmt_xdate()

        ax.set_title("")
        ax.set_xlabel("Time")
        ax.set_ylabel("Height (km)")

        output_dir = "plot_earthcare/"
        os.makedirs(output_dir, exist_ok=True)
        fig.savefig(f"{output_dir}{self.product_type}_{datetime.datetime.strftime(self.start_dt, '%Y%m%d%H%M')}", dpi=200, bbox_inches='tight')


    def _filter_data(self, start_dt=None, end_dt=None):
        if start_dt and end_dt:
                self.start_dt, self.end_date = start_dt, end_dt
        else:
            print("Using full {self.product_type} swath.")
        
        height_km = self.height_data/1000 # convert to km
        time = self._set_time()

        if start_dt is not None and end_dt is not None:
            time_mask = (time >= start_dt) & (time <= end_dt)

            filtered_time = time[time_mask]
            filtered_data = self.class_data[time_mask, :]
            filtered_height = height_km[time_mask, :]

        return filtered_time, filtered_data, filtered_height
    
    def _set_time(self):
        ref_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
        time = np.array([ref_time + datetime.timedelta(seconds=sec) for sec in self.time_data])
        return time
    
    def plot_groundtrack(self):

        time = self._set_time()
        step_size = 150
        abbr_lon = self.longitude[::step_size]
        abbr_lat = self.latitude[::step_size]
        abbr_time = time[::step_size]
        
        projection=ccrs.PlateCarree(central_longitude=0)
        fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

        ax.plot(abbr_lon, abbr_lat, color='red', marker='o', linewidth=1, transform=ccrs.PlateCarree())

        #extent = [-80, -25, 30, 60]
        #ax.set_extent(extent, crs=ccrs.PlateCarree())

        # Annotate each point with time (HH:MM), within the visible extent
        for lon, lat, t in zip(abbr_lon, abbr_lat, abbr_time):
            #if extent[0] <= lon <= extent[1] and extent[2] <= lat <= extent[3]:
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
        fig.savefig(f"{output_dir}{self.product_type}_{datetime.datetime.strftime(self.start_dt, '%Y%m%d%H%M')}_ground_track", dpi=200, bbox_inches='tight')



ec = EarthCarePlot("data_AC__TC__2B/ECA_EXAD_AC__TC__2B_20250703T062938Z_20250704T000519Z_06229A.h5")
#ec.plot(datetime.datetime(2025, 7, 3, 6, 21), datetime.datetime(2025, 7, 3, 6, 24))
ec.plot_groundtrack()