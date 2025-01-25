#                                                                       Modules
# =============================================================================

# Local
from .__version__ import __version__
from ._src import optimizers_extension
from ._src._imports import try_import

with try_import() as _evosax_imports:
    from ._src.evosax_optimizers import cmaes, de, pso, simanneal

with try_import() as _nevergrad_imports:
    from ._src.nevergrad_optimizers import de_nevergrad, pso_nevergrad

with try_import() as _optuna_imports:
    from ._src.optuna_optimizers import tpe_sampler


with try_import() as _optax_imports:
    from ._src.optax_optimizers import adam, sgd

#                                                          Authorship & Credits
# =============================================================================
__author__ = 'Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)'
__credits__ = ['Martin van der Schelling']
__status__ = 'Stable'
# =============================================================================
#
# =============================================================================

__all__ = [
    'optimizers_extension',
    'adam',
    'cmaes',
    'de',
    'de_nevergrad',
    'pso',
    'pso_nevergrad',
    'sgd',
    'simanneal',
    'tpe_sampler',
    '__version__',
]
