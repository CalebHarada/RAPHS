from rvsearch import search

from .stardata import StarData

def search_rvs(
    data : StarData,
    **kwargs
    ) -> None:
    """_summary_

    _extended_summary_

    Args:
        rv_data (StarData): _description_
    """
    
    searcher = search.Search(
        data.rv_data,
        starname=data.hd_identifier,
        **kwargs
    )
    
    searcher.run_search(outdir=f'../OUT/{searcher.starname}')
    
    return


