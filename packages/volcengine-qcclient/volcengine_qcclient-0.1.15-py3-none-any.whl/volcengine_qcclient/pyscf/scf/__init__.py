from .hf import RHF
from .uhf import UHF

__all__ = [
    'RHF', 'UHF',
    'load_or_run_scf'
]

def load_or_run_scf(mf):
    from .._future import create_methods_config
    if mf._task_id is None: # SCF not executed
        task_config = mf._build_task_config()
    else:
        task_config = mf._build_task_config()
        #TODO: Recover from previous jobs
        #task_config = create_methods_config(mf, with_return=False)
        #task_config = [
        #    Mole_to_task(mf.mol),
        #    *task_config,
        #    # FIXME: deserialization remotely
        #    {'method': 'update_from_chk', 'kwargs': mf._task_id + '.chk'}
        #]
    return task_config
