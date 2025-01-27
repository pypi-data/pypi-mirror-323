from ..scf.hf import SCF
from .rks import Grids

class UKS(SCF):
    _keys = {
        'xc', 'nlc', 'disp', 'grids', 'nlcgrids', 'small_rho_cutoff',
    }

    _methods = ['gpu4pyscf.dft.UKS']

    def __init__(self, mol, xc='lda,vwn'):
        SCF.__init__(self, mol)
        self.xc = xc
        self.grids = Grids()
        self.nlcgrids = Grids()
