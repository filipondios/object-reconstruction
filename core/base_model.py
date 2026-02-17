from abc import abstractmethod
from tabulate import tabulate
from core.base_view import BaseView
from pathlib import Path
import warnings


class BaseModel:

    views: list[BaseView]
    path: str
    bounds: tuple[float, float, float, float, float, float]
    print_info: bool

    def __init__(self, path: str, print_info: bool, viewClass: BaseView):
        """" Initializes a Model, loading all the available views """
        self.views = [viewClass(f) for f in Path(path).iterdir() if f.is_dir()]
        self.print_info = print_info
        self.path = path

        # Display all the model data in a table format
        format = lambda p: f'({p[0]}, {p[1]}, {p[2]})'
        data = [[view.name, 
            format(view.origin),
            format(view.vx),
            format(view.vy),
            format(view.vz)]
            for view in self.views]

        headers = ['Name', 'Origin', 'Vx', 'Vy', 'Vz']
        table = tabulate(data, headers=headers, tablefmt="github")
        name = 'A model has been found at: %s' % self.path
        print(f'{name}.\nThe views found of the model are:\n{table}')

        # Calculate the 3D bounding box that contains the model
        # This is required for the model's rendering
        bounds = list(self.views[0].polygon.bounds)

        for view in self.views[1:]:
            view_bounds = view.polygon.bounds
            bounds[0] = min(bounds[0], view_bounds[0])
            bounds[1] = min(bounds[1], view_bounds[1])
            bounds[2] = max(bounds[2], view_bounds[2])
            bounds[3] = max(bounds[3], view_bounds[3])
        self.bounds = (bounds[0], bounds[2], bounds[1], bounds[3], bounds[1], bounds[3])

        # Model reconstruction process
        print('[+] Starting initial reconstruction')
        self.initial_reconstruction()
        print('[+] Refining model')
        self.refine_model()
        print('[+] Generating surface')
        self.generate_surface()

        # Print additional information if required
        if self.print_info: self.additional_info()
       

    @abstractmethod
    def initial_reconstruction(self) -> None:
        """ Must generate a first version of the model """
        warnings.warn('This method has to be implemented')


    @abstractmethod
    def refine_model(self) -> None:
        """ Must generate a more accurate version of the model """
        warnings.warn('This method has to be implemented')


    @abstractmethod
    def generate_surface(self) -> None:
        """ Must generate some 'visual' surface for the model """
        warnings.warn('This method has to be implemented')


    @abstractmethod
    def draw_model(self) -> None:
        """ Must draw the model in a 3D space """
        warnings.warn('This method has to be implemented')


    @abstractmethod
    def additional_info(self) -> None:
        """ Must print some additional information about the model """
        warnings.warn('This method has to be implemented')