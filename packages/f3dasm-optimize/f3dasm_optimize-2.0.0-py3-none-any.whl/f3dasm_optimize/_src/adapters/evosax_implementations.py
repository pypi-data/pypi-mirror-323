#                                                                       Modules
# =============================================================================

# Standard
from typing import Optional, Type

# Third-party
import jax
import numpy as np
from evosax import Strategy
from f3dasm import Block, ExperimentData

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class EvoSaxOptimizer(Block):
    type: str = 'evosax'
    require_gradients: bool = False

    def __init__(self, algorithm_cls: Type[Strategy], population: int,
                 seed: Optional[int], **hyperparameters):

        if seed is None:
            seed = np.random.default_rng().integers(1e6)

        self.algorithm_cls = algorithm_cls
        self.population = population
        self.seed = seed
        self.hyperparameters = hyperparameters

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

    def arm(self, data: ExperimentData):
        self.algorithm: Strategy = self.algorithm_cls(num_dims=len(
            data.domain), popsize=self.population, **self.hyperparameters)

        # Set algorithm
        _, rng_ask = jax.random.split(
            jax.random.PRNGKey(self.seed))
        self.evosax_param = self.algorithm.default_params
        self.evosax_param = self.evosax_param.replace(
            clip_min=data.domain.get_bounds()[
                0, 0], clip_max=data.domain.get_bounds()[0, 1])

        self.state = self.algorithm.initialize(
            rng_ask, self.evosax_param)

    def call(self, data: ExperimentData, **kwargs) -> ExperimentData:
        _, rng_ask = jax.random.split(
            jax.random.PRNGKey(self.seed))

        # Get the last candidates
        x_i, y_i = data[-self.population:].to_numpy()

        # Tell the last candidates
        self.state = self.algorithm.tell(
            x_i, y_i.ravel(), self.state, self.evosax_param)

        # Ask for a set candidates
        x, state = self.algorithm.ask(
            rng_ask, self.state, self.evosax_param)

        return type(data)(
            input_data=np.array(x),
            domain=data.domain,
            project_dir=data.project_dir)
