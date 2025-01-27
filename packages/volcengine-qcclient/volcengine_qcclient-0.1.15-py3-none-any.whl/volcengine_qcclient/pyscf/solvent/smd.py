from .._future import SubOptions

def smd_for_scf(mf):
    class SMD_SCF(mf.__class__):
        _keys = {'with_solvent'}
        _methods = mf.__class__._methods + ['gpu4pyscf.solvent.SMD']
        _return = {
            **mf.__class__._return,
            'solvent.e': 'with_solvent.e',
        }

        def to_cpu(self):
            return super().to_cpu().SMD()

    new_mf = object.__new__(SMD_SCF)
    new_mf.__dict__.update(mf.__dict__)
    new_mf.with_solvent = SMD()
    return new_mf

class SMD(SubOptions):
    _keys = {
        'method', 'solvent', 'r_probe', 'sasa_ng'
    }
