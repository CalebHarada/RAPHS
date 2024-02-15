import os

from rvsearch import search

from .stardata import StarData

def search_rvs(
    data : StarData,
    output_dir : str,
    **kwargs
    ) -> None:
    """_summary_

    _extended_summary_

    Args:
        data (StarData): _description_
        output_dir (str): _description_
    """
    
    searcher = search.Search(
        data.rv_data,
        starname=data.hd_name,
        **kwargs
    )
    
    out_subdir = f'{output_dir}/{searcher.starname}'
    if not os.path.exists(out_subdir):
        os.makedirs(out_subdir)
    
    searcher.run_search(outdir=out_subdir)
    
    return


