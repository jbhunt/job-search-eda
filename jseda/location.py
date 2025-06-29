import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter   # polite 1 req/sec helper
import polars as pl
import numpy as np

class LocationFigure():
    """
    """

    def __init__(self, data):
        """
        """

        self.df = pl.read_csv(data)

        return
    
    def plot(self):
        """
        """

        proj = ccrs.AlbersEqualArea(central_longitude=-96, central_latitude=37.5)
        fig = plt.figure(figsize=(9, 6))
        ax  = plt.axes(projection=proj)
        # ax.set_extent([-125, -66.5, 23, 50], crs=ccrs.Geodetic())

        # Read Natural-Earth "countries" and keep only the U.S. geometry
        countries_shp = shpreader.natural_earth(
            resolution="50m",       # 10 m, 50 m, or 110 m
            category="cultural",
            name="admin_0_countries",
        )
        reader = shpreader.Reader(countries_shp)
        usa_geoms = [
            rec.geometry
            for rec in reader.records()
            if rec.attributes["ADM0_A3"] == "USA"   # ISO-3166-3 code for the U.S.
        ]

        # Add the U.S. polygon and state boundaries
        ax.add_geometries(
            usa_geoms,
            crs=ccrs.PlateCarree(),
            facecolor="none",
            edgecolor="black",
            linewidth=0.7,
        )

        #
        ax.set_xlim((-3067782.3585205222, 2919857.814802468))
        ax.set_ylim((-1611952.7046921505, 1889689.255009139))

        #
        geolocator = Nominatim(user_agent="us_city_locator")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        cmap = plt.get_cmap('tab10')
        colors = {
            industry: cmap(i) for i, industry in enumerate(list(self.df['Industry'].unique()))
        }
        for city, industry in zip(self.df['Location'], self.df['Industry']):
            if city == 'Remote':
                continue
            loc = geocode(f'{city}, USA')
            if industry == "None":
                color='k'
            else:
                color = colors[industry]
            print(city, industry)
            if loc is None:
                continue
            ax.plot(
                loc.longitude + np.random.normal(loc=0, scale=1, size=1).item(),
                loc.latitude + np.random.normal(loc=0, scale=1, size=1).item(),
                marker="o",
                markersize=5,
                markerfacecolor=colors[industry],
                markeredgecolor='none',
                alpha=0.3,
                transform=ccrs.PlateCarree()
            )

        return fig, ax