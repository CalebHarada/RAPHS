import matplotlib.pyplot as plt

from raphs.searchrvs import *


def test_search() -> None:
    """Test planet RV search
    """
    
    data = StarData('HD 75732 A')
        
    search_rvs(
        data,
        output_dir='test_outputs/',
        max_planets=0,
        min_per=8,
        workers=4,
        mcmc=False,
        verbose=True
    )
    
    return



if __name__ == '__main__':
    test_search()