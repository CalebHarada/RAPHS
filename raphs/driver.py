from raphs.stardata import StarData
from raphs.searchrvs import search_rvs
from raphs.injrec import run_injrec



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
            out_dir : str = 'OUT',
            inj_rec : bool = True,
            nproc : int = 64,
        ) -> None:
        """Run everything

        """
        
        for star in self.target_list:

            # load data
            data = StarData(star, data_dir=data_dir)
            
            # run search
            rv_search_obj, rv_search_dir = search_rvs(
                data=data,
                output_dir=out_dir,
                fap=0.001,
                crit='bic',
                max_planets=8,
                min_per=3,
                workers=nproc, 
                mcmc=True, 
                verbose=True
            )
            
            # run injection and recovery
            if inj_rec:
                recoveries = run_injrec(
                    search_path=f'{rv_search_dir}/search.pkl',
                    searches=[rv_search_obj],
                    mstar=data.catalog_entry['sed_grav_mass'],
                    workers=nproc,
                    plim=(2, 10000),
                    klim=(0.1, 1000),
                    elim=(0.0, 0.9),
                    num_sim=5000,
                    beta_e=True
                )
                

        
        