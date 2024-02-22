from raphs.stardata import StarData
from raphs.searchrvs import search_rvs


########################################################
# LIST OF TARGET STARS (eventually, should do all stars)
sample_stars = ['HD 190360']
########################################################
   

class Driver():
    """Main driver class to conduct RV analyses

       Args:
        target_list (list, optional): list of strings with target HD
                            names as they appear in the SPORES catalog.
                            Defaults to sample_stars.
    """
    def __init__(self, target_list : list = sample_stars) -> None:
        """__init__
        
        """
        self.target_list = target_list
        
        pass
    
    
    def do_everything(self,
            data_dir : str = '../data/',
            out_dir : str = 'OUT'
        ) -> None:
        """Run everything

        """
        
        for star in self.target_list:

            # load data
            data = StarData(star, data_dir=data_dir)
            
            # run search
            search_rvs(
                data=data,
                output_dir=out_dir,
                fap=0.001,
                crit='bic',
                max_planets=8,
                min_per=3,
                workers=64, 
                mcmc=True, 
                verbose=True
            )

        
        