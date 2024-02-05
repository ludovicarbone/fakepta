import numpy as np
import enterprise.constants as const
from scipy.interpolate import interp1d

'''
The PSD formulas are taken from the library ENTERPRISE, from the file "gp_priors.py"

https://github.com/nanograv/enterprise/blob/master/enterprise/signals/gp_priors.py
'''


def powerlaw(f, log10_A, gamma):

    psd_rn = (10**log10_A)** 2 / (12.0 * np.pi**2) * const.fyr**(gamma-3) * f**(-gamma)
    return psd_rn


def turnover(f, log10_A=-15, gamma=4.33, lf0=-8.5, kappa=10 / 3, beta=0.5):
    hcf = 10**log10_A * (f / const.fyr) ** ((3 - gamma) / 2) / (1 + (10**lf0 / f) ** kappa) ** beta
    return hcf**2 / 12 / np.pi**2 / f**3


def t_process(f, log10_A=-15, gamma=4.33, alphas=None):
    """
    t-process model. PSD  amplitude at each frequency
    is a fuzzy power-law.
    """
    alphas = np.ones_like(f) if alphas is None else np.repeat(alphas, 2)
    return powerlaw(f, log10_A=log10_A, gamma=gamma) * alphas


def t_process_adapt(f, log10_A=-15, gamma=4.33, alphas_adapt=None, nfreq=None):
    """
    t-process model. PSD  amplitude at each frequency
    is a fuzzy power-law.
    """
    if alphas_adapt is None:
        alpha_model = np.ones_like(f)
    else:
        if nfreq is None:
            alpha_model = np.repeat(alphas_adapt, 2)
        else:
            alpha_model = np.ones_like(f)
            alpha_model[2 * int(np.rint(nfreq))] = alphas_adapt
            alpha_model[2 * int(np.rint(nfreq)) + 1] = alphas_adapt

    return powerlaw(f, log10_A=log10_A, gamma=gamma) * alpha_model


def turnover_knee(f, log10_A, gamma, lfb, lfk, kappa, delta):
    """
    Generic turnover spectrum with a high-frequency knee.
    :param f: sampling frequencies of GWB
    :param A: characteristic strain amplitude at f=1/yr
    :param gamma: negative slope of PSD around f=1/yr (usually 13/3)
    :param lfb: log10 transition frequency at which environment dominates GWs
    :param lfk: log10 knee frequency due to population finiteness
    :param kappa: smoothness of turnover (10/3 for 3-body stellar scattering)
    :param delta: slope at higher frequencies
    """
    hcf = (
        10**log10_A
        * (f / const.fyr) ** ((3 - gamma) / 2)
        * (1.0 + (f / 10**lfk)) ** delta
        / np.sqrt(1 + (10**lfb / f) ** kappa)
    )
    return hcf**2 / 12 / np.pi**2 / f**3


def broken_powerlaw(f, log10_A, gamma, delta, log10_fb, kappa=0.1):
    """
    Generic broken powerlaw spectrum.
    :param f: sampling frequencies
    :param A: characteristic strain amplitude [set for gamma at f=1/yr]
    :param gamma: negative slope of PSD for f > f_break [set for comparison
        at f=1/yr (default 13/3)]
    :param delta: slope for frequencies < f_break
    :param log10_fb: log10 transition frequency at which slope switches from
        gamma to delta
    :param kappa: smoothness of transition (Default = 0.1)
    """
    hcf = (
        10**log10_A
        * (f / const.fyr) ** ((3 - gamma) / 2)
        * (1 + (f / 10**log10_fb) ** (1 / kappa)) ** (kappa * (gamma - delta) / 2)
    )
    return hcf**2 / 12 / np.pi**2 / f**3