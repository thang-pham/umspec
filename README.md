# How to run the machine and its expected output.

## Instructions:

* To run the machine:
    `$ ./um.py <codex>`

   The results should be:
   ```
    $ ./um.py ./codex.umz
    self-check succeeded!
    enter decryption key:
   ```

* To run the unit tests:
    `$ ./test_um.py`

   The results should be:
   ```
    $ ./test_um.py
    .....................
    ----------------------------------------------------------------------
    Ran 21 tests in 0.002s

    OK
   ```

* To run the benchmark for the machine:
   sandmark.umz (provided) was downloaded from http://www.boundvariable.org/task.shtml.

   ```
    $ ./um.py sandmark.umz

    The results should be:
    $ ./um.py sandmark.umz
    trying to Allocate array of size 0..
    trying to Abandon size 0 allocation..
    trying to Allocate size 11..
    trying Array Index on allocated array..
    trying Amendment of allocated array..
    checking Amendment of allocated array..
    trying Alloc(a,a) and amending it..
    comparing multiple allocations..
    pointer arithmetic..
    check old allocation..
    simple tests ok!
    about to load program from some allocated array..
    success.
    verifying that the array and its copy are the same...
    success.
    testing aliasing..
    success.
    free after loadprog..
    success.
    loadprog ok.
     == SANDmark 19106 beginning stress test / benchmark.. ==
    100. 12345678.09abcdef
     == SANDmark 19106 beginning stress test / benchmark.. ==
    100. 12345678.09abcdef
    99.  6d58165c.2948d58d
    98.  0f63b9ed.1d9c4076
    97.  8dba0fc0.64af8685
    96.  583e02ae.490775c0
    95.  0353a77b.2f02685c
    ...
   ```