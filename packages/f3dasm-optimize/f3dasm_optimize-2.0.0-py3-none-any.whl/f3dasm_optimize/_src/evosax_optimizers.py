#                                                                       Modules
# =============================================================================

# Standard
from typing import Optional

# Third-party
from evosax import BIPOP_CMA_ES, CMA_ES, DE, PSO, SimAnneal
from f3dasm import Block

# Local
from .adapters.evosax_implementations import EvoSaxOptimizer

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


def cmaes(population: int = 30,
          seed: Optional[int] = None, **kwargs) -> Block:
    """
    Covariance Matrix Adaptation Evolution Strategy (CMA-ES) optimizer.
    Adapated from the EvoSax library.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object
    """
    return EvoSaxOptimizer(
        algorithm_cls=CMA_ES,
        population=population,
        seed=seed,
        **kwargs)

# =============================================================================


def pso(population: int = 30,
        seed: Optional[int] = None, **kwargs) -> Block:
    """
    Particle Swarm Optimization (PSO) optimizer.
    Adapted from the EvoSax library.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object
    """
    return EvoSaxOptimizer(
        algorithm_cls=PSO,
        population=population,
        seed=seed,
        **kwargs)

# =============================================================================


def simanneal(population: int = 30,
              seed: Optional[int] = None, **kwargs) -> Block:
    """
    Simulated Annealing (SimAnneal) optimizer.
    Adapted from the EvoSax library.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object
    """
    return EvoSaxOptimizer(
        algorithm_cls=SimAnneal,
        population=population,
        seed=seed,
        **kwargs)

# =============================================================================


def de(population: int = 30,
       seed: Optional[int] = None, **kwargs) -> Block:
    """
    Differential Evolution (DE) optimizer.
    Adapted from the EvoSax library.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object
    """
    return EvoSaxOptimizer(
        algorithm_cls=DE,
        population=population,
        seed=seed,
        **kwargs)

# =============================================================================


def bipopcmaes(population: int = 30,
               seed: Optional[int] = None, **kwargs) -> Block:
    """
    BIPOP-CMA-ES optimizer.
    Adapted from the EvoSax library.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object
    """
    return EvoSaxOptimizer(
        algorithm_cls=BIPOP_CMA_ES,
        population=population,
        seed=seed,
        **kwargs)

# =============================================================================
