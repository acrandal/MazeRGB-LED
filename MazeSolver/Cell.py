# Single cell of the maze (x,y) coordinate

class Cell:
    def __init__(self, x, y, distance):
        self._x = x
        self._y = y
        self._distance = distance
        self._visited = False

    def __eq__(self, other):
        if (isinstance(other, Cell)):
            return self._distance == other._distance
        return False

    def __repr__(self):
        return f'({self._x},{self._y}) @ {self._distance}'

    def __lt__(self, other):
        return self._distance < other._distance

    def __str__(self):
        return f"({self._x},{self._y}) - dist = {self._distance} | visited: {self._visited})"
