from argparse import ArgumentParser
from core.complex.model import Model as ComplexModel
from core.simple.model import Model as SimpleModel
from core.model_render import ModelRender

if __name__ == '__main__':

    # Argument parsing (program options)
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True, help='Model path.')
    parser.add_argument('-c', '--complexity', type=str, required=True, help='Reconstruction algorithm complexity. Options: complex, simple.')
    parser.add_argument('-s', '--step', type=float, required=False, help='Rasterization segments separation (Used in the complex algorithm).')
    parser.add_argument('-r', '--resolution', type=int, required=False, help='Voxel resolution (Used in the simple algorithm). Default: 8')
    args = parser.parse_args()


    if args.complexity == 'complex':
        # Polygon implementation
        if args.step is None:
            step = 1
        else: step = args.step
        model = ComplexModel(args.path, step)

    elif args.complexity == 'simple':
        # Voxels implementation
        if args.resolution is None:
            resolution = 8
        else: resolution = args.resolution
        model = SimpleModel(args.path, resolution)

    render = ModelRender(model)
    render.initialize()
    render.render_loop()
