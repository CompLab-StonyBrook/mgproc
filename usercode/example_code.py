# we define our own function,
# which can then be used for defining metrics
#
# see memory_measure in tree_values.py for
# an example of a realistic metric function

from os import listdir
from os.path import isfile, join

# def my_really_pointless_test_function():
#     pass

def texprint_all_trees():
    ## print all trees from './trees' to './output_trees/batch_output

    ## get file path

    filepaths = [f for f in listdir('./trees/') if isfile(join('./trees/', f))]
    filepaths.remove('.DS_Store')

    ## get tree names in a list

    treenames = []

    for f in filepaths:
        treename = f.split(".", 1)[0]
        treenames.append(treename)

    ## save trees to a tuple (name, tree)

    trees = []

    for tree in treenames:
        treepath = "./trees/" + tree
        t = tree_from_file(treepath)
        trees.append((tree, t))

    ## texprint all trees

    for (name, tree) in trees:
        iotreepath = './output_trees/batch_output/' + name
        texprint(tree, filename = iotreepath, tree_directory = './trees')


# def texprint_one_tree(treename, "stringname"):
#     ## print treename to './output_trees'

#     filename = './output_trees/' + stringname
#     texprint(treename, filename = filename, tree_directory = './trees' )