from copy import deepcopy
import numpy as np
import pandas as pd
import xarray as xr
import plotly.express as px

from . import utils
class Obs:
    def __init__(self, df:pd.DataFrame):
        self.df = df
        self.df['lon'] = (df['lon'] + 360) % 360
        self.nobs = len(df)
        self.pids = df['pid'].values
        self.records = {}
        for pid in self.pids:
            self.records[pid] = self[pid]

    @property
    def y(self):
        return self.df['value'].values[..., np.newaxis]

    @property
    def y_locs(self):
        return self.df[['lat', 'lon']].values

    @property
    def R(self):
        return np.diag(self.df['R'].values)

    def copy(self):
        return deepcopy(self)

    def __getitem__(self, pid:str):
        mask = self.df['pid'] == pid
        row = self.df[mask].iloc[0]
        rec = ProxyRecord(row)
        return rec
    
    def get_dist(self):
        lats = self.df['lat'].values
        lons = self.df['lon'].values
        lat1, lat2 = np.meshgrid(lats, lats)
        lon1, lon2 = np.meshgrid(lons, lons)
        self.dist = utils.gcd(lat1, lon1, lat2, lon2)
        return self.dist

    def plotly(self, **kwargs):
        ''' Plot the database on an interactive map utilizing Plotly
        '''
        return px.scatter_geo(
            self.df, lat='lat', lon='lon',
            color='type',
            hover_name='pid',
            projection='natural earth',
            **kwargs,
        )


class ProxyRecord:
    def __init__(self, data:pd.Series):
        self.data = data.copy()
        if 'time' in data: self.data['time'] = np.array(data['time'])
        if 'value' in data: self.data['value'] = np.array(data['value']) 

        if 'seasonality' in data:
            if isinstance(data['seasonality'], str):
                self.data['seasonality'] = utils.str2list(data['seasonality'])
            elif isinstance(data['seasonality'], list):
                self.data['seasonality'] = data['seasonality']
            else:
                raise ValueError('Wrong seasonality type; should be a string or a list.')


    def get_clim(self, clim_ds, vns:list=None, verbose=False):
        if vns is None:
            vns = clim_ds.data_vars
        else:
            vns = [vn for vn in vns if vn in clim_ds.data_vars]

        self.clim = xr.Dataset()
        for vn in vns:
            self.clim[vn] = clim_ds[vn].x.nearest2d(
            # filled_da = clim_ds[vn].ffill(dim='lon').bfill(dim='lon').ffill(dim='lat').bfill(dim='lat')
            # self.clim[vn] = filled_da.sel(
                lat=self.data.lat,
                lon=self.data.lon,
                method='nearest',
            ).sel(month=self.data.seasonality).mean(dim='month')
            if verbose: utils.p_success(f'>>> ProxyRecord.clim["{vn}"] created')

        self.clim.attrs['seasonality'] = self.data.seasonality

