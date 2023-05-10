from cag.graph_elements.nodes import GenericOOSNode, Field


class Movie(GenericOOSNode):
    """
    A class representing a movie node in a graph.

    Attributes:
        _name (str): The name of the movie node.
        _fields (dict): A dictionary containing the fields and their respective types for the movie node.

    """

    _name = "Movie"
    _fields = {
        "name": Field(),
        "year": Field(),
        "genre": Field(),
        "description": Field(),
        **GenericOOSNode._fields,
    }


class Person(GenericOOSNode):
    """
    A class representing a person node in a graph.

    Attributes:
        _fields (dict): A dictionary containing the fields and their respective types for the person node.

    """

    _fields = {"name": Field(), "birthdate": Field(), **GenericOOSNode._fields}


class Actor(Person):
    """
    A class representing an actor node in a graph.

    Inherits from Person class.
    """

    ...


class Director(Person):
    """
    A class representing a director node in a graph.

    Inherits from Person class.
    """

    ...
