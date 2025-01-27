from ..scf.hf import SCF
from .._future import SubOptions

class RKS(SCF):
    _keys = {
        'xc', 'nlc', 'disp', 'grids', 'nlcgrids', 'small_rho_cutoff',
    }

    _methods = ['gpu4pyscf.dft.RKS']

    def __init__(self, mol, xc='lda,vwn'):
        SCF.__init__(self, mol)
        self.xc = xc
        self.grids = Grids()
        self.nlcgrids = Grids()

class Grids(SubOptions):
    _keys = {'atomic_radii', 'prune', 'level'}
