from .._future import SubOptions

def density_fit(mf, auxbasis=None):
    class DFHF(mf.__class__):
        _keys = {'with_df'}
        _methods = mf.__class__._methods + ['.density_fit']

        def to_cpu(self):
            return super().to_cpu().density_fit()

    new_mf = object.__new__(DFHF)
    new_mf.__dict__.update(mf.__dict__)
    new_mf.with_df = DF()
    if auxbasis is not None:
        new_mf.with_df.auxbasis = auxbasis
    return new_mf

class DF(SubOptions):
    _keys = {'auxbasis'}
