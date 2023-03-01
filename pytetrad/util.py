import os
import sys

import jpype
import jpype.imports

def startJVM():
    BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(BASE_DIR)

    try:
        jpype.startJVM(classpath=[f"{BASE_DIR}/tetrad-gui-7.2.2-launch.jar"])
    except OSError:
        print("JVM already started")
