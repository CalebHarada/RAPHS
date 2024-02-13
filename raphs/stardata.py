import os

import pandas as pd
from radvel.utils import bintels

class StarData():
    """StarData

    Class that defines data for a given star.

    Args:
        hd_identifier (int): HD identifier number for a star.
        data_dir (str, optional): Directory where all data is stored. Defaults to 'data/'.
    """
    def __init__(self, 
        hd_identifier : int, 
        data_dir : str = 'data/',
        ) -> None:
        """__init__
        
        """
        self.hd_identifier = hd_identifier
        self.data_dir = data_dir
        self._binned = False
        
        # load the EMSL/SPORES catalog
        self.catalog_df = pd.read_csv(self.data_dir + 'spores_catalog_v1.0.0.csv')
        
        # Find catalog entry for given HD target
        try:
            self.catalog_entry = self._load_catalog_entry()
        except ValueError:
            raise
        
        # Load HARPS data
        self.harps_df = None
        try:
            self.harps_df = self._load_harps_rvbank_data()
        except FileNotFoundError as err:
            print(err)
            pass
        
        # Load HIRES data
        self.hires_df = None
        try:
            self.hires_df = self._load_hires_ebps_data()
        except FileNotFoundError as err:
            print(err)
            pass
        
        # Combine data sets
        self.rv_data = self._combine_rvs()
        
        return
    
    
    def _load_catalog_entry(self) -> dict:
        """load catalog entry

        Attempt to load row from SPORES catalog

        Raises:
            ValueError: no catalog entry found for given HD number

        Returns:
            dict: catalog entry for given HD name
        """
        hd_name = f'HD {self.hd_identifier}'
        catalog_entry = self.catalog_df[self.catalog_df['hd_name'] == hd_name]
        
        # Check if entry exists
        if len(catalog_entry) == 0:
            raise ValueError(f'No catalog entry for {hd_name}.')
        
        catalog_entry_dict = catalog_entry.iloc[0].to_dict()
        
        return catalog_entry_dict
    
    
    def _load_harps_rvbank_data(self) -> pd.DataFrame:
        """load HARPS RVBank data

        Read csv file from RVBank archive
        
        Raises:
            FileNotFoundError: no HARPS data found for given HD number

        Returns:
            pd.DataFrame: table of values
        """
        harps_rvbank_dir = self.data_dir + 'harps_rv_bank'
        
        # Attempt on HD name
        try:
            file_name = f'HD{self.hd_identifier}.csv'
            harps_rvbank_data = pd.read_csv(f'{harps_rvbank_dir}/{file_name}.csv', index_col=0)
            return harps_rvbank_data
        except FileNotFoundError:
            pass
        
        # Attempt on GJ name
        try:
            gj_name = ''.join(self.catalog_entry['gj_name'].split())
            harps_rvbank_data = pd.read_csv(f'{harps_rvbank_dir}/{gj_name}.csv', index_col=0)
            return harps_rvbank_data
        except FileNotFoundError:
            pass
        
        # Attempt on HIP name
        try:
            hip_name = ''.join(self.catalog_entry['hip_name'].split())
            harps_rvbank_data = pd.read_csv(f'{harps_rvbank_dir}/{hip_name}.csv', index_col=0)
            return harps_rvbank_data
        except FileNotFoundError:
            pass
        
        # Attempt on TYC name
        try:
            tyc_name = 'TYC' + str(self.catalog_entry['tycho2_id'])
            harps_rvbank_data = pd.read_csv(f'{harps_rvbank_dir}/{tyc_name}.csv', index_col=0)
            return harps_rvbank_data
        except FileNotFoundError:
            pass
        
        # No HARPS data found
        raise FileNotFoundError(f'No HARPS data found for HD {self.hd_identifier}!')
    
    
    def _load_hires_ebps_data(self) -> pd.DataFrame:
        """load Keck/HIRES EBPS archive RV data

        Read csv file from Keck HIRES EBPS archive
        
        Raises:
            FileNotFoundError: no Keck/HIRES data found for given HD number

        Returns:
            pd.DataFrame: table of values
        """
        hires_ebps_dir = self.data_dir + 'ebps_keck_hires'
        col_names = ['JD', 'RVel', 'e_RVel', 'S_value', 'Halpha', 'phot_per_pix', 't_exp']

        # Attempt on HD name
        try:
            file_name = f'HD{self.hd_identifier}_KECK.vels'
            keck_hires_data = pd.read_csv(f'{hires_ebps_dir}/{file_name}', sep='\s+', header=None, names=col_names)
            return keck_hires_data
        except FileNotFoundError:
            pass
        
        # Attempt on HIP name
        try:
            hip_name = ''.join(self.catalog_entry['hip_name'].split())
            file_name = f'{hip_name}_KECK.vels'
            keck_hires_data = pd.read_csv(f'{hires_ebps_dir}/{file_name}', sep='\s+', header=None, names=col_names)
            return keck_hires_data
        except FileNotFoundError:
            pass

        # No HIRES data found
        raise FileNotFoundError(f'No HIRES data found for HD {self.hd_identifier}!')
    
    
    def _combine_rvs(self) -> pd.DataFrame:
        """combine rvs data sets

        Combine RV data sets from different sources

        Returns:
            pd.DataFrame: rv_data
        """
        rv_data = pd.DataFrame()
        
        # add HARPS data
        if self.harps_df is not None:
            # pre-upgrade
            harps_pre_msk = self.harps_df['BJD'] <= 2_457_163  # pre-upgrade (Trifonov et al. 2020)
            harps_pre_data = self.harps_df.loc[harps_pre_msk, ['BJD', 'RV_mlc_nzp', 'e_RV_mlc_nzp']]
            harps_pre_data['tel'] = 'harps_pre'
            harps_pre_data = harps_pre_data.rename(columns={'BJD':'jd', 'RV_mlc_nzp':'mnvel', 'e_RV_mlc_nzp':'errvel'})
            rv_data = pd.concat([rv_data, harps_pre_data])

            # post-upgrade
            harps_post_msk = self.harps_df['BJD'] >= 2_457_173  # post-upgrade (Trifonov et al. 2020)
            harps_post_data = self.harps_df.loc[harps_post_msk, ['BJD', 'RV_mlc_nzp', 'e_RV_mlc_nzp']]
            harps_post_data['tel'] = 'harps_post'
            harps_post_data = harps_post_data.rename(columns={'BJD':'jd', 'RV_mlc_nzp':'mnvel', 'e_RV_mlc_nzp':'errvel'})
            rv_data = pd.concat([rv_data, harps_post_data])
            
        # add HIRES data
        if self.hires_df is not None:
            # pre-upgrade
            hires_pre_msk = self.hires_df['JD'] <= 2_453_236  # pre-upgrade (August 18, 2004 = JD 2453236)
            hires_pre_data = self.hires_df.loc[hires_pre_msk, ['JD', 'RVel', 'e_RVel']]
            hires_pre_data['tel'] = 'hires_pre'
            hires_pre_data = hires_pre_data.rename(columns={'JD':'jd', 'RVel':'mnvel', 'e_RVel':'errvel'})
            rv_data = pd.concat([rv_data, hires_pre_data])
            
            # post-upgrade
            hires_post_msk = self.hires_df['JD'] >= 2_453_236  # post-upgrade (August 18, 2004 = JD 2453236)
            hires_post_data = self.hires_df.loc[hires_post_msk, ['JD', 'RVel', 'e_RVel']]
            hires_post_data['tel'] = 'hires_post'
            hires_post_data = hires_post_data.rename(columns={'JD':'jd', 'RVel':'mnvel', 'e_RVel':'errvel'})
            rv_data = pd.concat([rv_data, hires_post_data])
        
        # sort and re-index data
        rv_data = rv_data.sort_values('jd')
        rv_data = rv_data.reset_index(drop=True)
        
        return rv_data
    
    
    
    def bin_rvs(self,
        bin_size : float = 0.5
        ) -> None:
        """bin_rvs

        Bin RVs using radvel builtin function

        Args:
            bin_size (float, optional): bin size in days. Defaults to 0.5.
        """
        if not self._binned:
            # apply radvel bintel function
            jd_bin, mnvel_bin, errvel_bin, tel_bin = bintels(
                self.rv_data['jd'].values,
                self.rv_data['mnvel'].values,
                self.rv_data['errvel'].values,
                self.rv_data['tel'].values,
                binsize=bin_size
            )
            
            # convert back to Pandas DF
            bin_dict = {'jd': jd_bin, 'mnvel': mnvel_bin, 'errvel': errvel_bin, 'tel': tel_bin}
            data_binned = pd.DataFrame(data=bin_dict)
            
            # save to rv_data attribute and
            self.rv_data = data_binned
            self._binned = True
            
        else:
            print('RVs have already been binned. Cannot bin again.')
        
        return
    
    
    def to_csv(self,
        save_fn : str = 'default'
        ) -> None:
        """to_csv

        Save RV data to a CSV file

        Args:
            save_fn (str, optional): Save filename. Defaults to 'default'.
        """
        # create new directory if set to default
        if save_fn == 'default':
            save_dir = self.data_dir + 'combined_RVs/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            save_fn = save_dir + f'HD{self.hd_identifier}.csv'
        
        # save DF as CSV
        self.rv_data.to_csv(save_fn)
        
        return
        
    
    
        