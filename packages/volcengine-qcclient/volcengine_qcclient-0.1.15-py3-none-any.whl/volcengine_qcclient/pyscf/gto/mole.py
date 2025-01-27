from .._future import SubOptions, InputError

class Mole(SubOptions):
    _keys = {
        'verbose', 'unit', 'max_memory', 'cart', 'charge', 'spin', 'symmetry',
        'symmetry_subgroup', 'atom', 'basis', 'nucmod', 'ecp', 'pseudo',
        'groupname', 'topgroup', 'a', 'mesh'
    }

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def _build_task_config(self):
        attrs = self.__dict__
        input_keys = self._keys.intersection(attrs)
        if len(attrs) != len(input_keys):
            unknown = set(attrs).difference(self._keys)
            raise ValueError(f'Unsupported attributes {unknown}')

        kwargs = {k: attrs[k] for k in input_keys}
        if 'atom' not in kwargs:
            raise InputError('Molecule geometry not specified')
        return {
            'method': 'pyscf.M',
            'kwargs': kwargs
        }

    def build(self):
        return self

    def RHF(self):
        from volcengine_qcclient.pyscf.scf import RHF
        return RHF(self)

    def ROHF(self):
        raise NotImplementedError

    def UHF(self):
        from volcengine_qcclient.pyscf.scf import UHF
        return UHF(self)

    def RKS(self, **kwargs):
        from volcengine_qcclient.pyscf.dft import RKS
        return RKS(self, **kwargs)

    def ROKS(self):
        raise NotImplementedError

    def UKS(self, **kwargs):
        from volcengine_qcclient.pyscf.dft import UKS
        return UKS(self, **kwargs)
