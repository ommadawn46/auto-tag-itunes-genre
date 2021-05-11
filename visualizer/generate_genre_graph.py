import random

from graphviz import Digraph

import config

rand_byte = lambda: random.randint(0, 255)
rand_color = lambda: "#%02x%02x%02x" % (rand_byte(), rand_byte(), rand_byte())


def make_graph(parent_genre, graph):
    with graph.subgraph(name="cluster_" + parent_genre) as sub_graph:
        sub_graph.attr(color=rand_color(), label=parent_genre)
        for sub_genre in config.SUB_GENRES[parent_genre]:
            sub_graph.edge(parent_genre, sub_genre)
            if sub_genre in config.SUB_GENRES:
                make_graph(sub_genre, sub_graph)


def main():
    graph = Digraph(format="png", strict=True)
    for parent_genre in config.SUB_GENRES:
        graph.node(parent_genre)

    root_genres = []
    for genre in config.SUB_GENRES:
        for other_genre in config.SUB_GENRES:
            if genre in config.SUB_GENRES[other_genre]:
                break
        else:
            root_genres.append(genre)

    for parent_genre in root_genres:
        make_graph(parent_genre, graph)

    graph.render("./sub_genre_visualize/genre_tree")


if __name__ == "__main__":
    # ❯ python -m visualizer.generate_genre_graph
    main()
