import pandas as pd
from rvsearch.search import Search
from rvsearch.inject import Injections, Completeness
from rvsearch.plots import CompletenessPlots

def run_injrec(
    search_path : str,
    searches : Search,
    mstar : float,
    workers : int,
    **inj_kwargs
    ) -> pd.DataFrame:
    """Run injection and recovery simulations

    Args:
        search_path (str): path to search object pickle file
        searches (Search): rvsearch Search object with found planets
        mstar (float): stellar mass in solar units
        workers (int): number of cores for inj/rec tests
        **inj_kwargs: keyword args to pass to rvsearch Injections class

    Returns:
        pd.DataFrame: recoveries
    """
    # instantiate Injections class
    inj = Injections(f'{search_path}/search.pkl', **inj_kwargs)
    
    # run injections
    recoveries = inj.run_injections(num_cpus=workers)
    recoveries.to_csv(f'{search_path}/recoveries.csv', index=False)
        
    # plot completeness
    comp = Completeness(recoveries, mstar=mstar)
    cp = CompletenessPlots(comp, searches=[searches])
    fig = cp.completeness_plot(
        xlabel='$a$ [AU]', 
        ylabel=r'M$\sin{i}$ [M$_{\oplus}$]',
        title=searches.starname
    )
    fig.savefig(f'{search_path}/{searches.starname}_recoveries.pdf')
    
    return recoveries
    
    
    