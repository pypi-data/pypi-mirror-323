from .classes import *
class Cat:
    def __init__(self, catname, catcolor):
        self.catname = catname
        self.catcolor = catcolor

    def __str__(self):
        return f"name: {self.catname}, color: {self.catcolor}"

world = World()