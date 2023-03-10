import jpype
import jpype.imports

try:
    # jpype.startJVM(classpath=[f"resources/tetrad-gui-7.2.2-launch.jar"])
    jpype.startJVM(classpath=[f"resources/tetrad-gui-bugfix-launch.jar"])
except OSError:
    print("JVM already started")

from .translate import tetrad_to_pandas
import edu.cmu.tetrad.search as ts
import java.util as util

## Some functions wrapping various classes in Tetrad. Feel free to just steal
## the relevant code for your own projects, or call these functions. We
## will add more named parameters to help one see which methods for the
## the searches can be controlled.

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

def gango(score, data, verbose=False, out='tetrad'):
    fges_graph = fges(score, verbose)
    datasets = util.ArrayList()
    datasets.add(data)
    rskew = ts.Lofs2(fges_graph, datasets)
    rskew.setRule(ts.Lofs2.Rule.RSkew)
    gango_graph = rskew.orient()
    return return_graph(gango_graph, out)

def pc(test, verbose=False, out='tetrad'):
    pc = ts.Pc(test)
    pc.setVerbose(verbose)
    pc_graph = pc.search()
    return return_graph(pc_graph, out)

def fci(test, verbose=False, out='tetrad'):
    fci = ts.Fci(test)
    fci.setVerbose(verbose)
    fci_graph = fci.search()
    return return_graph(fci_graph, out)

def gfci(test, score, verbose=False, out='tetrad'):
    gfci = ts.GFci(test, score)
    gfci.setVerbose(verbose)
    gfci_graph = gfci.search()
    return return_graph(gfci_graph, out)