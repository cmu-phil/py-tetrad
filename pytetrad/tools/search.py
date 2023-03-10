import jpype
import jpype.imports

try:
    # jpype.startJVM(classpath=[f"resources/tetrad-gui-7.2.2-launch.jar"])
    jpype.startJVM(classpath=[f"resources/tetrad-gui-bugfix-launch.jar"])
except OSError:
    print("JVM already started")

from .translate import tetrad_to_pandas
import edu.cmu.tetrad.search as ts

def return_graph(graph, out):
    if out=='tetrad':
        return graph
    elif out =='pcalg':
        return tetrad_to_pandas(graph)

def fges(score, verbose=False, out='tetrad'):
    fges = ts.Fges(score)
    fges.setVerbose(verbose)
    pattern = fges.search()
    return return_graph(pattern, out)

def boss(score, verbose=False, out='tetrad'):
    test = ts.IndTestScore(score, score.getData())
    boss = ts.Boss(test, score)
    boss.setUseDataOrder(False)
    boss.setNumStarts(5)
    boss.bestOrder(score.getVariables())
    boss.setVerbose(verbose)
    pattern = boss.getGraph(True)
    return return_graph(pattern, out)

def grasp(score, verbose=False, out='tetrad'):
    test = ts.IndTestScore(score, score.getData())
    grasp = ts.Grasp(test, score)
    grasp.setOrdered(False)
    grasp.setUseDataOrder(False)
    grasp.setNumStarts(5)
    grasp.bestOrder(score.getVariables())
    grasp.setVerbose(verbose)
    pattern = grasp.getGraph(True)
    return return_graph(pattern, out)

