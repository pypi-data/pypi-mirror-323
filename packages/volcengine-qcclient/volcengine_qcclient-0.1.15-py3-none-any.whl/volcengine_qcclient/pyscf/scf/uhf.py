from .hf import SCF

class UHF(SCF):
    _methods = ['gpu4pyscf.scf.UHF']
