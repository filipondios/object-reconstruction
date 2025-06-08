from abc import abstractmethod
from tabulate import tabulate
from core.base_view import BaseView
from pathlib import Path


class BaseModel:

    views: list[BaseView]
    path: str

    def __init__(self, path: str, viewClass: BaseView):
        self.views = [viewClass(f) for f in Path(path).iterdir() if f.is_dir()]
        self.path = path
        print(self)

    @abstractmethod
    def initial_reconstruction(self, args=None):
        # Generate a first version of
        # the model using two views.
        pass

    @abstractmethod
    def refine_model(self):
        # Using the rest of views of 
        # the model, generate a more
        # accurate version of the 
        # model.
        pass

    @abstractmethod
    def generate_surface(self):
        # After all the steps above,
        # generate the surface of the
        # reconstructed object.
        pass

    @abstractmethod
    def draw_model(self):
        # Draw the model in a 3D space
        pass

    def __str__(self):
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