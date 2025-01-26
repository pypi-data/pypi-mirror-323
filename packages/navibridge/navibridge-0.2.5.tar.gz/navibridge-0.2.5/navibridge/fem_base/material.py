from .base import ApdlWriteable


class Material(ApdlWriteable):
    __slots__ = ('id', 'ex', 'dens', 'alpx', 'nuxy', 'description')

    def __init__(self, id, ex, dens, alpx, nuxy, description: str = ''):
        self.id = id
        self.ex = ex
        self.dens = dens
        self.alpx = alpx
        self.nuxy = nuxy
        self.description = description

    @property
    def mct_str(self):
        cmd = f" {self.id}, USER , {self.description} , 0.06, 0, , C, NO, 0, 2, 2.0600e+005,"
        cmd += f"{self.nuxy}, {self.alpx}, {self.dens * 9806},     0"
        return cmd

    @property
    def apdl_str(self):
        cmd_str = '''
!%s
MP,EX,  %i,%.4e
MP,DENS,%i,%.4e
MP,ALPX,%i,%.4e
MP,NUXY,%i,%.1f''' % (self.description,
                      self.id, self.ex,
                      self.id, self.dens,
                      self.id, self.alpx,
                      self.id, self.nuxy
                      )
        return cmd_str
