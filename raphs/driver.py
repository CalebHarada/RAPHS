import os, sys
import traceback
from datetime import datetime

import numpy as np

from raphs.stardata import StarData
from raphs.periodogram import LSPeriodogram
from raphs.search import search_rvs, search_sinds
from raphs.injrec import run_injrec


    
def do_everything(args) -> None:
    """Run everything
    
    Args:
        args (ArgumentParser): command line arguments
    """

    stdout_ = sys.stdout
    
    # set up output directory
    out_subdir = f'{args.output_dir}/{args.hd_name}'
    if not os.path.exists(out_subdir):
        os.makedirs(out_subdir)
            
    with open(out_subdir + '/log.txt', 'w') as f:
        # start log file
        sys.stdout = f
        print('RAPHS: (R)adial velocity (A)nalysis of (P)otential (H)WO (S)tars')
        print('LOG ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(args.hd_name)
        print('\n---------------------------\n')
            
        try:
            # load data and save CSVs
            print('Loading data...')
            data = StarData(args.hd_name, data_dir=args.data_dir)
        except Exception:
            print('Exception occurred!')
            print(traceback.format_exc())
            
        if data.rv_data is None:
            print('\nNO DATA FOUND. ABORTING RUN.')
            sys.stdout = stdout_
            exit()
        else:
            # save data to csv files
            data.save_csvs(out_subdir)
            
        # check for number of epochs (12 hour bins)
        if len(data.rv_data_bin) < 20:
            print('\nNUMBER OF EPOCHS < 20. ABORTING RUN.')
            sys.stdout = stdout_
            exit()
        print(f'\nNumber of RV epochs = {len(data.rv_data_bin)}')
        
        # check for baseline (10 days)
        baseline = data.rv_data_bin['jd'].max() - data.rv_data_bin['jd'].min()
        if baseline < 10.0:
            print('\nBASELINE < 10 DAYS. ABORTING RUN.')
            sys.stdout = stdout_
            exit()
        print(f'Baseline = {round(baseline, 2)} days ({round(baseline / 365.25, 2)} yrs)')
        
        
        # RV run search
        if args.search:
            print(f'\nSearching RVs...')
            try:
                rv_search_obj = search_rvs(data, out_subdir,
                    trend=True,
                    fap=0.001,
                    crit='bic',
                    max_planets=8,
                    min_per=3,
                    workers=args.num_cpus, 
                    mcmc=args.mcmc, 
                    verbose=True
                )
            except Exception:
                print('Exception occurred!')
                print(traceback.format_exc())
        
         # run injection and recovery
        if args.injrec:
            print(f'\nRunning injections...')
            try:
                _ = run_injrec(
                    search_path=out_subdir + '/RV_search',
                    searches=rv_search_obj,
                    mstar=data.catalog_entry['sed_grav_mass'],
                    workers=args.num_cpus,
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
           
        # s-index analysis         
        if args.sind:
            print(f'\nSearching S values...')
            try:
                _ = search_sinds(
                    data=data,
                    output_dir=out_subdir,
                    fap=0.001,
                    crit='bic',
                    max_planets=8,
                    min_per=3,
                    workers=args.num_cpus, 
                    mcmc=False, 
                    verbose=True
                )
            except Exception:
                print('Exception occurred!')
                print(traceback.format_exc())
        
        # make LS periodograms
        print(f'\nComputing LS periodograms...')  
        try:
            lsp = LSPeriodogram(data, out_subdir)
            lsp.plot_lsps()
        except Exception:
            print('Exception occurred!')
            print(traceback.format_exc())
        
        print(f'\nDONE.')
        
        sys.stdout = stdout_

    
    