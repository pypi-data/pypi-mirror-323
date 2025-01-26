from ezdxf.math import Vec3

from .base import ApdlWriteable


class Node(ApdlWriteable):
    __slots__ = ('id', 'x', 'y', 'z', 'vec')

    def __init__(self, n: int, *args):
        self.id = n
        args_list = list(args)
        if len(args_list) == 3:
            self.vec: Vec3 = Vec3(args_list)
            self.x = float(args_list[0])
            self.y = float(args_list[1])
            self.z = float(args_list[2])
        elif len(args_list) == 1:
            self.vec: Vec3 = args_list[0]
            self.x = self.vec.x
            self.y = self.vec.y
            self.z = self.vec.z
        else:
            raise ValueError

    @property
    def apdl_str(self):
        cmd_str = "n,%i,%.3f,%.3f,%.3f" % (self.id, self.x, self.z, self.y)
        return cmd_str

    def __str__(self):
        return "Node: (%i,%.3f,%.3f,%.3f)" % (self.id, self.x, self.y, self.z)

    def distance(self, other: 'Node'):
        return self.vec.distance(other.vec)

    def copy(self, dn: int = 0, x0: float = 0, y0: float = 0, z0: float = 0):
        return Node(self.n + dn, self.x + x0, self.y + y0, self.z + z0)

    def __eq__(self, other: 'Node'):
        return self.n == other.n

    def __ne__(self, other: 'Node'):
        return self.n != other.n

    def __gt__(self, other: 'Node'):
        return self.n > other.n

    def __lt__(self, other: 'Node'):
        return self.n < other.n

    def __ge__(self, other: 'Node'):
        return self.n >= other.n

    def __le__(self, other: 'Node'):
        return self.n <= other.n


if __name__ == '__main__':
    n1 = Node(1, 1, 1, 1)
