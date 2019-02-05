import sys
from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

packages = ["serial","threading","tkinter", "os", "numpy","struct","serial.tools.list_ports","matplotlib.pyplot","matplotlib","cv2", "pandas"]
build_exe_options = {'include_files':[os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'), os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll')], "packages":packages }


base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "MesureTempsDeReponse",
        version = "0.1",
        description = "tameroshika",
        options = {"build_exe": build_exe_options},
        executables = [Executable("tdr.py", base=base)])
        
        
#### Pour l'utiliser : ExeScript.py build #####