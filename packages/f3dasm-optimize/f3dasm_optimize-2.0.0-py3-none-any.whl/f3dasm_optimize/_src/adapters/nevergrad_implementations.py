#                                                                       Modules
# =============================================================================

# Standard
from typing import Optional

# Third-party
import autograd.numpy as np
import nevergrad as ng
from f3dasm import Block, ExperimentData

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


class NeverGradOptimizer(Block):
    require_gradients: bool = False

    def __init__(self, algorithm_cls, population: int,
                 seed: Optional[int] = None,
                 **hyperparameters):
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
        p = ng.p.Array(shape=(len(data.domain),),
                       lower=data.domain.get_bounds()[:, 0],
                       upper=data.domain.get_bounds()[:, 1],
                       )

        p._set_random_state(np.random.RandomState(self.seed))

        self.algorithm = self.algorithm_cls(
            popsize=self.population,
            **self.hyperparameters)(p, budget=1e8)

    def call(self, data: ExperimentData, **kwargs) -> ExperimentData:

        # Get the last candidates
        xx, yy = data[-self.population:].to_numpy()

        for x_tell, y_tell in zip(xx, yy):
            self.algorithm.tell(
                self.algorithm.parametrization.spawn_child(x_tell), y_tell)

        x = [self.algorithm.ask() for _ in range(
            self.population)]

        return type(data)(input_data=np.vstack([x_.value for x_ in x]),
                          domain=data.domain,
                          project_dir=data.project_dir)
