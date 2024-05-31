import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from radvel import posterior
from astropy.timeseries import LombScargle

from .stardata import StarData


class LSPeriodogram():
    """Object for Lomb-Scargle periodograms

    Args:
        data (StarData): StarData object
        output_dir (str): output directory
        bin_size (float, optional): Bin size in days. Defaults to 0.5.
    """
    def __init__(self,
        data : StarData,
        output_dir : str,
        bin_size : float = 0.5,
        ) -> None:
        """__init__
        
        """
        self.data = data
        self.output_dir = output_dir
        self.bin_size = bin_size
        self.tels = np.unique(data.rv_data['tel'].values)
        self.lsp_dict = None
        
        pass
    
    
    def compute_lsps(self,
        min_per : float = 3.1,
        delta_f : float = 1e-5,
        ) -> dict:
        """Compute LS periodograms for the data.

        Args:
            min_per (float, optional): minimum period. Defaults to 1.
            delta_f (float, optional): frequency grid spacing. Defaults to 1e-6.

        Returns:
            dict: lsp_dict
        """       
        rvs = self.data.rv_data
        svals = self.data.S_index_data
        
        max_per = 1.5 * np.ptp(rvs['jd'])
        f = np.arange(1/max_per, 1/min_per, delta_f)
        
        # combined data sets
        lsp_dict = dict(all=dict(frequency=f))
        lsp_dict['all']['rv_power'] = LombScargle(rvs['jd'], rvs['mnvel'], rvs['errvel']).power(f)
        lsp_dict['all']['sval_power'] = LombScargle(svals['jd'], svals['sind'], svals['errs']).power(f)
        
        # individual instruments
        for tel in self.tels:
            # frequencies
            max_per = 1.5 * np.ptp(rvs.loc[rvs['tel'] == tel, 'jd'])
            f = np.arange(1/max_per, 1/min_per, delta_f)
            lsp_dict[tel] = dict(frequency=f)
            
            # RVs
            lsp_dict[tel]['rv_power'] = LombScargle(
                rvs.loc[rvs['tel'] == tel, 'jd'],
                rvs.loc[rvs['tel'] == tel, 'mnvel'],
                rvs.loc[rvs['tel'] == tel, 'errvel']
            ).power(f)
            
            # S index values
            lsp_dict[tel]['sval_power'] = LombScargle(
                svals.loc[svals['tel'] == tel, 'jd'],
                svals.loc[svals['tel'] == tel, 'sind'],
                svals.loc[svals['tel'] == tel, 'errs']
            ).power(f)
            
            # window functions
            lsp_dict[tel]['windowfn_power'] = LombScargle(
                rvs.loc[rvs['tel'] == tel, 'jd'],
                np.ones(len(rvs.loc[rvs['tel'] == tel, 'jd'])),
                fit_mean=False, center_data=False
            ).power(f)
        
        self.lsp_dict = lsp_dict
        
        return lsp_dict
        
    
    def get_periods_from_posterior(self):
        """Load periods form radvel posterior object

        Returns:
            list: periods
        """
        try:
            post = posterior.load(self.output_dir + '/RV_search/post_final.pkl')
            param_list = post.list_params()
            
            periods = []
            for param in param_list:
                if param.startswith('per'):
                    periods.append(post.params[param].value)
            
            if len(periods) > 0:
                return periods
            else: return None
            
        except FileNotFoundError:
            return None
            
        
    
    def compute_fap_thresh(self,
            power : np.ndarray,
            fap : float
        ) -> tuple:
        """Calculate the empirical power threshold given some FAP value.
        
        Also calculates the minimum FAP value given the LS power.
        
        NOTE: implementation from RVSearch: 
              https://github.com/California-Planet-Search/rvsearch/blob/9f7b3b2265a0dbff56cff4771fab54e1826de639/rvsearch/periodogram.py

        Args:
            power (np.ndarray): power array
            fap (float): FAP value

        Returns:
            tuple: (power_thresh, fap_min)
        """
        # sort power
        power_sorted = np.sort(power)
        
        # crop out the 50th to 95th percentile data and save the median value
        power_crop = power_sorted[int(0.5 * len(power_sorted)) : int(0.95 * len(power_sorted))]
        power_med = power_crop[0]
        
        # compute the log(histogram)
        hist, edges = np.histogram(power_crop - power_med, bins=10)
        centers = (edges[1:] + edges[:-1]) / 2.
        loghist = np.log10(hist)
        
        # fit a line
        a, b = np.polyfit(centers[np.isfinite(loghist)], loghist[np.isfinite(loghist)], 1)
        B = 10**b
        A = -a*np.log(10)
        
        # calculate the power threshold value for the given FAP
        power_thresh = np.log(fap / len(power)) / (-A) + power_med
        
        # calculate the minimum FAP
        fap_min = np.exp(-A * (power_sorted[-1] - power_med)) * len(power)
        
        return (power_thresh, fap_min)
    
    
    
    
    def plot_lsps(self, fap=0.001, **compute_kwargs):
        """Plot LS periodograms

        Args:
            fap (float, optional): False alarm probability. Defaults to 0.001.
        """
        
        
        # compute LS periodograms
        lsps = self.compute_lsps(**compute_kwargs)
        
        # set up figure
        fig, axes = plt.subplots(
            int(2 * (len(self.tels) + 1)), 1,
            sharex=True,
            figsize=(8,10) 
        )
        axes[0].set_title(self.data.hd_name, size=18)
        
        # all RVs
        ax = axes[0]
        ax.plot(1/lsps['all']['frequency'], lsps['all']['rv_power'], c='navy', lw=1, label='All RVs')
        ax.axhline(self.compute_fap_thresh(lsps['all']['rv_power'], fap=fap)[0], ls='--', lw=1, c='firebrick', label=f'FAP = {fap}')
        ax.axhspan(-1, self.compute_fap_thresh(lsps['all']['rv_power'], fap=fap)[0], alpha=0.1)
        ax.legend(loc=2)
        
        # all S-index values
        ax = axes[1]
        ax.plot(1/lsps['all']['frequency'], lsps['all']['sval_power'], c='navy', lw=1, label='All S-index')
        ax.axhline(self.compute_fap_thresh(lsps['all']['sval_power'], fap=fap)[0], ls='--', lw=1, c='firebrick')
        ax.axhspan(-1, self.compute_fap_thresh(lsps['all']['sval_power'], fap=fap)[0], alpha=0.1)
        ax.legend(loc=2)
        
        for i, tel in enumerate(self.tels):
            # RV power
            ax = axes[int(2*i + 2)]
            ax.plot(1/lsps[tel]['frequency'], lsps[tel]['rv_power'], c='navy', lw=1, label=f'{tel} RVs')
            ax.axhline(self.compute_fap_thresh(lsps[tel]['rv_power'], fap=fap)[0], ls='--', lw=1, c='firebrick')
            ax.axhspan(-1, self.compute_fap_thresh(lsps[tel]['rv_power'], fap=fap)[0], alpha=0.1)
            ax.legend(loc=2)
            
            # window function power
            ax = axes[int(2*i + 3)]
            ax.plot(1/lsps[tel]['frequency'], lsps[tel]['windowfn_power'], c='navy', lw=1, label=f'{tel} Window')
            ax.axhline(self.compute_fap_thresh(lsps[tel]['windowfn_power'], fap=fap)[0], ls='--', lw=1, c='firebrick')
            ax.axhspan(-1, self.compute_fap_thresh(lsps[tel]['windowfn_power'], fap=fap)[0], alpha=0.1)
            ax.legend(loc=2)
        
        # add detected periods
        periods_post = self.get_periods_from_posterior()
        if periods_post is not None:
            for per in periods_post:
                for ax in axes:
                    ax.axvline(per, ls='--', c='k', lw=1, alpha=0.5, zorder=0)
            
        # global adjustments
        for ax in axes:
            ax.set_yticks([])
            ax.set_ylim(0, )
            ax.set_ylabel('Power', size=14)
            ax.axvline(365.25, ls='-', c='r', lw=5, alpha=0.25, zorder=0)  # alias at one year
            ax.axvline(29.5, ls='-', c='k', lw=5, alpha=0.25, zorder=0)  # alias at one lunar cycle
        axes[-1].set_xscale('log')
        axes[-1].set_xticks([10, 100, 1000, 10000])
        axes[-1].set_xticklabels([10, 100, 1000, 10000])
        axes[-1].set_xlim(1/lsps['all']['frequency'].max(), 1/lsps['all']['frequency'].min())
        axes[-1].set_xlabel('Period (days)', size=14)
        
        fig.savefig(self.output_dir + f'/{self.data.hd_name}_LSperiodograms.pdf', dpi=200)
        
        return fig
    
    
