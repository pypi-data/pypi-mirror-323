import json
import os
import shutil
import subprocess

import numpy as np

from .base_api import BaseAPI
from .wind_calculation import getFg, GetUd
from .ansys_tools import GetCd, GetSmax, GetDES
from ..zoo import FEM


class AnsysAPI(BaseAPI):
    def __init__(self, project, root_path, init=True):
        # self.cwd = ""
        super().__init__(project, root_path, init)
        wdr = os.path.join(root_path, self.project_name)
        if init:
            if not os.path.exists(wdr):
                os.mkdir(wdr)
            else:
                shutil.rmtree(wdr)
                os.mkdir(wdr)

    def _batch_file(self, filestream, jobname):
        cmd = rf'''set ANS_CONSEC=YES
set ANSYS_PATH="{self.options['ANSYS_PATH']}"
%ANSYS_PATH% -b -i {jobname}.inp -o {jobname}.out'''
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _apdl_main(self, filestream):
        cmd = f'''!=======================================================
! Modeled by Bill with Python Automation 2024
! Units: N,mm,t,s
!=======================================================
finish
/CLEAR,NOSTART
/TITLE,{self.project_name}
/input,Etype,inp
/input,Material,inp
/input,Section,inp
/input,Node,inp
/input,Element,inp
/input,Boundary,inp
/prep7 
nsel,all
nummrg,node,1
allsel
save,fem,db
finish
'''
        if self.options['image']:
            cmd += "/input,render,inp\n"

        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    @staticmethod
    def _apdl_list_out(filestream, prep_dict):
        cmd = "/prep7\n"
        for k in prep_dict.keys():
            val = prep_dict[k]
            cmd += val.apdl_str
        with open(filestream, 'w+', encoding='gbk') as fid:
            fid.write(cmd)

    @staticmethod
    def _apdl_etype(filestream):
        cmd = "/prep7"
        cmd += '''! 单元        
et,188,BEAM188
keyopt,188,1,1 
keyopt,188,3,2
et,1840,MPC184,1
et,1841,MPC184,1
'''
        with open(filestream, 'w+', encoding='utf-8') as fid:
            fid.write(cmd)

    def _apdl_node(self, filestream):
        fem = self.fem
        cmd = "/prep7\n"
        for n in fem.node_list.keys():
            cmd += fem.node_list[n].apdl_str
            cmd += "\n"
        cmd += "n,9999999,0,1e15,0\n"
        cmd += "n,8888888,0,0,1e15\n"
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _apdl_dead_load(self, filestream):
        cmd = '''!-------------------------------------------------------
! DC
!-------------------------------------------------------
/solu
ACEL,0,9800,0
antype,0
solve
finish
'''
        with open(filestream, 'w+') as fid:
            fid.write(cmd)
            fid.write(self.write_etab(1, 'DC_SE1'))
            fid.write(self.write_etab(11, 'DC_SE11'))

    def _apdl_elem(self, filestream):
        fem = self.fem
        cmd = "/prep7\n"
        for e in fem.elem_list.keys():
            cmd += fem.elem_list[e].apdl_str
            if fem.elem_list[e].secn in [11, 12, 21, 22]:
                cmd += '9999999'
            cmd += "\n"
        # cmd += "esel,s,secn,,2\n"
        # cmd += "cm,girder,elem\n"
        # cmd += "nsle,s,1\n"
        # cmd += "nsel,u,node,,999999\n"
        # cmd += "cm,gnode,node\n"
        # cmd += "allsel\n"
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    @staticmethod
    def _apdl_render(filestream):
        cmd = f'''/SHOW,png,,
/DEVICE,PNG
/VIEW,1,0,0,1       
/ANG,1,X,90         
/ERASE              
/PREP7
/ESHAPE,1    
/PBC,ALL, ,1       
EPLOT               
/SHOW,CLOSE         
/DEVICE,CLOSE'''
        with open(filestream, 'w+', encoding='utf-8') as fid:
            fid.write(cmd)

    def run_fem(self, fem_model: FEM):
        self.fem = fem_model
        self._apdl_etype(os.path.join(self.cwd, 'etype.inp'))
        self._apdl_list_out(os.path.join(self.cwd, 'Material.inp'), fem_model.mat_list)
        self._apdl_list_out(os.path.join(self.cwd, 'Section.inp'), fem_model.sect_list)
        self._apdl_node(os.path.join(self.cwd, 'Node.inp'))
        self._apdl_elem(os.path.join(self.cwd, 'Element.inp'), )
        self._apdl_list_out(os.path.join(self.cwd, 'Boundary.inp'), fem_model.fix_list)
        self._apdl_render(os.path.join(str(self.cwd), 'render.inp'))
        self._apdl_main(os.path.join(str(self.cwd), 'main.inp'))
        self._batch_file(os.path.join(self.cwd, 'run.bat'), 'main')
        if not self.options['only_cmd']:
            subprocess.call(os.path.join(self.cwd, 'run.bat'), shell=True, cwd=self.cwd,
                            stdout=subprocess.DEVNULL,  # 抑制标准输出
                            stderr=subprocess.DEVNULL  # 抑制标准错误输出
                            )
            # print(f'{self.project_name}')

    def _run_ansys(self, bat_file):
        subprocess.call(os.path.join(self.cwd, bat_file), shell=True, cwd=self.cwd,
                        stdout=subprocess.DEVNULL,  # 抑制标准输出
                        stderr=subprocess.DEVNULL  # 抑制标准错误输出
                        )
        # print(bat_file)

    @staticmethod
    def write_etab(secn, tab_name, set_id='Last'):
        cmd = f'''/post1
    set,{set_id}
    esel,s,secn,,{secn}
    ETABLE, {tab_name}, SMISC, 31
    PRETAB,{tab_name}   
    finish
    '''
        return cmd

    def run_rs(self, case_name, lcn, direction, Ci, Cs, A, Tg, dr=0.03):
        """
        写入反应谱计算结果
        """
        Cd0 = GetCd(0.03)
        Smax_x = GetSmax(Ci, Cs, Cd0, A)
        T, DES_x = GetDES(Smax_x, Tg, 0.1, 10, 0.1)
        Freq = 1 / np.array(T)
        Acc = np.array(DES_x) * 9806
        Freq = np.flip(Freq)
        Acc = np.flip(Acc)
        sfreq = ["%.5f" % a for a in Freq]
        sacel = ["%.5f" % a for a in Acc]
        if direction == "X":
            sdir = '1,0,0'
        elif direction == "Y":
            sdir = '0,1,0'
        else:
            sdir = '0,0,1'
        cmd = f'''/clear,nostart 
!/FILNAME,mode,0
/solution
resume,mode,db    
antype,8               
SPOPT,SPRS,,1,1
dmprat,0.03                
grp,0.001                   
svtyp,2   
sed,{sdir}
'''
        for line in str2lines(sfreq, 9):
            cmd += "FREQ," + line + '\n'
        for line in str2lines(sacel, 9):
            cmd += "SV,%.2f," % dr + line + '\n'
        cmd += f'''
solve 
finish 
/post1
/input,file,mcom
set,last
lcdef,1
lcwrite,{lcn}
'''
        with open(os.path.join(self.cwd, f'rs_{case_name}.inp'), 'w+', encoding='utf-8') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'run_{case_name}.bat'), f'rs_{case_name}')
            self._run_ansys(f'run_{case_name}.bat')

    def run_mode(self, nmode: int):
        cmd = f'''/clear,nostart 
!/filename,model,0
/solution
resume,fem,db
ANTYPE,2
MODOPT,LANB,{nmode}  
EQSLV,SPAR  
MXPAND,{nmode}  , , ,1 
LUMPM,0 
PSTRES,0
MODOPT,LANB,{nmode}  ,0,0, ,OFF
SOLVE   
save,mode,db    
FINISH  '''
        with open(os.path.join(self.cwd, 'model.inp'), 'w+', encoding='utf-8') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, 'run_model.bat'), 'model')
            self._run_ansys('run_model.bat')
            with open(os.path.join(self.cwd, 'model.out'), 'r') as fid:
                lines = fid.readlines()
            idx = []
            for jj, l in enumerate(lines):
                if l.__contains__("   TOTAL MASS"):
                    with open(self.res_dir, 'a+') as fid:
                        fid.write("\n" + str(float(l.split()[-1])))
                if l.startswith("   sum                        "):
                    idx.append(jj)
                if l.startswith("  MODE    FREQUENCY (HERTZ)  "):
                    idx.append(jj)
                    idx.append(jj + 3)
            with open(self.res_dir, 'a+') as fid:
                fid.write("\n" + lines[idx[0]])
                fid.write(lines[idx[1]])
                fid.write(lines[idx[-1]])
            return

    def run_deadload(self, lcn=1):
        cmd = f'''/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,9800,0
allsel
solve
save,dc,db   
finish
/post1
set,last
lcdef,1
lcwrite,{lcn}
        '''
        with open(os.path.join(self.cwd, 'dc.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, 'run_dc.bat'), 'dc')
            self._run_ansys('run_dc.bat')

    def run_dw(self, f2=1.6, lcn=2):
        cmd = f'''/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,0,0
esel,s,secn,,11
sfbeam,all,2,pres,-{f2 * 0.5}
allsel
solve
finish
/post1
set,last
lcdef,1
lcwrite,{lcn}
            '''
        with open(os.path.join(self.cwd, 'dw.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, 'run_dw.bat'), 'dw')
            self._run_ansys('run_dw.bat')

    def run_rq(self, rq, lcn):
        cmd = f'''/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,0,0
esel,s,secn,,11
sfbeam,all,2,pres,-{rq * 0.5}
allsel
solve
finish
/post1
set,last
lcdef,1
lcwrite,{lcn}
                '''
        with open(os.path.join(self.cwd, 'rq.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, 'run_rq.bat'), 'rq')
            self._run_ansys('run_rq.bat')

    def run_wind(self, case_name, wind_speed, tower_locs, tower_z0, truss_z0, truss_height, lcn):
        cmd = '''/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,0,0
'''
        Ud = GetUd(wind_speed, truss_z0, 0.785, 1, 0.22).m
        Fg = getFg(1.2, Ud, 0.55, truss_height).m * 1e-3  # N/mm
        cmd += f'''esel,s,secn,,11
esel,r,cent,z,-10000,0
sfbeam,all,2,pres,-{Fg}
'''
        sps = np.mean([tower_locs[i + 1] - tower_locs[i] for i in range(len(tower_locs) - 1)])
        for tx, tz in zip(tower_locs, tower_z0):
            Ud = GetUd(wind_speed, tz, 0.785, 1, 0.22).m
            Fg = getFg(1.2, Ud, 0.55, truss_height).m * 1e-3  # N/mm
            cmd += f"esel,s,secn,,1\n"
            cmd += f"esel,r,cent,z,-10000,0\n"
            cmd += f"esel,r,cent,x,{tx - 0.5 * sps},{tx + 0.5 * sps}\n"
            cmd += f"sfbeam,all,1,pres,-{Fg}\n"
        cmd += f'''allsel
solve
save,wind_{case_name},db   
finish
/post1
set,last
lcdef,2
lcwrite,{lcn}
'''
        with open(os.path.join(self.cwd, f'wind_{case_name}.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'run_wind_{case_name}.bat'), f'wind_{case_name}')
            self._run_ansys(f'run_wind_{case_name}.bat')

    def get_node_deformation(self, config: dict):
        cmd = f'''/clear,nostart 
/post1
resume,fem,db
'''
        for key in config.keys():
            lc = config[key][0]
            direction = config[key][1]
            var_name = config[key][2]
            cmd += f'''
lcfile,{lc}
lcoper,zero
FORCE,STATIC 
lcase,{lc}
NSORT, U, {direction}, 0, 1,3
*GET, {var_name}, SORT, 0, Max
'''

        with open(os.path.join(self.cwd, 'nodel_def.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, 'nodel_def.bat'), 'nodel_def')
            self._run_ansys('nodel_def.bat')
            with open(os.path.join(self.cwd, 'nodel_def.out'), 'r') as fid:
                lines = fid.readlines()
            res = {}
            for key in config.keys():
                var_name = config[key][2]
                for line in lines:
                    if line.__contains__(f"{var_name.upper()}") and line.__contains__(" *GET"):
                        vals = line.split()
                        res[key] = float(vals[-1])
            with open(self.res_dir, 'a+') as fid:
                fid.write(json.dumps(res, ensure_ascii=False, indent=4))
            return

    def get_elem_forces(self, secn, lcn):
        cmd = f'''
/clear,nostart 
/post1
resume,fem,db   
lcfile,{lcn}
esel,s,secn,,{secn}
lcoper,zero
FORCE,STATIC 
lcase,{lcn}
ETABLE, sxx, SMISC, 31
ETABLE, syT, SMISC, 32
ETABLE, syB, SMISC, 33
ETABLE, szT, SMISC, 34
ETABLE, szB, SMISC, 35
sadd,sTT,sxx,syT
sadd,sTT,sTT,szT
sadd,sTB,sxx,syT
sadd,sTB,sTB,szB
sadd,sBB,sxx,syB
sadd,sBB,sBB,szB
sadd,sBT,sxx,syB
sadd,sBT,sBT,szT
SMAX,smaxT,sTT,sTB
SMAX,smaxB,sBT,sBB
SMAX,smax,smaxT,smaxB
SMIN,sminT,sTT,sTB
SMIN,sminB,sBT,sBB
SMIN,smin,sminT,sminB
ESORT, ETAB, smin, 1,0,1
ESORT, ETAB, smax, 0,0,1
PRETAB, smin, smax
'''
        with open(os.path.join(self.cwd, f'ET_{secn}_{lcn}.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'et_{secn}_{lcn}.bat'), f'et_{secn}_{lcn}')
            self._run_ansys(f'et_{secn}_{lcn}.bat')
            with open(os.path.join(self.cwd, f'et_{secn}_{lcn}.out'), 'r') as fid:
                lines = fid.readlines()
            res = {}
            for ii, line in enumerate(lines):
                if line.__contains__(" MINIMUM VALUES"):
                    vals = [float(a) for a in lines[ii + 2].split()[-2:]]
                    res[f'{lcn}_{secn}_min'] = vals[0]
                    res[f'{lcn}_{secn}_max'] = vals[1]
            with open(self.res_dir, 'a+') as fid:
                fid.write('\n')
                fid.write(json.dumps(res, ensure_ascii=False, indent=4))
            return

    def srss_rs(self, case_name, lcn, lc_x, lc_y, lc_z):
        cmd = f'''/clear,nostart 
/post1
resume,fem,db    
lcfile,{lc_x}
lcfile,{lc_y}
lcfile,{lc_z}
lcoper,zero
FORCE,STATIC 
lcase,{lc_x}
lcoper,SQUA
LCOPER,ADD,{lc_y},MULT,{lc_y}
LCOPER,ADD,{lc_z},MULT,{lc_z}
LCOPER,SQRT
lcwrite,{lcn}
'''
        with open(os.path.join(self.cwd, f'{case_name}.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'run_{case_name}.bat'), case_name)
            self._run_ansys(f'run_{case_name}.bat')

    def run_lcomb(self, case_name, conf):
        cmd = ""
        for key in conf.keys():
            cmd += f'''/clear,nostart 
/post1
resume,fem,db    
'''
            lc = conf[key]
            for sub_lc, fct in lc:
                cmd += f"lcfile,{sub_lc}\n"
                cmd += f"lcfact,{sub_lc},{fct}\n"
            cmd += f''' 
lcoper,zero
FORCE,STATIC 
lcase,{lc[0][0]}
'''
            for sub_lc, fct in lc[1:]:
                cmd += f"lcoper,add,{sub_lc}\n"
            cmd += f"lcwrite,{key}\n"
        with open(os.path.join(self.cwd, f'{case_name}.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'run_{case_name}.bat'), case_name)
            self._run_ansys(f'run_{case_name}.bat')

    def run_tu(self, case_name, temp_up, temp_down, lcn):
        cmd = f'''/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,0,0
TUNIF, {temp_up}
allsel
solve
finish
/post1
set,last
lcdef,1
lcwrite,{lcn + 1}
/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,0,0
TUNIF, {temp_down}
allsel
solve
finish
/post1
set,last
lcdef,1
lcwrite,{lcn + 2}
'''
        with open(os.path.join(self.cwd, f'{case_name}.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'run_{case_name}.bat'), case_name)
            self._run_ansys(f'run_{case_name}.bat')

    def run_se(self, case_name, num_tower, val, lcn):
        fd = np.array(list(self.fem.fix_list.keys()))
        cmd = ""
        for i in range(num_tower):
            cmd += f'''/clear,nostart 
/solution
resume,fem,db
antype,0
ACEL,0,0,0
'''
            cur_n = fd[np.where(fd // 1e6 == (i + 1))]
            for n in cur_n:
                cmd += f"d,{n},uy,-{val}\n"
            cmd += f'''allsel
solve
finish
/post1
set,last
lcdef,1
lcwrite,{51 + i}
'''
        cmd += f'''/clear,nostart 
/post1
resume,fem,db   
'''
        for i in range(num_tower):
            cmd += f"lcfile,{51 + i}\n"
        cmd += '''lcoper,zero
FORCE,STATIC 
lcase,51
        '''
        for i in range(num_tower - 1):
            cmd += f"lcoper,ABM X,{52 + i}\n"
        cmd += f"lcwrite,{lcn}\n"
        with open(os.path.join(self.cwd, f'{case_name}.inp'), 'w+') as fid:
            fid.write(cmd)
        if not self.options['only_cmd']:
            self._batch_file(os.path.join(self.cwd, f'run_{case_name}.bat'), case_name)
            self._run_ansys(f'run_{case_name}.bat')

    def clear(self):
        if self.init:
            shutil.rmtree(self.cwd)
        pass

    def init_records(self, dimensions, loads):
        with open(self.res_dir, 'w+') as fid:
            json_string = json.dumps(dimensions, ensure_ascii=False, indent=4)
            fid.write(json_string)
            fid.write("\n")
            json_string = json.dumps(loads, ensure_ascii=False, indent=4)
            fid.write(json_string)


def str2lines(str_list, n):
    lines = [",".join(str_list[i:i + n]) for i in range(0, len(str_list), n)]
    return lines
