#                                                                       Modules
# =============================================================================

# Third party
import optuna
from f3dasm import Block, ExperimentData, ExperimentSample
from f3dasm.design import Domain

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================

optuna.logging.set_verbosity(optuna.logging.WARNING)


class OptunaOptimizer(Block):
    require_gradients: bool = False

    def __init__(self, algorithm_cls, seed: int, **hyperparameters):
        self.algorithm_cls = algorithm_cls
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
        self.distributions = domain_to_optuna_distributions(
            data.domain)

        # Set algorithm
        self.algorithm = optuna.create_study(
            sampler=self.algorithm_cls(seed=self.seed, **self.hyperparameters)
        )

        for _, es in data:
            self.algorithm.add_trial(
                optuna.trial.create_trial(
                    params=es.input_data,
                    distributions=self.distributions,
                    value=es.to_numpy()[1],
                )
            )

    def call(self, data: ExperimentData, **kwargs) -> ExperimentData:
        for _, es in data[-1]:
            self.algorithm.add_trial(
                optuna.trial.create_trial(
                    params=es.input_data,
                    distributions=self.distributions,
                    value=es.to_numpy()[1],
                )
            )
        trial = self.algorithm.ask()
        new_es = self._suggest_experimentsample(
            trial=trial, domain=data.domain)
        return type(data).from_data(data={0: new_es},
                                    domain=data.domain,
                                    project_dir=data.project_dir)

    def _suggest_experimentsample(self, trial: optuna.Trial, domain: Domain
                                  ) -> ExperimentSample:
        optuna_dict = {}
        for name, parameter in domain.input_space.items():
            if parameter._type == 'float':
                optuna_dict[name] = trial.suggest_float(
                    name=name,
                    low=parameter.lower_bound,
                    high=parameter.upper_bound, log=parameter.log)
            elif parameter._type == 'int':
                optuna_dict[name] = trial.suggest_int(
                    name=name,
                    low=parameter.lower_bound,
                    high=parameter.upper_bound, step=parameter.step)
            elif parameter._type == 'category':
                optuna_dict[name] = trial.suggest_categorical(
                    name=name,
                    choices=parameter.categories)
            elif parameter._type == 'object':
                optuna_dict[name] = trial.suggest_categorical(
                    name=name, choices=[parameter.value])

        return ExperimentSample(input_data=optuna_dict,
                                domain=domain)


def domain_to_optuna_distributions(domain: Domain) -> dict:
    optuna_distributions = {}
    for name, parameter in domain.input_space.items():
        if parameter._type == 'float':
            optuna_distributions[
                name] = optuna.distributions.FloatDistribution(
                low=parameter.lower_bound,
                high=parameter.upper_bound, log=parameter.log)
        elif parameter._type == 'int':
            optuna_distributions[
                name] = optuna.distributions.IntDistribution(
                low=parameter.lower_bound,
                high=parameter.upper_bound, step=parameter.step)
        elif parameter._type == 'category':
            optuna_distributions[
                name] = optuna.distributions.CategoricalDistribution(
                parameter.categories)
        elif parameter._type == 'object':
            optuna_distributions[
                name] = optuna.distributions.CategoricalDistribution(
                choices=[parameter.value])
    return optuna_distributions
