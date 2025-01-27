def newton(mf):
    class SOSCF(mf.__class__):
        _methods = mf.__class__._methods + ['.newton']

        def to_cpu(self):
            return super().to_cpu()

    new_mf = object.__new__(SOSCF)
    new_mf.__dict__.update(mf.__dict__)
    return new_mf
