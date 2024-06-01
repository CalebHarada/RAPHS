"""
Extra code for stuffs

"""

def convert_rhkp_to_sindex(
    rhkp : float,
    bv_mag : float,
    subgiant : bool = False
    ) -> float:
    """Convert R_HKp to Mt Wilson S-index

    Conversion procedure from Gomes da Silva et al. (2021)

    Args:
        rhkp (float): R_HK_prime
        bv_mag (float): B-V color (mag)
        subgiant (bool, optional): Main sequence or subgiant star. Defaults to False (main sequence).

    Returns:
        float: S-index
    """
    # constants
    ALPHA = 1.34E-4
    A = -4.898
    B = 1.918
    C = -2.893
    D = -0.066 if subgiant else 0.25
    E = -0.25 if subgiant else -1.33
    F = -0.49 if subgiant else 0.43
    G = 0.45 if subgiant else 0.24
    
    # photospheric contribution
    log_Rphot = A + B * bv_mag**2 + C * bv_mag**3
    
    # bolometric correction
    log_Ccf = D * bv_mag**3 + E * bv_mag**2 + F * bv_mag + G
    
    # calculate Mt Wilson S-index
    S_mw = (rhkp + 10**log_Rphot) / (ALPHA * 10**log_Ccf)
    
    return S_mw