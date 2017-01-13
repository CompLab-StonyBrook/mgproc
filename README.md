mgproc: A Python Package for MG Processing Research
===================================================

This is a collection of Python3 scripts to facilitate the investigation of human processing from the perspective of Minimalist grammars (MGs).


Background
----------

MGs were developed in Stabler (1997) as a formalization of Chomsky's Minimalist program.
A top-down parser for MGs is defined in Stabler (2012) and has been [implemented in a number of languages](https://github.com/epstabler/mgtdb).
A number of subsequent works have successfully used this parser to make predictions about relative difficulty in sentence processing.

Fixme: references to literature


Quick Usage Guide
-----------------

With mgproc you can easily compare MG derivation trees with respect to thousands of complexity metrics for sentence processing.
The scripts integrate well with a LaTeX-centric workflow, following the ideal of OpenScience where data and publication form a cohesive unit.
Usually a parsed derivation tree is specified by four files.
Assuming the tree is called `foo`, we have:

1. `foo.forest`: the tree specification, given as labeled bracketing using the syntactic conventions of the [forest package for LaTeX](https://www.ctan.org/pkg/forest?lang=en).
1. `foo_move.forest`: all movement paths, expressed with the typical [tikz](https://www.ctan.org/pkg/pgf?lang=en) syntax for path drawing
1. `foo.linear`: the linear order of all leaf nodes; this is necessary because MG derivation trees encode linear order only indirectly
1. `foo_io.forest`: automatically created by mgproc, this file provides an overlay of the index/outdex annotation to be used in publications

The general workflow is as follows:

1. Create `foo.forest` and write tree exactly the same way you always do in forest.
   - As in forest, nodes can be given a name by adding `, name=` after the label.
     If you do not provide a name, mgproc will refer to the node as `t<gorn>`, where `<gorn>` is the [Gorn address](https://en.wikipedia.org/wiki/Gorn_address) of the node.
   - For empty (= unpronounced) leaf nodes, add the attribute `, empty`.
     Interior nodes do not need this attribute, mgproc can infer their status automatically.
   - Usage of other forest options should not interfere with mgproc.
     If you notice any problems, please open an issue here on github.

1. If the derivation tree contains movement dependencies, create `foo_move.forest` and specify them there.
   The general syntax is `\draw[move{f}] (source) to (target);`, where `source` and `target` are the names of the nodes and `f` is the feature triggering movement (e.g. nom, wh, top).
   You can use more complicated tikz constructs as you see fit.

1. Specifying `foo.linear` by hand can be difficult, but `mgproc` provides a helper for this, too.
   Open a shell and run `python3 -i mgproc.py`.
   In the shell, execute `mytree = tree_from_file('path/to/foo')`.
   This creates a tree from `foo.forest` and (if it exists) `foo_move.forest`.
   Then run `mytree.show_leaves()` to get a list of all the leaf nodes.
   Each line contains a node, specified in the form `<label>; <gorn>`.
   Copy this list into your text editor and reorder the lines so that their order in the file from top-to-bottom mirrors their linear order in the sentence from left to right.
   Save the file as `foo.linear`.

1. In the Python3 shell, rerun `mytree = tree_from_file('path/to/foo')`.
   You now have a fully index/outdex annotated derivation tree.
   You can inspect the tree more carefully with `mytree.show()` and `mytree.fprint()`.
   Run `ioprint(mytree, filename='foo')` to have mgproc produce a forest file with the annotations for each node.


LaTeX Integration 
-----------------

To effectively use mgproc with LaTeX, you have to specify a few macros and tikz styles. 
Just copy-paste the following commands into the preamble of your document.

```latex
% load tikz and forest with more visible arrows
\usepackage{tikz}
\usepackage{forest}
\usetikzlibrary{arrows.meta}

% define move style
\tikzset{move/.style = {-{Latex[length=.5em]},dashed,blue}}
\tikzset{index/.style = {font={\footnotesize}, anchor=south.east}}
\tikzset{outdex/.style = {font={\footnotesize}, anchor=north.west}}
\tikzset{boxed/.style = {draw}}

% indexed node labels in trees;
% these macros are only needed if you want to use the output of the .fprint method
\newcommand{\Lab}[3]{\tsp{#2}#1\tsb{#3}} % for normal nodes
\newcommand{\BLab}[3]{\tsp{#2}#1{\setlength{\fboxsep}{.25\fboxsep}\boxed{\tsb{#3}}}} % for boxed leaves
\newcommand{\IBLab}[3]{\tsp{#2}#1{\setlength{\fboxsep}{.25\fboxsep}\boxed{\tsb{#3}}}} % for boxed interior nodes
```

To typeset a tree with forest, use `\input` to load the relevant files.
Here is an example where all files are stored in a subfolder `trees`:

```latex
\begin{forest}
    % load derivation tree
    \input{./trees/foo.forest}
    % add movement arrows
    \input{./trees/foo_move.forest}
    % add index/outdex annotation for each node
    \input{./trees/foo_io.forest}
\end{forest}
```

Note that there must not be any empty lines anywhere within the forest environment.
This also holds for the files you load with `\input`.


Limitations and Known Bugs
--------------------------

### Naming Conventions for Node Information

Since mgproc uses regular expressions instead of a proper text parser, there is a risk of it breaking down if you deviate from the intended naming conventions:

1. The most important rule: do not use `%` for anything except LaTeX comments!
   Everything after `%` will be considered a comment and be removed from the file.
   So if your node label is `10\% of people`, it will be truncated to `10`.

1. Node labels are allowed to contain
   - alphanumeric unicode characters,
   - ASCII apostrophes (`'`),
   - hyphens (`-`),
   - periods (`.`),
   - the dollar sign (`$`), 
   - backslash (`\ `),
   - curly braces (`{`, `}`).

   This covers most LaTeX needs.
   However, **commas (`,`) and square brackets (`[`, `]`) are not allowed**, not even if they are contained within curly braces.
   If you need those, use equivalent LaTeX commands instead (`\lbrack`, `\rbrack`).
   For the comma, define your own macro with `\newcommand{\comma}{,}`.

1. Node names may only contain
   - alphanumeric unicode characters,
   - ASCII apostrophes (`'`),
   - hyphens (`-`),
   This covers the full range of recommended tikz names.

1. When specifying a node as `empty`, it must be preceded by a comma, possibly with whitespace inbetween.
   So `[S, name=root,empty` and `S, name=root,   empty` are both fine, but `S, name=root empty` is not.
   But the latter would not be allowed by forest anyways.

1. Feature names given via `move={<name>}` may consist of just about anything.
   But I suggest sticking with simple alphanumeric characters and doing any typesetting by redefining the move style.

1. Line breaks are ignored by mgproc (see `ugly.forest` for a working but, well, ugly example).
   Nonetheless it is recommended that you write your forest files with proper line breaks and indentation for improved readability.


### Linearization

Unexpected things may happen if the forest files are not well-formed.
An incorrect `.linear` file may lead to obvious breakage or just an incorrectly computed index/outdex annotation without any warning messages.
Always double- and triple-check that the linear order of leaf nodes is specified correctly!


### File Names

While batch processing has not been implemented yet, the plan is to simply collect all forest files in a given folder and filter out those that end in `_move` or `_io`.
Each remaining file should be of the form `foo.forest` and thus work with `tree_from_file()` as intended.
Of course this strategy will fail whenever a tree specification file has been given a name that ends in `_move`, e.g.\ `relative_clause_with_move`.
So avoid giving trees names that end in `_move` or `_io`.


To Do
-----

- Better documentation of code (in particular docstrings)
- Batch processing
- Rewrite metric evaluation from scratch
- Bach comparison of metrics
- Unit tests
- Tons of bug testing
