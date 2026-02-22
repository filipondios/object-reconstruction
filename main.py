import importlib
import pkgutil
from pathlib import Path


def discover_algorithms():
    """ auto-discover all algorithms in 'algorithms' directory"""
    algorithms_path = Path('algorithms')
    algorithms = {}
    
    for _, name, ispkg in pkgutil.iter_modules([str(algorithms_path)]):
        if ispkg and not name.startswith('_'):
            try:
                module = importlib.import_module(f'algorithms.{name}')
                if hasattr(module, 'Model') and hasattr(module, 'ALGORITHM_NAME'):
                    algorithms[module.ALGORITHM_NAME] = {
                        'module': module,
                        'Model': module.Model,
                        'params': getattr(module, 'ALGORITHM_PARAMS', {})
                    }
            except Exception as e:
                print(f"[!] Failed to load algorithm '{name}': {e}")
    return algorithms


if __name__ == '__main__':
    
    import sys
    from argparse import ArgumentParser
    from core.model_render import ModelRender

    algorithms = discover_algorithms()
    if not algorithms: sys.exit('[!] No algorithms found!')

    # build program arguments, then parse the command line args
    parser = ArgumentParser(description='3D Object Reconstruction')
    parser.add_argument('-p', '--path', type=str, required=True, 
        help='Path of the model data to be reconstructed')
    parser.add_argument('-a', '--algorithm', type=str, required=True,
        help='Name of the reconstruction algorithm to use', 
        choices=list(algorithms.keys()))
    parser.add_argument('-i', '--info', action='store_true', 
        help='Print additional information')

    # add the arguments for all loaded algorithms
    for algo_name, algo_info in algorithms.items():
        for (param_name, param_config) in algo_info['params'].items():
            parser.add_argument(f'--{param_name}', type=param_config['type'],
                required=param_config.get('required', False),
                default=param_config.get('default'),
                help=f'[{algo_name}] ' + param_config.get('help', 'No available info'))
    args = parser.parse_args()

    # build kwargs from algorithm parameters
    model_kwargs = { 'path': args.path }
    for param_name in algo_info['params'].keys():
        value = getattr(args, param_name, None)
        if value is not None: model_kwargs[param_name] = value

    # instantiate the model and build
    ModelClass = algo_info['Model']
    model = ModelClass(**model_kwargs).initial_reconstruction(
        ).refine_model().generate_surface()    
    if args.info: model.additional_info()

    render = ModelRender(model)
    render.initialize()
    render.render_loop()