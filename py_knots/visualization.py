from braid import *
from matplotlib import pyplot as plt
from matplotlib import lines as lines
import sys


# Visualizes a braid
def visualize_braid(p: ColBraid) -> None:
    fig = plt.figure(figsize=(8, 6), dpi=100)
    x_scale = 1/(float(2*len(p.braid)+1))
    y_scale = 1/(float(p.strands+1))
    colors = ["b", "g", "r", "c", "m", "y", "k", "w"]
    vert = p.init_vert_perm

    # Adds a horizontal line
    def horizontal_line(x_1: float, x_2: float, y: float, col: str):
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_2)*x_scale],
            [(y)*y_scale, (y)*y_scale],
            color=col))

    # Adds a twist
    def twist(x_1: float, x_2: float, y_1: float, y_2: float,
            col1: str, col2: str):
        dy = y_2 - y_1
        dx = x_2 - x_1
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_2)*x_scale],
            [(y_1)*y_scale, (y_2)*y_scale],
            color=col1))
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_1 + dx/3.0)*x_scale],
            [(y_2)*y_scale, (y_2 - dy/3.0)*y_scale],
            color=col2))
        fig.add_artist(lines.Line2D(
            [(x_2 - dx/3.0)*x_scale, (x_2)*x_scale],
            [(y_1 + dy/3.0)*y_scale, (y_1)*y_scale],
            color=col2))

    for j in range(len(p.braid)):
        k = p.braid[j]
        for i in range(p.strands):
            if((abs(k)-1 != i) and (abs(k) != i)):  # Straight line
                horizontal_line(2*j, 2*j+2, i+0.5, colors[vert[i].col])

            elif((k>0) and (abs(k) == i+1)):  # Right handed twist
                # Straight lines
                horizontal_line(2*j, 2*j+1, i+0.5, colors[vert[i].col])
                horizontal_line(2*j, 2*j+1, i+1.5, colors[vert[i+1].col])
                # The actual twist
                twist(2*j+1, 2*j+2, i+0.5, i+1.5,
                    colors[vert[i].col], colors[vert[i+1].col])

            elif((k<0) and (abs(k) == i+1)):  # Left-handed twist
                # Straight lines
                horizontal_line(2*j, 2*j+1, i+0.5, colors[vert[i].col])
                horizontal_line(2*j, 2*j+1, i+1.5, colors[vert[i+1].col])
                # The actual twist
                twist(2*j+1, 2*j+2, i+1.5, i+0.5,
                    colors[vert[i+1].col], colors[vert[i].col])
            
        vert = transpose(abs(k)-1, vert)

    for i in range(p.strands):
        horizontal_line(2*len(p.braid), 2*len(p.braid)+1, i+0.5,
            colors[vert[i].col])

    fig.savefig("C:/Users/chinm/Downloads/test")


# Visualizes a clasp complex, given its spline graph
def visualize_clasp_complex(graph: SGraph) -> None:
    fig = plt.figure(figsize=(8, 6), dpi=100)
    x_scale = 1/(float(2*len(graph.edges)+1))
    y_scale = 1/(float(len(graph.vert)+1))
    colors = ["b", "g", "r", "c", "m", "y", "k", "w"]
    vert = graph.vert

    # Adds a horizontal line
    def horizontal_line(x_1: float, x_2: float, y: float, col: str):
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_2)*x_scale],
            [(y)*y_scale, (y)*y_scale],
            color=col))

    def twist(x_1: float, x_2: float, y_1: float, y_2: float,
            col1: str, col2: str):
        dy = y_2 - y_1
        dx = x_2 - x_1
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_2)*x_scale],
            [(y_1)*y_scale, (y_2)*y_scale],
            color=col1))
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_1 + dx/3.0)*x_scale],
            [(y_2)*y_scale, (y_2 - dy/3.0)*y_scale],
            color=col2))
        fig.add_artist(lines.Line2D(
            [(x_2 - dx/3.0)*x_scale, (x_2)*x_scale],
            [(y_1 + dy/3.0)*y_scale, (y_1)*y_scale],
            color=col2))

    def vertical_line(x: float, y_1: float, y_2: float, col: str):
        fig.add_artist(lines.Line2D(
            [(x)*x_scale, (x)*x_scale],
            [(y_1)*y_scale, (y_2)*y_scale],
            color=col))

    def cap(x_1: float, x_2: float, y_1: float, col: str):
        x_mid = (x_1+x_2)/2.0
        fig.add_artist(lines.Line2D(
            [(x_1)*x_scale, (x_mid)*x_scale],
            [(y_1 + 1.0/3.0)*y_scale, (y_1 + 0.5)*y_scale],
            color=col))
        fig.add_artist(lines.Line2D(
            [(x_mid)*x_scale, (x_2)*x_scale],
            [(y_1 + 0.5)*y_scale, (y_1 + 1.0/3.0)*y_scale],
            color=col))
        vertical_line(x_1, y_1+1.0/6.0, y_1+1.0/3.0, col)
        vertical_line(x_2, y_1+1.0/6.0, y_1+1.0/3.0, col)
    
    for j in range(len(graph.edges)):
        edge = graph.edges[j]
        k = edge.terminal.num
        for i in range(len(vert)):
            horizontal_line(2*j, 2*j+1.0/3.0, i+0.5, colors[vert[i].col])
            horizontal_line(2*j+2-1.0/3.0, 2*j+2, i+0.5, colors[vert[i].col])

            if((edge.initial.num > i) or (edge.terminal.num < i)):
                horizontal_line(2*j, 2*j+2, i+0.5, colors[vert[i].col])

            elif((edge.typ == 1) and (edge.initial.num == i)):
                horizontal_line(2*j, 2*j+0.5, i+0.5, colors[vert[i].col])
                horizontal_line(2*j, 2*j+0.5, i+1.5, colors[vert[i+1].col])
                horizontal_line(2*j+1.5, 2*j+2, i+0.5, colors[vert[i].col])
                horizontal_line(2*j+1.5, 2*j+2, i+1.5, colors[vert[i+1].col])

                twist(2*j+0.5, 2*j+1.5, i+0.5, i+1.5, colors[vert[i].col],
                    colors[vert[i+1].col])

            elif((edge.typ == -1) and (edge.initial.num == i)):
                horizontal_line(2*j, 2*j+0.5, i+0.5, colors[vert[i].col])
                horizontal_line(2*j, 2*j+0.5, i+1.5, colors[vert[i+1].col])
                horizontal_line(2*j+1.5, 2*j+2, i+0.5, colors[vert[i].col])
                horizontal_line(2*j+1.5, 2*j+2, i+1.5, colors[vert[i+1].col])

                twist(2*j+0.5, 2*j+1.5, i+1.5, i+0.5, colors[vert[i].col],
                    colors[vert[i+1].col])

            elif((edge.typ == 2) and (edge.initial.num == i)):
                horizontal_line(2*j, 2*j+0.5, i+0.5, colors[edge.col])
                horizontal_line(2*j+1.5, 2*j+2, i+0.5, colors[edge.col])

                vertical_line(2*j+0.5, i+0.5, k+0.5+1.0/3.0,
                    colors[edge.col])
                vertical_line(2*j+1.5, i+0.5, k+0.5-1.0/6.0,
                    colors[edge.col])

                cap(2*j+0.5, 2*j+1.5, k+0.5, colors[edge.col])
                horizontal_line(2*j+1, 2*j+2, k+0.5, colors[vert[k].col])

            elif((edge.typ == -2) and (edge.initial.num == i)):
                horizontal_line(2*j, 2*j+0.5, i+0.5, colors[edge.col])
                horizontal_line(2*j+1.5, 2*j+2, i+0.5, colors[edge.col])

                vertical_line(2*j+0.5, i+0.5, k+0.5-1.0/6.0,
                    colors[edge.initial.col])
                vertical_line(2*j+1.5, i+0.5, k+0.5+1.0/3.0,
                    colors[edge.initial.col])

                cap(2*j+0.5, 2*j+1.5, edge.terminal.num + 0.5,
                    colors[edge.col])
                horizontal_line(2*j, 2*j+1, k+0.5, colors[vert[k].col])

    for i in range(len(graph.vert)):
        horizontal_line(2*len(graph.edges), 2*len(graph.edges)+1, i+0.5,
            colors[vert[i].col])

    fig.savefig("C:/Users/chinm/Downloads/test1")
    
                

