import pytetrad.tools.gregression as greg
import edu.cmu.tetrad.graph as tg

g = tg.EdgeListGraph()
n = {i: tg.GraphNode(f"X{i}") for i in range(1, 7)}
for node in n.values(): g.addNode(node)
for a, b in [(1, 2), (1, 3), (1, 4), (4, 5), (4, 6)]: g.addDirectedEdge(n[a], n[b])
for a, b in [(2, 3), (3, 4), (5, 6)]:                 g.addUndirectedEdge(n[a], n[b])

print(greg.mpdag_problem(g), greg.buckets(g))
for A in (["X2"], ["X4"], ["X2", "X4"], ["X2", "X3"], ["X3"]):
    print(A, "-> X5:", greg.is_identified(g, A, "X5"))

g2 = greg.orient_with_knowledge(g, required=[("X3", "X4")])
for A in (["X2"], ["X3"], ["X2", "X3"]):
    print("with 3->4:", A, "-> X5:", greg.is_identified(g2, A, "X5"))