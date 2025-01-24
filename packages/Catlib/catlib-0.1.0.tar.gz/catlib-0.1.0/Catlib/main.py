from .vars import *
class Cat:
    def __init__(self, catname, catcolor):
        self.catname = catname
        self.catcolor = catcolor

    def __str__(self):
        return f"name: {self.catname}, color: {self.catcolor}"

class World:
    def __init__(self):
        self.animals = []

    def addcat(self, cat):
        self.animals.append(cat)

    def getcat(self, name):
        for i in range(len(self.animals)):
            if self.animals[i].catname == name:
                return self.animals[i]
        return None

    def deletecat(self, cat_name):
        for i in range(len(self.animals)):
            if self.animals[i].catname == cat_name:
                del self.animals[i]
                return

world = World()