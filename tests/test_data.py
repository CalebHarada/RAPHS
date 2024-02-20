import matplotlib.pyplot as plt

from raphs.stardata import StarData


def test_data() -> None:
    """Test loading data
    
    """
    
    data = StarData('HD 75732 A')

        
    # save to csv
    data.to_csv()
    
    return None



if __name__ == '__main__':
    test_data()