
from enum import StrEnum


class ForceDirectedMethod(StrEnum):
    """
   The method to compute the layout. If ‘force’, the force-directed Fruchterman-Reingold algorithm
   is used. If ‘energy’, the energy-based optimization algorithm  is used with absolute values of
   edge weights and gravitational forces acting on each connected component.
   If ‘auto’,the algorithm uses  ‘force’ if the graph has less than 500 nodes, Above
   500 the algorithm uses the 'energy’ method
    """
    AUTO    = 'auto'
    FORCE   = 'force'
    ENERGY  = 'energy'
    NOT_SET = 'Not Set'
