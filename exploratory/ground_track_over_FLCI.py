import matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from datetime import datetime
import xarray as xr
import os, glob, sys
import numpy as np

#=====================================================

def main():

    filepath, date = setVariables()
    latitudes, longitudes, times = readTrackData(filepath)
    BTD = openFLCI(date)
    plotFigure(date, latitudes, longitudes, times, BTD)

    return

#=====================================================

def setVariables():

    date = '20250625' # YYYYMMDD
    filepath = f'ground_track_data/earthcare_{date}.txt'

    return filepath, date

#-----------------------------------------------------

def readTrackData(filepath):

    latitudes = []
    longitudes = []
    times = []

    with open(filepath, 'r') as file:
        for line in file:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                # Parse date + time
                timestamp_str = parts[0] + ' ' + parts[1]
                timestamp = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                times.append(timestamp)

                # Parse coordinates
                latitudes.append(float(parts[2]))
                longitudes.append(float(parts[3]))

    return latitudes, longitudes, times

#-----------------------------------------------------

def openFLCI(date):

    flci_directory = "./data_FLCI"

    search_pattern = f"{flci_directory}/*{date}.nc"
    matching_files = glob.glob(search_pattern)

    if matching_files:
        file_to_open = matching_files[0]
        ds = xr.open_dataset(file_to_open)
        BTD = ds["BTD"]
    else: 
        print(f'No file containing {date} found.')
        sys.exit(1)

    return BTD

#-----------------------------------------------------

def plotFigure(date, latitudes, longitudes, times, BTD):

    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

    extent = [-80, -25, 30, 61]
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Plot FLCI
    from matplotlib.colors import LinearSegmentedColormap
    colors = [(0, '#A9A9A9'), (0.5, 'white'), (1, '#1167b1')]  # +3 = blueish teal, 0 = white, -3 = grey
    cmap = LinearSegmentedColormap.from_list('custom_cmap', colors)
    levels = np.linspace(-3, 3, 31)
    c=ax.contourf(BTD.longitude, BTD.latitude, BTD, cmap=cmap, extend='both', levels=levels)
    clb = plt.colorbar(c, shrink=0.3, pad=0.05, ax=ax)
    clb.ax.tick_params(labelsize=15)
    clb.set_label('(K)', fontsize=15)

    plotEarthCAREtrack(longitudes, latitudes, times, ax, extent)

    # Map features
    ax.add_feature(cfeature.LAND, edgecolor='#000', facecolor='tan', zorder=1)
    ax.gridlines(draw_labels=True, zorder=2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=3)
    ax.coastlines(zorder=4)
    
    # Figure features
    ax.set_title(f"Simulated BTD (11.2 μm - 3.9 μm) \n(GFS + OISST, {date})", fontsize=15, pad=10)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    fig.tight_layout()
    fig.set_dpi(200)
    ax.legend()

    output_dir = "ground_track_image/"
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(f"{output_dir}earthcare_flci_{date}", dpi=200, bbox_inches='tight')

    return

#-----------------------------------------------------

def plotEarthCAREtrack(longitudes, latitudes, times, ax, extent):
    # Highlighting the pass over the FLC
    highlight_lons = []
    highlight_lats = []
    highlight_times = []
    background_lons = []
    background_lats = []

    for lon, lat, t in zip(longitudes, latitudes, times):
        if t.strftime('%H:%M') >= '05:57' and t.strftime('%H:%M') <= '05:59':
            highlight_lons.append(lon)
            highlight_lats.append(lat)
            highlight_times.append(t)  # ✅ Track times for red points
        else:
            background_lons.append(lon)
            background_lats.append(lat)

    # Plot background (grey, no label)
    ax.plot(background_lons, background_lats, color='grey', linewidth=2, transform=ccrs.PlateCarree(), zorder=5)

    # Plot highlighted section (red, with label)
    ax.plot(highlight_lons, highlight_lats, color='red', marker='o', linewidth=3, transform=ccrs.PlateCarree(),
            label='EarthCARE', zorder=6)

    # Annotate only the highlighted (red) section with correct timestamps
    for lon, lat, t in zip(highlight_lons, highlight_lats, highlight_times):
        time_label = t.strftime('%H:%M')
        if extent[0] <= lon <= extent[1] and extent[2] <= lat <= extent[3]:
            ax.text(lon + 0.5, lat, time_label, fontsize=10, color='black', weight='bold',
                    transform=ccrs.PlateCarree(), zorder=7)
            
#-----------------------------------------------------

#=====================================================

if __name__ == '__main__':
    main()