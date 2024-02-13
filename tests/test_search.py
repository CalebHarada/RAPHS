import sys
import os

import matplotlib.pyplot as plt

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(MAIN_DIR))

from rvpipeline.search import *


def test_search() -> None:
    """_summary_

    _extended_summary_
    """
    
    data = StarData(115617)
    data.bin_rvs()
        
    search_rvs(
        data,
        max_planets=8,
        min_per=3,
        workers=4,
        mcmc=True,
        verbose=True
    )
    
    return



if __name__ == '__main__':
    test_search()