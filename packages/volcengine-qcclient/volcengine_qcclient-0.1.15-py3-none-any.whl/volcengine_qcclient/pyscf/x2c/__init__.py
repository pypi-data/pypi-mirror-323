from .._future import SubOptions

def x2c(mf):
    class X2CHF(mf.__class__):
        _keys = {'with_x2c'}
        _methods = mf.__class__._methods + ['.x2c']

        def to_cpu(self):
            return super().to_cpu().x2c()

    new_mf = object.__new__(X2CHF)
    new_mf.__dict__.update(mf.__dict__)
    new_mf.with_x2c = X2CHelper()
    return new_mf

class X2CHelper(SubOptions):
    _keys = {'approx', 'xuncontract', 'basis'}
