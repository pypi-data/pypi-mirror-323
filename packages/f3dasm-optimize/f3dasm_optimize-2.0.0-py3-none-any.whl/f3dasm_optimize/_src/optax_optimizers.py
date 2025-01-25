#                                                                       Modules
# =============================================================================

# Third-party
from typing import Optional

import optax
from f3dasm import Block

# Local
from .adapters.optax_implementations import OptaxOptimizer

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


def adam(learning_rate: float = 0.001, beta_1: float = 0.9,
         beta_2: float = 0.999, epsilon: float = 1e-07, eps_root: float = 0.0,
         seed: Optional[int] = None, **kwargs) -> Block:
    """
    Adam optimizer.
    Adapted from the Optax library.

    Parameters
    ----------
    learning_rate : float, optional
        The learning rate, by default 0.001.
    beta_1 : float, optional
        Exponential decay rate for the first moment estimates, by default 0.9.
    beta_2 : float, optional
        Exponential decay rate for the second moment estimates,
        by default 0.999.
    epsilon : float, optional
        A small constant for numerical stability, by default 1e-07.
    eps_root : float, optional
        A small constant for numerical stability, by default 0.0.
    seed : int, optional
        Random seed, by default None.

    Returns
    -------
    Optimizer
        Optimizer object.
    """

    return OptaxOptimizer(
        algorithm_cls=optax.adam,
        seed=seed,
        learning_rate=learning_rate,
        b1=beta_1,
        b2=beta_2,
        eps=epsilon,
        eps_root=eps_root,
        **kwargs
    )


# =============================================================================


def sgd(learning_rate: float = 0.01, momentum: float = 0.0,
        nesterov: bool = False, seed: Optional[int] = None, **kwargs
        ) -> Block:
    """
    Stochastic Gradient Descent (SGD) optimizer.
    Adapted from the Optax library.

    Parameters
    ----------
    learning_rate : float, optional
        The learning rate, by default 0.01.
    momentum : float, optional
        Momentum parameter, by default 0.0.
    nesterov : bool, optional
        Use Nesterov momentum, by default False.
    seed : int, optional
        Random seed, by default None.

    Returns
    -------
    Optimizer
        Optimizer object.
    """

    return OptaxOptimizer(
        algorithm_cls=optax.sgd,
        seed=seed,
        learning_rate=learning_rate,
        momentum=momentum,
        nesterov=nesterov,
        **kwargs
    )

# =============================================================================
