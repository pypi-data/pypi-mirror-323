#                                                                       Modules
# =============================================================================

# Standard
from typing import Optional

# Third-party
import nevergrad as ng
from f3dasm import Block

# Local
from .adapters.nevergrad_implementations import NeverGradOptimizer

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


def de_nevergrad(population: int = 30,
                 initialization: str = 'parametrization',
                 scale: float = 1.0,
                 recommendation: str = 'optimistic',
                 crossover: float = 0.5,
                 F1: float = 0.8,
                 F2: float = 0.8,
                 seed: Optional[int] = None,
                 **kwargs) -> Block:
    """
    Nevergrad Differential Evolution (DE) optimizer.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    initialization : str, optional
        Initialization strategy, by default 'parametrization'
    scale : float, optional
        Scale factor, by default 1.0
    recommendation : str, optional
        Recommendation strategy, by default 'optimistic'
    crossover : float, optional
        Crossover probability, by default 0.5
    F1 : float, optional
        First differential weight, by default 0.8
    F2 : float, optional
        Second differential weight, by default 0.8
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object.
    """
    return NeverGradOptimizer(
        algorithm_cls=ng.optimizers.DifferentialEvolution,
        population=population,
        seed=seed,
        initialization=initialization,
        scale=scale,
        recommendation=recommendation,
        crossover=crossover,
        F1=F1,
        F2=F2,
        **kwargs
    )
# =============================================================================


def pso_nevergrad(
    population: int = 30,
        transform: str = 'identity',
        omega: float = 0.7213475204444817,
        phip: float = 1.1931471805599454,
        phig: float = 1.1931471805599454,
        qo: bool = False,
        sqo: bool = False,
        seed: Optional[int] = None,
        so: bool = False, **kwargs) -> Block:
    """
    Nevergrad Particle Swarm Optimization (PSO) optimizer.

    Parameters
    ----------
    population : int, optional
        The number of individuals in the population, by default 30
    transform : str, optional
        Transform strategy, by default 'identity'
    omega : float, optional
        Inertia weight, by default 0.7213475204444817
    phip : float, optional
        Personal attraction coefficient, by default 1.1931471805599454
    phig : float, optional
        Global attraction coefficient, by default 1.1931471805599454
    qo : bool, optional
        Use quasi-opposition, by default False
    sqo : bool, optional
        Use stochastic quasi-opposition, by default False
    so : bool, optional
        Use space opposition, by default False
    seed : Optional[int], optional
        The seed for the random number generator, by default None

    Returns
    -------
    Optimizer
        Optimizer object.
    """
    return NeverGradOptimizer(
        algorithm_cls=ng.optimizers.ConfPSO,
        population=population,
        seed=seed,
        transform=transform,
        omega=omega,
        phip=phip,
        phig=phig,
        qo=qo,
        sqo=sqo,
        so=so,
        **kwargs
    )
