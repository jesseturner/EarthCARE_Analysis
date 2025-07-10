import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs, cartopy.feature as cfeature
from datetime import datetime

#=====================================================

def main():

    filepath, date = setVariables()
    latitudes, longitudes, times = readTrackData(filepath)
    plotFigure(date, latitudes, longitudes, times)

    return

#=====================================================

def setVariables():

    date = '20250612' # YYYYMMDD
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

def plotFigure(date, latitudes, longitudes, times):

    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

    ax.plot(longitudes, latitudes, color='red', marker='o', linewidth=1, transform=ccrs.PlateCarree())

    extent = [-80, -25, 30, 60]
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Annotate each point with time (HH:MM), within the visible extent
    for lon, lat, t in zip(longitudes, latitudes, times):
        if extent[0] <= lon <= extent[1] and extent[2] <= lat <= extent[3]:
            time_label = t.strftime('%H:%M')
            ax.text(lon + 0.5, lat, time_label, fontsize=8, transform=ccrs.PlateCarree())


    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.gridlines(draw_labels=True)

    ax.set_title(f"Satellite Ground Track ({date})")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    fig.tight_layout()

    output_dir = "ground_track_image/"
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(f"{output_dir}earthcare_{date}", dpi=200, bbox_inches='tight')

    return

#-----------------------------------------------------

#=====================================================

if __name__ == '__main__':
    main()