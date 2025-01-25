#                                                                       Modules
# =============================================================================

# Standard

from ._imports import try_import

with try_import() as _evosax_imports:
    from .evosax_optimizers import cmaes, de, pso, simanneal

with try_import() as _nevergrad_imports:
    from .nevergrad_optimizers import de_nevergrad, pso_nevergrad

with try_import() as _optuna_imports:
    from .optuna_optimizers import tpe_sampler

with try_import() as _optax_imports:
    from .optax_optimizers import adam, sgd

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================


def optimizers_extension():
    optimizer_list = []

    if _optuna_imports.is_successful():
        optimizer_list.extend([tpe_sampler])

    if _evosax_imports.is_successful():
        optimizer_list.extend([cmaes, de, pso, simanneal])

    if _nevergrad_imports.is_successful():
        optimizer_list.extend([de_nevergrad, pso_nevergrad])

    if _optax_imports.is_successful():
        optimizer_list.extend([adam, sgd])

    return optimizer_list


__all__ = [
    'adam',
    'cmaes',
    'de',
    'de_nevergrad',
    'pso',
    'pso_nevergrad',
    'sgd',
    'simanneal',
    'tpe_sampler',
]
