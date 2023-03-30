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

def fges(score, verbose=False, knowledge=None):
    fges = ts.Fges(score)
    if knowledge != None:
        fges.setKnowledge(knowledge)
    fges.setVerbose(verbose)
    pattern = fges.search()
    return pattern


def boss(score, depth=-1, num_starts=1, verbose=False):
    boss = ts.Boss(score)
    boss.setNumStarts(num_starts)
    alg = ts.PermutationSearch(ts.Boss(score))
    alg.setVerbose(verbose)
    pattern = alg.search()
    return pattern

def sp(score, depth=-1, num_starts=1, verbose=False):
    boss = ts.Boss(score)
    boss.setNumStarts(num_starts)
    alg = ts.PermutationSearch(ts.Sp(score))
    alg.setVerbose(verbose)
    pattern = alg.search()
    return pattern


def grasp(score, verbose=False, knowledge=None):
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
    return pattern


def gango(score, data, verb=False, knowledge=None):
    fges_graph = fges(score, verbose=verb, knowledge=knowledge)
    datasets = util.ArrayList()
    datasets.add(data)
    rskew = ts.Lofs2(fges_graph, datasets)
    if knowledge != None:
        rskew.setKnowledge(knowledge)
    rskew.setRule(ts.Lofs2.Rule.RSkew)
    gango_graph = rskew.orient()
    return gango_graph


def pc(test, depth=-1, prevent_cycles=True, knowledge=None, verbose=False):
    pc = ts.Pc(test)
    if knowledge != None:
        pc.setKnowledge(knowledge)
    pc.setDepth(depth)
    pc.setAggressivelyPreventCycles(prevent_cycles)
    pc.setVerbose(verbose)
    pc_graph = pc.search()
    return pc_graph


def fci(test, knowledge=None, verbose=False):
    fci = ts.Fci(test)
    if knowledge != None:
        fci.setKnowledge(knowledge)
    fci.setVerbose(verbose)
    fci_graph = fci.search()
    return fci_graph


def gfci(test, score, knowledge=None, verbose=False):
    gfci = ts.GFci(test, score)
    if knowledge != None:
        gfci.setKnowledge(knowledge)
    gfci.setVerbose(verbose)
    gfci_graph = gfci.search()
    return gfci_graph

def bfci(test, score, knowledge=None, verbose=False):
    bfci = ts.BFci(test, score)
    if knowledge != None:
        bfci.setKnowledge(knowledge)
    bfci.setVerbose(verbose)
    bfci_graph = bfci.search()
    return bfci_graph

def spfci(test, score, knowledge=None, verbose=False):
    spfci = ts.SpFci(test, score)
    if knowledge != None:
        spfci.setKnowledge(knowledge)
    spfci.setVerbose(verbose)
    sp_graph = spfci.search()
    return sp_graph

def grasp_fci(test, score, knowledge=None, verbose=False):
    grasp_fci = ts.GraspFci(test, score)
    if knowledge != None:
        grasp_fci.setKnowledge(knowledge)
    grasp_fci.setVerbose(verbose)
    grasp_fci_graph = grasp_fci.search()
    return grasp_fci_graph
