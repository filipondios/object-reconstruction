if __name__ == '__main__':

    # Print startup information
    file = open('config/startup.txt', 'r')
    print(file.read())

    from argparse import ArgumentParser
    from algorithms.complex.model import Model as ComplexModel
    from algorithms.simple.model import Model as SimpleModel
    from core.model_render import ModelRender

    # Argument parsing (program options)
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', type=str, required=True, help='Model path.')
    parser.add_argument('-c', '--complexity', type=str, required=True, help='Reconstruction algorithm complexity. Options: complex, simple.')
    parser.add_argument('-s', '--step', type=float, required=False, help='Rasterization segments separation (Used in the complex algorithm).')
    parser.add_argument('-r', '--resolution', type=int, required=False, help='Voxel resolution (Used in the simple algorithm). Default: 8')
    parser.add_argument('-i', '--info', action='store_true', required=False, help='Print additional information about the model.')
    args = parser.parse_args()


    if args.complexity == 'complex':
        # Polygon implementation
        if args.step is None:
            step = 1
        else: step = args.step
        model = ComplexModel(args.path, args.info, step)

    elif args.complexity == 'simple':
        # Voxels implementation
        if args.resolution is None:
            resolution = 8
        else: resolution = args.resolution
        model = SimpleModel(args.path, args.info, resolution)

    render = ModelRender(model)
    render.initialize()
    render.render_loop()
