from argparse import ArgumentParser
from core.complex.model import Model as ComplexModel
from core.simple.model import Model as SimpleModel
from core.modelRender import ModelRender

if __name__ == "__main__":

    # Argument parsing (options)
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True, help='Model path.')
    parser.add_argument('-c', '--complexity', type=str, required=True, help='Reconstruction algorithm complexity. Options: complex, simple.')
    parser.add_argument('-s', '--step', type=float, required=False, help='Rasterization segments separation (Used in the complex algorithm).')
    args = parser.parse_args()


    # Build and render the model
    if args.complexity == 'complex':
        if args.step is None:
            step = 1
        else: step = args.step
        model = ComplexModel(args.path, step)

    elif args.complexity == 'simple':
        model = SimpleModel(args.path)

    render = ModelRender(model)
    render.initialize()
    render.render_loop()