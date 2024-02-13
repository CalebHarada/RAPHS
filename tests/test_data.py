import sys
import os

import matplotlib.pyplot as plt

from raphs.stardata import StarData


def test_data() -> None:
    """_summary_

    _extended_summary_
    """
    
    data = StarData(115617)
    # data = StarData(166)
    
    # plt.scatter(data.rv_data['jd'], data.rv_data['mnvel'], c='k', s=5)
    
    # bin RVs
    data.bin_rvs()
    
    # plt.scatter(data.rv_data['jd'], data.rv_data['mnvel'], c='r', s=10)
    # plt.show()
    
    # save to csv
    data.to_csv()

    
    return None



if __name__ == '__main__':
    test_data()