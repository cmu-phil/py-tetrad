import jpype
import jpype.imports
import pandas as pd

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    print("JVM already started")

from .translate import tetrad_graph_to_pcalg, tetrad_graph_to_causal_learn
import edu.cmu.tetrad.search as ts
import java.util as util

from edu.cmu.tetrad.util import Params, Parameters


## Some functions wrapping various classes in Tetrad. Feel free to just steal
## the relevant code for your own projects, or call these functions. We
## will add more named parameters to help one see which methods for the
## the searches can be controlled.

def return_graph(graph, out):
    if out == 'tetrad':
        return graph
    elif out == 'pcalg':
        return tetrad_graph_to_pcalg(graph)
    elif out == 'cl':
        return tetrad_graph_to_causal_learn(graph)
    else:
        raise Exception("Graph type must be tetrad (default), pcalg, or cl (causal-learn)")


def fges(score, verbose=False, knowledge=None, out='tetrad'):
    fges = ts.Fges(score)
    if knowledge != None:
        fges.setKnowledge(knowledge)
    fges.setVerbose(verbose)
    pattern = fges.search()
    return return_graph(pattern, out)


def boss(score, depth=-1, num_starts=1, verbose=False, out='tetrad'):
    boss = ts.Boss(score)
    boss.setNumStarts(num_starts)
    alg = ts.PermutationSearch(ts.Boss(score))
    alg.setVerbose(verbose)
    pattern = alg.search()
    return return_graph(pattern, out)


def grasp(score, verbose=False, knowledge=None, out='tetrad'):
    # _test = ts.IndTestScore(score)
    grasp = ts.Grasp(score)
    grasp.setOrdered(False)
    grasp.setUseDataOrder(False)
    grasp.setNumStarts(5)
    grasp.bestOrder(score.getVariables())
    if knowledge != None:
        grasp.setKnowledge(knowledge)
    grasp.setVerbose(verbose)
    pattern = grasp.getGraph(True)
    return return_graph(pattern, out)


def gango(score, data, verb=False, knowledge=None, out='tetrad'):
    fges_graph = fges(score, verbose=verb, knowledge=knowledge)
    datasets = util.ArrayList()
    datasets.add(data)
    rskew = ts.Lofs2(fges_graph, datasets)
    if knowledge != None:
        rskew.setKnowledge(knowledge)
    rskew.setRule(ts.Lofs2.Rule.RSkew)
    gango_graph = rskew.orient()
    return return_graph(gango_graph, out)


def pc(test, depth=-1, prevent_cycles=True, knowledge=None, verbose=False, out='tetrad'):
    pc = ts.Pc(test)
    if knowledge != None:
        pc.setKnowledge(knowledge)
    pc.setDepth(depth)
    pc.setAggressivelyPreventCycles(prevent_cycles)
    pc.setVerbose(verbose)
    pc_graph = pc.search()

    # Putting this version of PC here because it's the one that's used
    # in the interface and in Causal Command.
    # params = Parameters()

    return return_graph(pc_graph, out)


def fci(test, knowledge=None, verbose=False, out='tetrad'):
    fci = ts.Fci(test)
    if knowledge != None:
        fci.setKnowledge(knowledge)
    fci.setVerbose(verbose)
    fci_graph = fci.search()
    return return_graph(fci_graph, out)


def gfci(test, score, knowledge=None, verbose=False, out='tetrad'):
    gfci = ts.GFci(test, score)
    if knowledge != None:
        gfci.setKnowledge(knowledge)
    gfci.setVerbose(verbose)
    gfci_graph = gfci.search()
    return return_graph(gfci_graph, out)

def bfci(test, score, knowledge=None, verbose=False, out='tetrad'):
    bfci = ts.BFci(test, score)
    if knowledge != None:
        bfci.setKnowledge(knowledge)
    bfci.setVerbose(verbose)
    bfci_graph = bfci.search()
    return return_graph(bfci_graph, out)

def grasp_fci(test, score, knowledge=None, verbose=False, out='tetrad'):
    grasp_fci = ts.GraspFci(test, score)
    if knowledge != None:
        grasp_fci.setKnowledge(knowledge)
    grasp_fci.setVerbose(verbose)
    grasp_fci_graph = grasp_fci.search()
    return return_graph(grasp_fci_graph, out)
