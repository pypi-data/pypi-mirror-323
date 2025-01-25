#                                                                       Modules
# =============================================================================

# Standard
from typing import Callable, Optional

# Third-party
import jax.numpy as jnp
import numpy as onp
import optax
from f3dasm import Block, ExperimentData

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class OptaxOptimizer(Block):
    require_gradients: bool = True

    @property
    def _seed(self) -> int:
        """
        Property to return the seed of the optimizer

        Returns
        -------
        int | None
            Seed of the optimizer

        Note
        ----
        If the seed is not set, the property will return None
        This is done to prevent errors when the seed is not an available
        attribute in a custom optimizer class.
        """
        return self.seed if hasattr(self, 'seed') else None

    @property
    def _population(self) -> int:
        """
        Property to return the population size of the optimizer

        Returns
        -------
        int
            Number of individuals in the population

        Note
        ----
        If the population is not set, the property will return 1
        This is done to prevent errors when the population size is not an
        available attribute in a custom optimizer class.
        """
        return self.population if hasattr(self, 'population') else 1

    def __init__(self, algorithm_cls, seed: Optional[int], **hyperparameters):
        self.algorithm_cls = algorithm_cls
        self.seed = seed
        self.hyperparameters = hyperparameters

    def arm(self, data: ExperimentData):
        # Set algorithm
        self.algorithm = self.algorithm_cls(**self.hyperparameters)

        # Set data
        x = data[-1].to_numpy()[0].ravel()

        self.opt_state = self.algorithm.init(jnp.array(x))

    def call(self, data: ExperimentData, grad_fn: Callable, **kwargs
             ) -> ExperimentData:
        # Set data
        x = data[-1].to_numpy()[0].ravel()

        def grad_f(params):
            return jnp.array(
                grad_fn(onp.array(params)))

        updates, self.opt_state = self.algorithm.update(
            grad_f(x), self.opt_state)
        new_x = optax.apply_updates(jnp.array(x), updates)
        new_x = jnp.clip(new_x, data.domain.get_bounds()[
            :, 0], data.domain.get_bounds()[:, 1])

        return type(data)(input_data=onp.atleast_2d(new_x),
                          domain=data.domain,
                          project_dir=data.project_dir)
