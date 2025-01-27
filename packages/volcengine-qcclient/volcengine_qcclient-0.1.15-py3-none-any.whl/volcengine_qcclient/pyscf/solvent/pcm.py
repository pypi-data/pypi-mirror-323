from .._future import SubOptions

def pcm_for_scf(mf):
    class PCM_SCF(mf.__class__):
        _keys = {'with_solvent'}
        _methods = mf.__class__._methods + ['gpu4pyscf.solvent.PCM']
        _return = {
            **mf.__class__._return,
            'solvent.e': 'with_solvent.e',
        }

        def to_cpu(self):
            return super().to_cpu().PCM()

    new_mf = object.__new__(PCM_SCF)
    new_mf.__dict__.update(mf.__dict__)
    new_mf.with_solvent = PCM()
    return new_mf

class PCM(SubOptions):
    _keys = {
        'method', 'vdw_scale', 'surface', 'lebedev_order', 'lmax', 'eta', 'eps',
        'max_cycle', 'conv_tol', 'frozen'
    }
