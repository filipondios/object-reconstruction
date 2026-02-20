from .model import Model

ALGORITHM_NAME = 'complex'
ALGORITHM_PARAMS = {
    'step': {
        'type': float,
        'required': False,
        'default': 1.0,
        'help': 'Separation between segmentation lines. Lower values mean higher precission.'
    }
}