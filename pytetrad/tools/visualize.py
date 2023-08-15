
def graphs_to_probs(graphs):
    probs = {}
    reverse = {"---": "---", "o-o": "o-o", "o--": "--o",
               "--o": "o--", "<--": "-->", "-->": "<--",
               "<-o": "o->", "o->": "<-o", "<->": "<->"}

    for graph in graphs:
        for edge in graph.getEdges():
            edge = str(edge).split()

            if edge[0] < edge[2]:
                key = (edge[0], edge[2])
                arr = edge[1]
            else:
                key = (edge[2], edge[0])
                arr = reverse[edge[1]]

            if key not in probs: probs[key] = {}
            if arr not in probs[key]: probs[key][arr] = 0

            probs[key][arr] += 1.0 / len(graphs)
    return probs


def write_gdot(gdot, probs, threshold=0, weight=1, length=1, power=1, hidden=lambda pair: False):
    for node in set([key[0] for key in probs] + [key[1] for key in probs]):
        gdot.node(node,
                  shape="circle",
                  fixedsize="true",
                  weight=f"{weight}",
                  style="filled",
                  color="lightgray",
                  stroke="transparent")

    for pair in probs:
        if hidden(pair): continue
        adj = round(sum([probs[pair][edge] for edge in probs[pair]]))
        if adj < threshold: continue

        for edge in probs[pair]:
            marks = ["none", "none"]
            prob = round(probs[pair][edge], 3)

            if edge[0] == "o": marks[0] = "odot"
            if edge[2] == "o": marks[1] = "odot"
            if edge[0] == "<": marks[0] = "empty"
            if edge[2] == ">": marks[1] = "empty"

            intensity = 1.0 - prob ** power
            alpha = hex(int(255 * intensity))[2:]
            if len(alpha) == 1: alpha = "0" + alpha
            if marks[0] == "empty" and marks[1] == "empty": color = "#ff" + 2 * alpha
            else: color = "#" + 2 * alpha + "ff"

            gdot.edge(pair[0], pair[1],
                      arrowhead=marks[1],
                      arrowtail=marks[0],
                      dir="both",
                      len=f"{length}",
                      color=color)

    return gdot
