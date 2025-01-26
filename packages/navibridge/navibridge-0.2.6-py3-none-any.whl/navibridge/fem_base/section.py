from abc import ABCMeta
from typing import Tuple

from .base import ApdlWriteable


class Section:
    __slots__ = ('id', 'name', '_offset')
    __metaclass__ = ABCMeta

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float]):
        self.id = Id
        self.name = Name
        self._offset = offset

    def __cmp__(self, other: "Section"):
        """compare two Section
        negative if self <  other;
        zero     if self == other;
        positive if self >  other;
        """
        return self.id - other.id

    def set_offset(self, x=0, y=0):
        self._offset = (x, y)

    @property
    def offset(self):
        return self._offset


class ShellSection(Section, ApdlWriteable):
    """
    Shell截面
    """

    __slots__ = ('thickness',)

    thickness: float

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float], th: float):
        super().__init__(Id, Name, offset)
        self.thickness = th

    @property
    def apdl_str(self):
        cmd_str = ''' 
! Shell截面
sect,%i,shell,,%s
secdata, %.5f,1,0.0,3  
secoffset,user,%.5f  
seccontrol,,,, , , ,''' % (self.id, self.name, self.thickness, self._offset[1])
        return cmd_str

    def __str__(self):
        st = "%i : %s : (" % (self.id, self.name)
        for key in self.__slots__:
            st += "%.3f," % getattr(self, key)
        st += ")"
        return st


class ISection(Section, ApdlWriteable):
    """
    I型梁截面
    """

    __slots__ = ('w1', 'w2', 'w3', 't1', 't2', 't3')

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float], **kwargs):
        super().__init__(Id, Name, offset)
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, value)

    def __str__(self):
        st = "%i : %s : (" % (self.id, self.name)
        for key in self.__slots__:
            st += "%.3f," % getattr(self, key)
        st += ")"
        return st

    @property
    def mct_str(self):
        cmd = (f" {self.id}, DBUSER, {self.name}   , CC, 0, 0, 0, 0, 0, 0, YES, NO,"
               + f"H  , 2, {self.w3}, {self.w2}, {self.t3}, {self.t2}, {self.w1}, {self.t1}, 0, 0, 0, 0\n")
        return cmd

    @property
    def apdl_str(self):
        if self._offset[0] == 0 and self._offset[1] == 0:
            cmd_str = '''
! I型梁截面
sect,  %i, BEAM, I, %s, 0   
SECOFFSET, CENT 
secdata,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0,0,0,0,0,0''' % (
                self.id, self.name,
                self.w1, self.w2, self.w3, self.t1, self.t2, self.t3)
        else:
            cmd_str = '''
! I型梁截面
sect,  %i, BEAM, I, %s, 0   
secoffset, user, %f, %f 
secdata,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0,0,0,0,0,0''' % (
                self.id, self.name, self._offset[0], self._offset[1],
                self.w1, self.w2, self.w3, self.t1, self.t2, self.t3)
        return cmd_str

    @property
    def yg(self):
        h = self.w3 - self.t1 - self.t2
        a1 = self.t1 * self.w1
        a3 = self.t3 * h
        a2 = self.t2 * self.w2
        y1 = 0.5 * self.t1
        y3 = self.t1 + 0.5 * h
        y2 = self.w3 - self.t2 * 0.5
        y0 = (y1 * a1 + y2 * a2 + y3 * a3) / self.area
        return y0

    @property
    def area(self):
        return self.w1 * self.t1 + self.w2 * self.t2 + (self.w3 - self.t1 - self.t2) * self.t3

    @property
    def inertia(self):
        h = self.w3 - self.t1 - self.t2
        a1 = self.t1 * self.w1
        a3 = self.t3 * h
        a2 = self.t2 * self.w2
        y1 = 0.5 * self.t1
        y3 = self.t1 + 0.5 * h
        y2 = self.w3 - self.t2 * 0.5
        y0 = (y1 * a1 + y2 * a2 + y3 * a3) / self.area
        i1 = self.t1 ** 3 * self.w1 / 12 + a1 * (y0 - y1) ** 2
        i2 = self.t2 ** 3 * self.w2 / 12 + a2 * (y0 - y2) ** 2
        i3 = self.t3 * h ** 3 / 12 + a3 * (y0 - y3) ** 2
        i = i1 + i2 + i3
        return i


class BoxSection(Section):
    __slots__ = ('w1', 'w2', 't1', 't2', 't3', 't4')

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float], w1: float, w2: float, t1: float, t2: float, t3: float, t4: float):
        super().__init__(Id, Name, offset)
        self.w1 = w1
        self.w2 = w2
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.t4 = t4

    @property
    def apdl_str(self):
        cmd_str = f'''
sectype, {self.id}, BEAM, HREC, {self.name}, 0
SECOFFSET, cent
secdata, {self.w1}, {self.w2}, {self.t1}, {self.t2}, {self.t3}, {self.t4}, 0, 0, 0, 0, 0, 0
'''
        return cmd_str

    @property
    def mct_str(self):
        cmd = f" {self.id}, DBUSER    , {self.name}  , CC, 0, 0, 0, 0, 0, 0, YES, NO, B  ,2, {self.w2}, {self.w1}, {self.t3}, {self.t1}, 0, 0, 0, 0, 0, 0\n"
        return cmd


class TubeSection(Section):
    __slots__ = ('diameter', 'thickness')

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float], d: float, t: float):
        super().__init__(Id, Name, offset)
        self.diameter = d
        self.thickness = t

    @property
    def apdl_str(self):
        ro = 0.5 * self.diameter
        ri = ro - self.thickness
        cmd_str = f'''
sectype, {self.id}, BEAM, CTUBE, {self.name}, 0
SECOFFSET, cent
secdata, {ri}, {ro}, 12,0,0,0,0,0,0,0,0,0
'''
        return cmd_str

    @property
    def mct_str(self):
        cmd = f' {self.id}, DBUSER , {self.name} , CC, 0, 0, 0, 0, 0, 0, YES, NO, P  , 2, {self.diameter}, {self.thickness}, 0, 0, 0, 0, 0, 0, 0, 0\n'
        return cmd
