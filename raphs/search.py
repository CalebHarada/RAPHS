import os

import numpy as np
import pandas as pd
from rvsearch.search import Search
from rvsearch.plots import PeriodModelPlot
from radvel.utils import bintels

from .stardata import StarData


def search_rvs(
    data : StarData,
    output_dir : str,
    bin_size : float = 0.5,
    **search_kwargs
    ) -> str:
    """Search RVs in a given data set

    Args:
        data (StarData): StarData object
        output_dir (str): output directory
        bin_size (float, optional): Bin size in days. Defaults to 0.5.
    
    Returns:
        search.Search: searcher
    """
    # grab RV time series
    if bin_size is None:
        rv_timeseries = data.rv_data
            
    # bin RVs
    else:
        jd_bin, mnvel_bin, errvel_bin, tel_bin = bintels(
            data.rv_data['jd'].values,
            data.rv_data['mnvel'].values,
            data.rv_data['errvel'].values,
            data.rv_data['tel'].values,
            binsize=bin_size
        )
        # update values in new df
        rv_timeseries = pd.DataFrame()
        rv_timeseries['jd'] = jd_bin
        rv_timeseries['mnvel'] = mnvel_bin
        rv_timeseries['errvel'] = errvel_bin
        rv_timeseries['tel'] = tel_bin
                
    
    # get stellar mass and uncert
    # NOTE: here using ARIADNE-derived masses
    mstar = (
        data.catalog_entry['sed_grav_mass'],
        np.mean([data.catalog_entry['sed_grav_masserr1'], data.catalog_entry['sed_grav_masserr2']])
        )
    
    # initiate search
    searcher = Search(
        rv_timeseries,
        starname=data.hd_name,
        mstar=mstar,
        **search_kwargs
    )
    
    # set up output dir
    out_subdir = f'{output_dir}/RV_search'
    if not os.path.exists(out_subdir):
        os.makedirs(out_subdir)
    
    # run search
    searcher.run_search(outdir=out_subdir)
    
    # create summary plot 
    pmp = PeriodModelPlot(searcher, saveplot=f'{out_subdir}/{searcher.starname}_summary.pdf')
    pmp.plot_summary()
    
    return searcher


def search_sinds(
    data : StarData,
    output_dir : str,
    bin_size : float = 0.5,
    **search_kwargs
    ) -> str:
    """Search S index values in a given data set

    Args:
        data (StarData): StarData object
        output_dir (str): output directory
        bin_size (float, optional): Bin size in days. Defaults to 0.5.
    
    Returns:
        search.Search: searcher
    """
    # must change column names to match rvsearch syntax
    sinds = data.S_index_data.copy()
    sinds.rename(
        columns={
            'sind' : 'mnvel',
            'errs' : 'errvel',
            }, 
        inplace=True
    )
    
    # bin time series
    if bin_size is not None:
        jd_bin, mnvel_bin, errvel_bin, tel_bin = bintels(
            sinds['jd'].values,
            sinds['mnvel'].values,
            sinds['errvel'].values,
            sinds['tel'].values,
            binsize=bin_size
        )
        # update values in new df
        sind_timeseries = pd.DataFrame()
        sind_timeseries['jd'] = jd_bin
        sind_timeseries['mnvel'] = mnvel_bin
        sind_timeseries['errvel'] = errvel_bin
        sind_timeseries['tel'] = tel_bin
    else:
        sind_timeseries = sinds
                
    
    # get stellar mass and uncert
    # NOTE: here using ARIADNE-derived masses
    mstar = (
        data.catalog_entry['sed_grav_mass'],
        np.mean([data.catalog_entry['sed_grav_masserr1'], data.catalog_entry['sed_grav_masserr2']])
        )
    
    # initiate search
    searcher = Search(
        sind_timeseries,
        starname=data.hd_name,
        mstar=mstar,
        **search_kwargs
    )
    
    # set up output dir
    out_subdir = f'{output_dir}/Sind_search'
    if not os.path.exists(out_subdir):
        os.makedirs(out_subdir)
    
    # run search
    searcher.run_search(outdir=out_subdir)
    
    # create summary plot 
    pmp = PeriodModelPlot(searcher, saveplot=f'{out_subdir}/{searcher.starname}_summary.pdf')
    pmp.plot_summary()
    
    return searcher