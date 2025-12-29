from automate import *

def export_dot(a, name="automate.dot"):
    with open(name,"w") as f:
        f.write("digraph A {\nrankdir=LR;\n")
        f.write("start [shape=point]; start -> 0;\n")
        for q in range(a.n):
            shape = "doublecircle" if q in a.final else "circle"
            f.write(f"{q} [shape={shape}];\n")
        for (q,c),dests in a.transition.items():
            for d in dests:
                lbl = "ε" if c=="E" else c
                f.write(f"{q} -> {d} [label=\"{lbl}\"];\n")
        f.write("}\n")
