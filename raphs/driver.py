import os, sys
import traceback
from datetime import datetime


from raphs.stardata import StarData
from raphs.periodogram import LSPeriodogram
from raphs.search import search_rvs, search_sinds
from raphs.injrec import run_injrec



########################################################
# LIST OF TARGET STARS (eventually, should do all stars)
sample_stars = ['HD 190360', 'HD 115617']
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
            mcmc : bool = True,
            sind : bool = True,
            nproc : int = 64,
        ) -> None:
        """Run everything

        """
        stdout_ = sys.stdout
        
        for star in self.target_list:
            
            # set up output dir
            out_subdir = f'{out_dir}/{star}'
            if not os.path.exists(out_subdir):
                os.makedirs(out_subdir)
                
            with open(out_subdir + '/log.txt', 'w') as f:
                # start log file
                sys.stdout = f
                print('RAPHS: (R)adial velocity (A)nalysis of (P)otential (H)WO (S)tars')
                print('LOG ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print(star)
                print('\n---------------------------\n')
                
                try:
                    # load data and save CSVs
                    print('Loading data...')
                    data = StarData(star, data_dir=data_dir)
                    data.rv_data.to_csv(out_subdir + '/rvs.csv')
                    data.S_index_data.to_csv(out_subdir + '/sinds.csv')
                except Exception:
                    print('Exception occurred!')
                    print(traceback.format_exc())
                    
                # check for number of data points
                if len(data.rv_data) < 25:
                    print('\nNUMBER OF RVS < 25. SKIPPING TO NEXT TARGET.')
                    sys.stdout = stdout_
                    continue
                    
                try:
                    # run search
                    print(f'\nSearching RVs...')
                    rv_search_obj = search_rvs(
                        data=data,
                        output_dir=out_subdir,
                        fap=0.001,
                        crit='bic',
                        max_planets=8,
                        min_per=3,
                        workers=nproc, 
                        mcmc=mcmc, 
                        verbose=True
                    )
                except Exception:
                    print('Exception occurred!')
                    print(traceback.format_exc())
                    
                try:
                    # run injection and recovery
                    if inj_rec:
                        print(f'\nRunning injections...')
                        _ = run_injrec(
                            search_path=out_subdir + '/RV_search',
                            searches=rv_search_obj,
                            mstar=data.catalog_entry['sed_grav_mass'],
                            workers=nproc,
                            plim=(3.1, 1e6),
                            klim=(0.1, 1000.0),
                            elim=(0.0, 0.9),
                            num_sim=5000,
                            full_grid=False,
                            beta_e=True
                        )
                except Exception:
                    print('Exception occurred!')
                    print(traceback.format_exc())
                        
                try:
                    # s-index analysis
                    if sind:
                        print(f'\nSearching S values...')
                        _ = search_sinds(
                            data=data,
                            output_dir=out_subdir,
                            fap=0.001,
                            crit='bic',
                            max_planets=8,
                            min_per=3,
                            workers=nproc, 
                            mcmc=False, 
                            verbose=True
                        )
                except Exception:
                    print('Exception occurred!')
                    print(traceback.format_exc())
                    
                try:
                    # make LS periodograms
                    print(f'\nComputing LS periodograms...')
                    lsp = LSPeriodogram(data, out_subdir)
                    lsp.plot_lsps()
                except Exception:
                    print('Exception occurred!')
                    print(traceback.format_exc())
                
                print(f'\nDONE.')
                
                sys.stdout = stdout_

        
        