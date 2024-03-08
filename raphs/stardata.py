import os

import pandas as pd

from .utilities import *


class StarData():
    """StarData

    Class that defines data for a given star.

    Args:
        hd_name (int): HD identifier number for a star.
        data_dir (str, optional): Directory where all data is stored. Defaults to 'data/'.
        outlier_threshold (float, optional): Outlier rejection threshold in sigma. Defaults to 5.
    """
    def __init__(self, 
        hd_name : str, 
        data_dir : str = 'data/',
        outlier_threshold : float = 5,
        ) -> None:
        """__init__
        
        """
        self.hd_name = hd_name
        self.data_dir = data_dir
        self.outlier_threshold = outlier_threshold
        
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
        self.rv_data = None
        self.S_index_data = None
        try:
            self.rv_data = self._combine_rvs()
            self.S_index_data = self._combine_S_indexes()
        except ValueError as err:
            print(err)
            pass
        
        return
    
    
    def _load_catalog_entry(self) -> dict:
        """load catalog entry

        Attempt to load row from SPORES catalog

        Raises:
            ValueError: no catalog entry found for given HD number

        Returns:
            dict: catalog entry for given HD name
        """
        catalog_entry = self.catalog_df[self.catalog_df['hd_name'] == self.hd_name]
        
        # Check if entry exists
        if len(catalog_entry) == 0:
            raise ValueError(f'No catalog entry for {self.hd_name}.')
        
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
            hd_name = ''.join(self.hd_name.split())
            harps_rvbank_data = pd.read_csv(f'{harps_rvbank_dir}/{hd_name}.csv', index_col=0)
            return harps_rvbank_data
        except FileNotFoundError:
            pass
        
        # Attempt again if letter in name
        if 'A' in self.hd_name:
            try:
                hd_name = ''.join(self.hd_name.split()[:-1])
                harps_rvbank_data = pd.read_csv(f'{harps_rvbank_dir}/{hd_name}.csv', index_col=0)
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
        raise FileNotFoundError(f'No HARPS data found')
    
    
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
            hd_name = ''.join(self.hd_name.split())
            file_name = f'{hd_name}_KECK.vels'
            keck_hires_data = pd.read_csv(f'{hires_ebps_dir}/{file_name}', sep='\s+', header=None, names=col_names)
            return keck_hires_data
        except FileNotFoundError:
            pass
        
        # Attempt again if letter in name
        if 'A' in self.hd_name:
            try:
                hd_name = ''.join(self.hd_name.split()[:-1])
                file_name = f'{hd_name}_KECK.vels'
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
        raise FileNotFoundError(f'No HIRES data found')
    
    
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
        
        # clean, sort, and re-index data
        if len(rv_data) > 0:
            
            # reject outliers
            mean = rv_data['mnvel'].mean()
            std = rv_data['mnvel'].std()
            threshold = std * self.outlier_threshold
            rv_data = rv_data.drop(rv_data[abs(rv_data['mnvel'] - mean) > threshold].index)
            
            # sort by JD
            rv_data = rv_data.sort_values('jd')
            
            # reset index
            rv_data = rv_data.reset_index(drop=True)
            
            return rv_data
        
        else:
            raise ValueError(f'WARNING: No RV data!')
        
        
        
    def _combine_S_indexes(self) -> pd.DataFrame:
        """combine S-index data sets

        Combine S-index data sets from different sources

        Returns:
            pd.DataFrame: S_index_data
        """
        st_activity_data = pd.DataFrame()
        
        # grab B-V mag
        bv_mag = self.catalog_entry['sy_bvmag']
        
        # True if star is evolved
        subgiant = ('IV' in self.catalog_entry['st_spectype'])
        
        # add HARPS data
        if self.harps_df is not None:
            # pre-upgrade
            harps_pre_msk = self.harps_df['BJD'] <= 2_457_163  # pre-upgrade (Trifonov et al. 2020)
            harps_pre_data = self.harps_df.loc[harps_pre_msk, ['BJD', 'RHKp']]
            harps_pre_data['sind'] = convert_rhkp_to_sindex(harps_pre_data['RHKp'].values, bv_mag=bv_mag, subgiant=subgiant)
            harps_pre_data['errs'] = 0.007  # Empirically determined S-index uncertainty
            harps_pre_data['tel'] = 'harps_pre'
            harps_pre_data.drop(columns=['RHKp'], inplace=True)
            harps_pre_data = harps_pre_data.rename(columns={'BJD':'jd'})
            st_activity_data = pd.concat([st_activity_data, harps_pre_data])

            # post-upgrade
            harps_post_msk = self.harps_df['BJD'] >= 2_457_173  # post-upgrade (Trifonov et al. 2020)
            harps_post_data = self.harps_df.loc[harps_post_msk, ['BJD', 'RHKp']]
            harps_post_data['sind'] = convert_rhkp_to_sindex(harps_post_data['RHKp'].values, bv_mag=bv_mag, subgiant=subgiant)
            harps_post_data['errs'] = 0.006  # Empirically determined S-index uncertainty
            harps_post_data['tel'] = 'harps_post'
            harps_post_data.drop(columns=['RHKp'], inplace=True)
            harps_post_data = harps_post_data.rename(columns={'BJD':'jd'})
            st_activity_data = pd.concat([st_activity_data, harps_post_data])
            
        # add HIRES data
        if self.hires_df is not None:
            # pre-upgrade
            hires_pre_msk = self.hires_df['JD'] <= 2_453_236  # pre-upgrade (August 18, 2004 = JD 2453236)
            hires_pre_data = self.hires_df.loc[hires_pre_msk, ['JD', 'S_value']]
            hires_pre_data['errs'] = 0.01  # Empirically determined S-index uncertainty
            hires_pre_data['tel'] = 'hires_pre'
            hires_pre_data = hires_pre_data.rename(columns={'JD':'jd', 'S_value':'sind'})
            st_activity_data = pd.concat([st_activity_data, hires_pre_data])
            
            # post-upgrade
            hires_post_msk = self.hires_df['JD'] >= 2_453_236  # post-upgrade (August 18, 2004 = JD 2453236)
            hires_post_data = self.hires_df.loc[hires_post_msk, ['JD', 'S_value']]
            hires_post_data['errs'] = 0.009  # Empirically determined S-index uncertainty
            hires_post_data['tel'] = 'hires_post'
            hires_post_data = hires_post_data.rename(columns={'JD':'jd', 'S_value':'sind'})
            st_activity_data = pd.concat([st_activity_data, hires_post_data])
        
        # clean, sort, and re-index data
        if len(st_activity_data) > 0:
            
            # remove negative (bad) values
            st_activity_data = st_activity_data.drop(st_activity_data[st_activity_data['sind'] < 0].index)
            
            # reject outliers
            mean = st_activity_data['sind'].mean()
            std = st_activity_data['sind'].std()
            threshold = std * self.outlier_threshold
            st_activity_data = st_activity_data.drop(st_activity_data[abs(st_activity_data['sind'] - mean) > threshold].index)
            
            # sort
            st_activity_data = st_activity_data.sort_values('jd')
            
            # reset index
            st_activity_data = st_activity_data.reset_index(drop=True)
            
            return st_activity_data
        
        else:
            raise ValueError(f'WARNING: No S-index data!')
        

    
    def to_csv(self,
        save_fn : str
        ) -> None:
        """to_csv

        Save RV data to a CSV file

        Args:
            save_fn (str): Save filename.
        """

        # save DF as CSV
        self.rv_data.to_csv(save_fn)
        
        return
        
    
    
        