import numpy as np

from ..result import Result
from .geweke_test import burnInBySequentialGeweke
from .auto_correlation import auto_correlation


def GewekeTest(result: Result,
               zscore: float = 2.):
    ''' Calculates the burn-in of MCMC chains.

    Parameters
    ----------
    result:
        The pyPESTO result object with filled sample result.
    zscore:
        The Geweke test threshold. Default 2.

    Returns
    -------
    burn_in:
        Iteration where the first and the last fraction of the chain
        do not differ significantly regarding Geweke test -> Burn-In

    '''
    # Get parameter samples as numpy arrays
    chain = np.array(result.sample_result['trace_x'][0])

    # Calculate burn in index
    burn_in = burnInBySequentialGeweke(chain=chain,
                                       zscore=zscore)
    print('Geweke Burn-in index: '+str(burn_in))

    result.sample_result['burn_in'] = burn_in

    return result


def ChainAutoCorrelation(result: Result):
    ''' Calculates the auto-correlation of the MCMC samples.

    Parameters
    ----------
    result:
        The pyPESTO result object with filled sample result.

    Returns
    -------
    tau:
        Array with the auto-correlation time tau for each parameter
        dimension. We suggest taking the maximum over all components.

    '''

    # Burn in index
    burn_in = result.sample_result['burn_in']

    # Get parameter samples as numpy arrays
    # and discarding warm up phase
    chain = np.array(result.sample_result['trace_x'][0][burn_in:, :])

    # Calculate chain auto-correlation
    tau = auto_correlation(chain=chain)

    return tau


def EffectiveSampleSize(result: Result):
    ''' Calculates the effective sample size of the MCMC samples.

        Parameters
        ----------
        result:
            The pyPESTO result object with filled sample result.

        Returns
        -------
        ess:
            Effective sample size. The effective sample size
            is determined counting the remaining points after
            thinning the signal by tau.
        '''

    # Burn in index
    burn_in = result.sample_result['burn_in']

    # Get parameter samples as numpy arrays
    # and discarding warm up phase
    chain = np.array(result.sample_result['trace_x'][0][burn_in:, :])

    # Calculate chain auto-correlation
    tau = auto_correlation(chain=chain)
    # Take the maximum over all components.
    ac = np.max(tau)
    # Calculate effective sample size
    ess = chain.shape[0] / (1. + ac)

    return ess