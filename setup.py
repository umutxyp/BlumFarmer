from cx_Freeze import setup, Executable
import os
import sys

if getattr(sys, 'frozen', False):
    root_path = sys._MEIPASS
else:
    root_path = os.path.dirname(os.path.abspath(__file__))

setup(
    name="BlumAutoClicker",
    version="0.1",
    description="A description of your script",
    executables=[Executable("main.py")],
    options={
        'build_exe': {
            'packages': ['comtypes'],
            'include_files': [
                (os.path.join(root_path, 'assets'), 'assets'),
                (os.path.join(root_path, 'utility'), 'utility'),
                (os.path.join(root_path, 'gui'), 'gui')
            ]
        }
    }
)
