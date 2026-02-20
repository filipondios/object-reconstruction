from .model import Model

ALGORITHM_NAME = 'simple'
ALGORITHM_PARAMS = {
    'resolution': {
        'type': int,
        'required': False,
        'default': 16,
        'help': 'Voxel space resolution. Higher resolution leads to more accurate results.'
    }
}