from .base import ApdlWriteable


class Fix(ApdlWriteable):
    __slots__ = ('id', 'fix_dict')

    def __init__(self, idx, f_dict):
        self.id = idx
        self.fix_dict = f_dict

    @property
    def apdl_str(self):
        cmd_str = ""
        for key in self.fix_dict.keys():
            cmd_str += "d,%i,%s,%i\n" % (self.id, key, self.fix_dict[key])
        return cmd_str

    @property
    def mct_str(self):
        if 'all' in self.fix_dict.keys():
            cmd = f"{self.id},111111,\n"
        else:
            ux = 1 if 'Ux' in self.fix_dict.keys() else 0
            uy = 1 if 'Uy' in self.fix_dict.keys() else 0
            uz = 1 if 'Uz' in self.fix_dict.keys() else 0
            rx = 1 if 'Rx' in self.fix_dict.keys() else 0
            ry = 1 if 'Ry' in self.fix_dict.keys() else 0
            rz = 1 if 'Rz' in self.fix_dict.keys() else 0
            cmd = f"{self.id},{ux}{uy}{uz}{rx}{ry}{rz},\n"
        return cmd
