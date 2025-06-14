from abc import abstractmethod
from tabulate import tabulate
from core.base_view import BaseView
from pathlib import Path


class BaseModel:

    views: list[BaseView]
    path: str

    def __init__(self, path: str, viewClass: BaseView):
        """" Initializes a Model, loading all the available views """
        self.views = [viewClass(f) for f in Path(path).iterdir() if f.is_dir()]
        self.path = path
        print(self)


    @abstractmethod
    def initial_reconstruction(self, args=None) -> None:
        """ Must generate a first version of the model """
        print('TODO: This method has to be implemented')
        pass


    @abstractmethod
    def refine_model(self) -> None:
        """ Must generate a more accurate version of the model """
        print('TODO: This method has to be implemented')
        pass


    @abstractmethod
    def generate_surface(self) -> None:
        """ Must generate some 'visual' surface for the model """
        print('TODO: This method has to be implemented')
        pass


    @abstractmethod
    def draw_model(self) -> None:
        """ Must draw the model in a 3D space """
        print('TODO: This method has to be implemented')
        pass


    def __str__(self) -> str:
        """ Displays all the model data in a table format. """
        fmt = lambda p: f"({p.x}, {p.y}, {p.z})"
        data = [[view.name, 
            fmt(view.origin),
            fmt(view.vx),
            fmt(view.vy),
            fmt(view.vz)]
            for view in self.views]
        headers = ['Name', 'Origin', 'Vx', 'Vy', 'Vz']
        table = tabulate(data, headers=headers, tablefmt="github")
        name = 'A model has been found at: %s' % self.path
        return '%s.\nThe views found of the model are:\n%s' % (name, table)