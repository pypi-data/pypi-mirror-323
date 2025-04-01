`Mathics3 <https://mathics.org>`_ Debugger Module
==================================================

Until we have some proper documentation here are some examples.


Mathics3 Module Examples
------------------------

To enable debugging in Mathics3, install ``mathics3-trepan``.
Inside a mathics3 session run::

  In[1]:= LoadModule["pymathics.trepan"]
  Out[1]= "pymathics.trepan"

Next, you need to active some events to trigger going into the debugger::

  In[2]:= DebugActivate[mpmath->True]
  Out[2]=

Other events include: "Debugger", "Get", "Numpy", "SymPy", "apply", "evalMethod", and "evaluation".

In the above, ``mpmath->True`` goes into the debugger anytime a mpmath function is called.
``Exp[1.0]`` is such a function::

  In[3]:= Exp[1.0]
  mpmath call  : mpmath.ctx_base.StandardBaseContext.power(2.718281828459045, 1.0)
  (/tmp/mathics-core/mathics/eval/arithmetic.py:68 @88): run_mpmath
  mp 68             result_mp = tracing.run_mpmath(mpmath_function, *mpmath_args)
  (Mathics3 Debug)

A useful command to run is ``bt -b`` which shows the Buitin Function calls in the call stack::

    (Mathics3 Debug) bt -b
    B#0 (2) Power[z__]
              called from file '/tmp/mathics-core/mathics/core/builtin.py' at line 659
    B#1 (3) Power[x_, y_]
              called from file '/tmp/mathics-core/mathics/builtin/arithfns/basic.py' at line 477

To get a list of all debugger commands::

    (Mathics3 Debug) help *
    List of all debugger commands:
        alias      down   help  mathics3      reload  trepan3k
        backtrace  eval   info  printelement  set     up
        continue   frame  kill  python        show

When you are done inspecting things, run ``continue`` (or short-hand ``c``) to resume execution::

    (Mathics3 Debug) c
    mpmath result: 2.71828182845905
    Out[3]= 2.71828


Improved TraceEvaluation
------------------------

As before, install ``mathics3-trepan``. To set up tracing ``.evaluate()`` calls::

    In[1]:= LoadModule["pymathics.trepan"]
    Out[1]= "pymathics.trepan"

    In[2]:= TraceActivate[evaluation->True]
    Out[2]=

In contrast to ``DebugActivate``, ``TraceActivate`` just prints or traces events.

Now we are ready for some action:

.. image:: https://github.com/Mathics3/mathics3-debugger/blob/master/screenshots/TraceEvaluation.png

Above we trace before an ``evaluate()`` method call and also sometimes show the return value.

To reduce the unnecessary output, evaluations when it has some value. In particular, above there is an evaluation of the Symbols "Power", and "Plus", The result of evaluating these is the same symbol. So we don't show either ``Evaluating: Power``or ``Returning: Power``. Similarly, we omit the same for ``Plus``.

We also omit ``Returning: Plus[1, x]`` because ``Plus[1, x]`` is the same expression as went in.
But notice we *do* show ``Returning: Plus[x, 1] = Plus[1, x]``. Here the difference is that the order of the parameters got rearranged. Perhaps this is not interesting either, but currently, it is shown.

Now let's do the same thing but set the value of ``x``::

   In[4]:= x = 3
   Evaluating: Set[x, 3]

   Returning: Set[x, 3] = 3

   Out[4]= 3

   In[5]:= (x + 1) ^ 2
   Evaluating: Power[Plus[x, 1], 2]

     Evaluating: Plus[x, 1]

       Returning: x = 3

     Returning: Plus[x, 1] = 4

   Returning: Power[Plus[x, 1], 2] = 16

   Out[5]= 16

Here, the return values have the computed Integer values from evaluation as you'd expect to see when working with Integer values instead of mixed symbolic and Integer values.

Post-mortem debugging
---------------------


To enter the debugger on an unrecoverable error, use the
``--post-mortem`` option when invoking ``mathics``::

  mathics --post-mortem
  # Find a Python bug in Mathics3 and trigger that.
  # I modified Compress.eval() and added 1/0

  In[1]:= Compress["abc"]
    Traceback (most recent call last):
    File "/tmp/mathicsscript", line 8, in <module>
    sys.exit(main())
             ^^^^^
    ...
    ZeroDivisionError: division by zero
    Uncaught exception. Entering post-mortem debugger...
    (/tmp/mathics/builtin/compress.py:37 @6): eval
    !! 37         1/0
    R=> (<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero'),
    (Trepan3k:pm) load trepan3k_mathics3
    loaded command: "mathics3"
    loaded command: "mbacktrace"
    loaded command: "mup"
    loaded command: "printelement"
    (Trepan3k:pm) mbt -b
    B>0 (0) Compress[expr_, OptionsPattern[Compress]]
              called from file '/tmp/Mathics3/mathics-core/mathics/builtin/compress.py' at line 37
    B>1 (36) Compress[expr_, OptionsPattern[Compress]]
               called from file '/tmp/Mathics3/mathics-core/mathics/builtin/compress.py' at line 37
    (Trepan3k:pm)


Showing Tracebacks on long-running operations
----------------------------------------------

The debugger (and trepan3k) support signal handling. With this, you can set up a ``SIGINT`` handler.

Here is an example:

.. image:: https://github.com/Mathics3/mathics3-debugger/blob/master/screenshots/traceback-with-Ctrl-C.png


Without the debugger, but with ``trepan3k`` installed, you can use ``Breakpoint[]``, and issue the ``handle`` command. You won't get as nice of a traceback, but it should still work.
