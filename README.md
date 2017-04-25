*mgproc*: A Python Package for MG Processing Research
===================================================

This is a collection of Python3 scripts to facilitate the investigation of human processing from the perspective of Minimalist grammars (MGs).


Background
----------

MGs were developed in Stabler (1997) as a formalization of Chomsky's Minimalist program.
A top-down parser for MGs is defined in Stabler (2013) and has been [implemented in a number of languages](https://github.com/epstabler/mgtdb).
A number of subsequent works have successfully used this parser to make predictions about relative difficulty in sentence processing.
Good starting points with a review of the previous literature are Gerth (2015) and Graf et al. (to appear).

- Gerth, Sabrina: [Memory Limitations in Sentence Comprehension](https://publishup.uni-potsdam.de/opus4-ubp/frontdoor/index/index/docId/7155)
- Graf, Thomas, James Monette, and Chong Zhang (to appear): Relative Clauses as a Benchmark for Minimalist Parsing (link to be added soon)
- Stabler, Edward (1997): [Derivational Minimalism](http://www.linguistics.ucla.edu/people/stabler/eps-lacl.pdf)
- Stabler, Edward (2013): [Two Models of Minimalist, Incremental Syntactic Analysis](http://www.linguistics.ucla.edu/people/stabler/Stabler12-2models.pdf)


Quick Start Guide
-----------------

With *mgproc* you can easily compare MG derivation trees with respect to thousands of complexity metrics for sentence processing.
The scripts integrate well with a LaTeX-centric workflow, following the ideal of OpenScience where data and publication form a cohesive unit.
Usually a parsed derivation tree is specified by four files.
Assuming the tree is called `foo`, we have:

1. `foo.tree.forest`: the tree specification, given as labeled bracketing using the syntactic conventions of the [forest package for LaTeX](https://www.ctan.org/pkg/forest?lang=en).
1. `foo.move.forest`: all movement paths, expressed with the typical [tikz](https://www.ctan.org/pkg/pgf?lang=en) syntax for path drawing
1. `foo.linear`: the linear order of all leaf nodes; this is necessary because MG derivation trees encode linear order only indirectly
1. `foo.io.forest`: automatically created by *mgproc*, this file provides an overlay of the index/outdex annotation to be used in publications

The general workflow is as follows:

1. Create `foo.tree.forest` and write the tree exactly the same way you always do in forest.
   - As in forest, nodes can be given a name by adding `, name=` after the label.
     If you do not provide a name, *mgproc* will refer to the node as `t<gorn>`, where `<gorn>` is the [Gorn address](https://en.wikipedia.org/wiki/Gorn_address) of the node.
   - For empty (= unpronounced) leaf nodes, add the attribute `, empty`.
     Interior nodes do not need this attribute, *mgproc* can infer their status automatically.
   - Usage of other forest options should not interfere with *mgproc*.
     If you notice any problems, please open an issue here on github.

1. If the derivation tree contains movement dependencies, create `foo.move.forest` and specify them there.
   The general syntax is `\draw[move={f}] (source) to (target);`, where `source` and `target` are the names of the nodes and `f` is the feature triggering movement (e.g. nom, wh, top).
   You can use more complicated tikz constructs as you see fit, but avoid `\foreach` loops and other tricks that obscure what moves where.
   For movement to intermediate landing sites, you can add `non-final` as a parameter for the draw command.
   If a subtree undergoes multiple movement steps, the draw commands should be ordered according to the timing of movement.
   So the first movement step is listed first, then the second, then the third, and so on.

1. Specifying `foo.linear` by hand can be difficult, but *mgproc* provides a helper for this, too.
   Open a shell and run `python3 -i __init__.py`.
   In the shell, execute `mytree = tree_from_file('path/to/foo')`.
   This creates a tree from `foo.tree.forest` and (if it exists) `foo.move.forest`.
   Then run `mytree.show_leaves()` to get a list of all the leaf nodes.
   Each line contains a node, specified in the form `<label>; <gorn>`.
   Copy this list into your text editor and reorder the lines so that their order in the file from top-to-bottom mirrors their linear order in the sentence from left to right.
   Save the file as `foo.linear`.

1. In the Python3 shell, rerun `mytree = tree_from_file('path/to/foo')`.
   You now have a fully index/outdex annotated derivation tree.
   You can inspect the tree more carefully with `mytree.show()` and `mytree.fprint()`.
   Run `ioprint(mytree, filename='foo')` to have *mgproc* produce a forest file `foo.io.forest` with the annotations for each node.


Automated Comparisons
---------------------

Once you are sure that all trees have been specified correctly, you can move on to automated comparisons.
A comparison uses two components: a list of metrics, and a pair of trees such that the first one is easier to process than the second.
While you could define all of that directly in the shell, *mgproc* tries to make this process much less painful through the use of text files.


### Metric Files

Metrics can be defined in a *.metrics file.
The format is as follows:

```csv
name of metric; LaTeX command for metric name; type of memory load; operator; trivial; filter; function
```

Concrete examples can be found in the `metrics` subfolder.
The file `node_filtered.metrics`, for instance, contains this line:

```csv
BoxT' ;   ; tenure; len    ; trivial; I, U, P, *
```

You can easily create your own metric files with the available parameters.

Parameter | Values                                       | Effect
--:       | :--                                          | :--
name      | any string                                   | used in shell outputs
LaTeX     | any LaTeX command                            | used in LaTeX output
load type | tenure, size                                 | whether tenure or size-based values are calculated by the metric
operator  | safemax, avg, any Python function over lists | maps list of tenure/size values to metric value
trivial   | empty or trivial                             | wheter trivial values (e.g. tenure < 2) should be included in calculations
filters   | I, P, U, *                                   | whether nodes of a particular type should be filtered out


Filter Value | Effect
--:          | :-- 
I            | ignore interior nodes
P            | ignore pronounced leaf nodes
U            | ignore unpronounced leaf nodes
\*           | also use filter combinations

The `*` operator is used to produce multiple metrics from one line.
Whereas a filter specification `U, I` would just produce a single metric that ignores unpronounced leaf nodes and all interior nodes, the minimally different `U, I, *` produces four metrics with different filters (no filters, I filter, U filter, both I and U filter).

Once a metric file has been created, you can load it with `metrics_from_file`.

```python
my_metrics = metrics_from_file(inputfile='./metrics/base')
```

Note that the `.metrics` file extension can be omitted.
You can also specify a parameter `ranks` to build ranked metrics.

```python
my_metrics = metrics_from_file(inputfile='./metrics/base', ranks=3)
```

With two metrics *A* and *B* and a rank of 3, *mgproc* would build 8 ranked metrics:

1. A,A,A (same as A)
1. A,A,B (same as A,B)
1. A,B,A (same as A,B)
1. A,B,B (same as A,B)
1. B,A,A (same as B,A)
1. B,A,B (same as B,A)
1. B,B,A (same as B,A)
1. B,B,B (same as B)

As this example shows, there is little point in setting the number of ranks higher than the number of base metrics.
Quite generally, you should not set the number of ranks too high, the number of ranked metrics grows very, very fast, and by extension *mgproc*'s memory usage will too.


### Comparison Files

Comparisons can also be specified in files.
Several examples are collected in the subfolder `comparisons`.
The file `relatives_wh.compare`, for instance, looks like this:

```csv
eng-src-orc-prom; ; ENG_src_prom; ENG_orc_prom;
chn-src-orc-prom; ; CHN_src_prom; CHN_orc_prom;
```

This defines two comparisons with names *eng-src-orc-prom* and *chn-src-orc-prom*, respectively.
The second field is empty but could be used to define LaTeX commands for these comparisons.
The remaining two fields are names of some `.tree.forest` files that specify the relevant trees.
The first tree is supposed to be easier to process than the second.
The overall format, then, is as follows:

```csv
name; LaTeX command; winner; loser
```

You can load a `.compare` file with the command `comparisons_from_file`:

```python
comp = comparisons_from_file('./comparisons/relatives_wh', directory='./trees', metrics=my_metrics)
```

As with `metrics_from_file`, the file extension can be omitted.
Note that `comparisons_from_file` requires a set of metrics to already be defined.
The directory parameter tells *mgproc* that all the trees referenced in `relatives_wh` are located in the folder `trees`.
Alternatively, we could have specified the full paths in `relatives_wh` rather than just the filenames.

Exectuting the above command will immediately cause *mgproc* to run the relevant comparisons.
If your sets of metrics is very large, this can take quite a while and consume a lot of memory.
Once the job completes, you can view the results with `comp.show()` and `comp.table()`.


LaTeX Integration 
-----------------

To effectively use *mgproc* with LaTeX, you have to specify a few macros and tikz styles. 
Just copy-paste the following commands into the preamble of your document.

```latex
% load tikz and forest with more visible arrows
\usepackage{tikz}
\usepackage{forest}
\usetikzlibrary{arrows.meta}

% define move style
\tikzset{move/.style = {-{Latex[length=.5em]},dashed,blue}}
\tikzset{rightward/.style = {dotted}}
\tikzset{annotation/.style = {font=\footnotesize}}
\tikzset{index/.style = {annotation, anchor=south east}}
\tikzset{outdex/.style = {annotation, anchor=north west}}
\tikzset{boxed/.style = {draw}}
\tikzset{empty/.style = {}}
\tikzset{non-final/.style = {opacity=70}}

% indexed node labels in trees;
% these macros are only needed if you want to use the output of the .fprint method
\newcommand{\Lab}[3]{\tsp{#2}#1\tsb{#3}} % for normal nodes
\newcommand{\BLab}[3]{\tsp{#2}#1{\setlength{\fboxsep}{.25\fboxsep}\boxed{\tsb{#3}}}} % for boxed leaves
\newcommand{\IBLab}[3]{\tsp{#2}#1{\setlength{\fboxsep}{.25\fboxsep}\boxed{\tsb{#3}}}} % for boxed interior nodes
```

Then use the `texprint` function to produce an `mgproc.forest` file for you and load it with `\input` in your document.

```python
my_tree = tree_from_file('./trees/beautiful.tree.forest')
texprint(my_tree, filename='beautiful', tree_directory='./trees/')
```

Here is an example that shows how to load files stored in a subfolder `img`:

```latex
The first tree is shown below.
%
\begin{center}
    \input{./img/foo.mgproc.forest}
\end{center}
%
And the second one is next.
%
\input{./img/bar.mgproc.forest}
```


Dynamically Extending the Code
------------------------------

For your own research, you may need to define completely new metrics or tree traversals.
But digging into the bowels of *mgproc* and making code changes is not for the faint of heart and may easily cause breakage.
Instead, you can create a new Python file in the folder *usercode*.
When mgproc is started, it automatically executes all the code in every Python file in that folder.


### Defining New Metrics

Behind the scenes, the value a metric assigns to a given tree is computed in three steps:

1.  The `memory_measure` function calls the correct helper function based on the load type of the metric (*tenure* or *size*).

1.  Depending on the load type, `tenure_extract` or `move_extract` is called to produce a list of the tenure or size values for every node.

1.  The operator function is applied to the list to obtain the final value under the defined metric.

For most cases, defining a new metric only requires you to use a different operator.
For example, if you want the lowest tenure value rather than the highest, you could use the Python built-in function `min`:

~~~bash
MinTen; ; tenure; min; ; I, U, P, *
~~~

But sometimes Python built-ins just won't do and you have to define your own function.
This is very easy.

1.  Create a new file in *usercode*.
1.  Add the appropriate function definition to that file.

    ~~~python
    def new_function(list_argument):
        """This function does not do much"""
        return list_argument
    ~~~

1.  Specify that function as the operator for your new metric.

    ~~~bash
    NewMetric; ; tenure; new_function;
    ~~~

Since you can use just about any Python function that takes a single list as its argument, you can define even very complicated metrics.


### Defining New Load Types

Unfortunately, sometimes your metric is so complicated that the values provided by `tenure_extract` and `move_extract` simply aren't enough.
In that case, you have to define a completely new load type.
This requires more effort, but is still doable.

The solution is to redefine `memory_measure` to expand it with your own custom code:

1.  Create a new file in *usercode*.
1.  Write a new function definition for `memory_measure`.
    It is a good idea to copy-paste the original memory_measure code so that old metrics will still work as intended.
    Just expand the if-then-else block for load_type with new cases.

    ~~~python
    def memory_measure(IOTree,
                       operator: 'function'=None, load_type: str='tenure',
                       filters: list=[], trivial: bool=False) -> 'int/list':

    if load_type == 'tenure':
        load_type = tenure_extract
    elif load_type == 'size':
        load_type = move_extract
    elif load_type == 'my_metric':
        load_type = new_function

    return operator(load_type(IOTree,
                              filters=filters,
                              trivial=trivial).values())
    ~~~

1.  Add a definition for the new function you are calling in `memory_measure`.
    In the example above, we added `new_function`, so we need to add the corresponding definition.

    ~~~python
    def new_function(list_argument):
        """This function does not do much"""
        return list_argument
    ~~~

    For examples of what a useful metric function looks like, check out `tenure_extract` and `move_extract` in `tree_values.py`.

1.  Add the definition for your new metric to the relevant metric file.
    Since we told memory_measure to use `new_function` if the load type is `my_metric` in the example above, our metric file could include the following new line:

    ```bash
    DummyMetric; ; my_metric; sum
    ```

### Defining New Tree Traversals

Unfortunately the code in its current form isn't sufficiently modular when it comes to the tree traversal.
Right now, it is defined directly in the `_annotate` method of the class `IOTree`.
So you will have to overwrite that class method with your own.
That is pretty tricky and should not be attempted unless you know what you're doing.
At this point, it is indeed easier to just change `_annotate` directly in the code.

In the future, this part of the code will be modularized so that multiple traversals can be defined at the same time and each metric decides which traversal it should be used with.


Limitations and Known Bugs
--------------------------

### Naming Conventions for Node Information

Since *mgproc* uses regular expressions instead of a proper text parser, there is a risk of it breaking down if you deviate from the intended naming conventions:

1. The most important rule: do not use `%` for anything except LaTeX comments!
   Everything after `%` will be considered a comment and be removed from the file.
   So if your node label is `10\% of people`, it will be truncated to `10\ `.

1. Node labels are allowed to contain
   - alphanumeric unicode characters,
   - ASCII apostrophes (`'`),
   - hyphens (`-`),
   - periods (`.`),
   - the dollar sign (`$`), 
   - backslash (`\ `),
   - curly braces (`{`, `}`).

   This covers most LaTeX needs.
   However, **commas (`,`), semicolons (`;`) and square brackets (`[`, `]`) are not allowed**, not even if they are contained within curly braces.
   If you need those, use equivalent LaTeX commands instead (`\lbrack`, `\rbrack`).
   For the others, define your own macro with `\newcommand{\comma}{,}` and `\newcommand{\semicolon}{;}`.

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

1. Line breaks are ignored by *mgproc* (see `ugly.forest` for a working but, well, ugly example).
   Nonetheless it is recommended that you write your forest files with proper line breaks and indentation for improved readability.


### Linearization

Unexpected things may happen if the forest files are not well-formed.
An incorrect `.linear` file may lead to obvious breakage or just an incorrectly computed index/outdex annotation without any warning messages.
Always double- and triple-check that the linear order of leaf nodes is specified correctly!


### Memory Usage

Do not underestimate memory usage when defining many metrics.
Each individual metric only consumes about 1 kilobit (not kilobyte!) of memory, but if you automatically create ranked metrics then number still rises fast enough to quickly consume multiple gigabytes.
For instance, running `metrics = metrics_from_file(inputfile='metrics/node_filtered', ranks=4)` will take the base metrics, create all their possible variants with node filters, and then use this set M to construct M^4^, i.e. the set of ranked metrics with four components.
This set has 65,610,000 members, so you better have 6GB of free memory to store all those metrics.
For comparison, setting the rank to 3 reduces the number to 729,000 metrics and thus under 100MB of RAM.
Given the dubious empirical status of metrics of rank 4 or greater, there are currently no plans to redesign the code for more efficient memory usage.


Tips & Tricks
-------------

- The *usercode* folder can be used to design your own standard test suites.
  If you find yourself always running the same sequence of `metrics_from_file` and `comparison_from_file` commands right after starting *mgproc*, just put them in a separate Python file in *usercode*.

  Give it a filename like `zzz_startup` to ensure that the file is loaded **after** any other files in *usercode* that are needed for any custom metrics you use.

- If you have a forest file that uses our custom LaTeX macros `\Lab`, `\BLab`, or `\IBLab` for node labels, you can use a regular expression to remove them automatically.
  On Linux, the command is:

    ~~~bash
    sed -i 's/\\I\?B\?Lab{\([^}]*\)}{[0-9]*}{[0-9]*}/\1/' <file_to_be_changed>
    ~~~

  You can also batch process all files in a given folder:

    ~~~bash
    for file in *.tree.forest; do sed -i 's/\\I\?B\?Lab{\([^}]*\)}{[0-9]*}{[0-9]*}/\1/' $file; done
    ~~~


To Do
-----

- factorize file reading and writing to avoid code duplication
- some lists should be sets (e.g. filters)
- Generalize empty & content to arbitrary property system
   - prop={empty, content, R-expression, discourse-salient}
   - generalize filters accordingly to match any definable property
- Unit tests
- Implement a faster evaluation system for ranked metrics (based on results for base metrics)
- allow disjunctions in comparison files ("A or B is easier than C or D"; useful for scope, attachment preferences, and ambiguities)
