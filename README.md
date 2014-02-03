BDDtool
=======

Conversion of BDD feature description and Catch source files and vice versa.
See the [`https://github.com/philsquared/Catch`](https://github.com/philsquared/Catch)
for the details related to Catch.

**The tool is in the very early stage**.

Please, have a look and report the wanted
features or through the [Issue tracker on GitHub](https://github.com/pepr/BDDtool/issues),
or through the [BDD tool for Catch](https://groups.google.com/forum/?fromgroups#!topic/catch-forum/TNY1h-rSkUk)
topic in the [Google Groups Catch forum](https://groups.google.com/forum/?fromgroups#!forum/catch-forum).


License
-------

The software uses *Boost Software License*, i.e. the same license as the Catch
does (see the `LICENSE_1_0.txt`).


The first goal
--------------

The `f2c.py` tool for converting the `features/*.feature` files
to the `catch/*.catch` skeletons.

**2014/02/03:** First version of `f2c.py` implemented. The core is in `felex.py`
(the lexical analyzer of the `*.feature` files), and `fesyn.py` (the syntactic
analyzer of the lexical tokens produced by the `felex` module).

The tool for the reverse process (the analysis of Catch sources and producing
the feature files) is to be published soon.