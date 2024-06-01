import os

import numpy as np
from rvsearch.search import Search
from rvsearch.plots import PeriodModelPlot

from .stardata import StarData


def search_rvs(
    data : StarData,
    output_dir : str,
    **search_kwargs
    ) -> str:
    """Search RVs in a given data set

    Args:
        data (StarData): StarData object
        output_dir (str): output directory
    
    Returns:
        search.Search: searcher
    """
    
    # get stellar mass and uncert
    # NOTE: here using ARIADNE-derived masses
    mstar = (
        data.catalog_entry['sed_grav_mass'],
        np.mean([data.catalog_entry['sed_grav_masserr1'], data.catalog_entry['sed_grav_masserr2']])
        )
    
    # initiate search
    searcher = Search(
        data.rv_data_bin,
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
    sinds = data.sind_data_bin.copy()
    sinds.rename(
        columns={
            'sind' : 'mnvel',
            'errs' : 'errvel',
            }, 
        inplace=True
    )
    
    # get stellar mass and uncert
    # NOTE: here using ARIADNE-derived masses
    mstar = (
        data.catalog_entry['sed_grav_mass'],
        np.mean([data.catalog_entry['sed_grav_masserr1'], data.catalog_entry['sed_grav_masserr2']])
        )
    
    # initiate search
    searcher = Search(
        sinds,
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