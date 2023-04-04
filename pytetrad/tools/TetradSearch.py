## Provides a simple wrapper for many of the Tetrad searches.

import jpype
import jpype.imports

try:
    jpype.startJVM(classpath=[f"resources/tetrad-gui-current-launch.jar"])
except OSError:
    pass
    # print("JVM already started")

import tools.translate as tr
import tools.search as search
import edu.cmu.tetrad.search as ts
import edu.cmu.tetrad.data as td


class TetradSearch:

    def __init__(self):
        self.score = None
        self.test = None
        self.verbose = False
        self.knowledge = td.Knowledge()

    def use_sem_bic(self, data, penalty_discount = 2):
        data_ = tr.pandas_data_to_tetrad(data)
        score = ts.SemBicScore(data_)
        score.setPenaltyDiscount(penalty_discount)
        self.score = score

    def add_to_tier(self, tier, *var_names):
        for s in var_names:
            self.knowledge.addToTier(tier, s)

    def add_fobidden(self, var_name_1, var_name_2):
        self.knowledge.addForbidden(var_name_1, var_name_2)

    def add_required(self, var_name_1, var_name_2):
        self.knowledge.addRequired(var_name_1, var_name_2)

    def clear_knowledge(self):
        self.knowledge.clear()

    def set_verbose(self, verbose):
        self.verbose = verbose

    def run_fges(self):
        pattern = search.fges(self.score, self.knowledge, verbose=self.verbose)
        return tr.tetrad_graph_to_pcalg(pattern)
