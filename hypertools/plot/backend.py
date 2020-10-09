import inspect
import sys
import warnings
from contextlib import redirect_stdout
from functools import wraps
from io import StringIO
from os import getenv

import matplotlib as mpl
import matplotlib.pyplot as plt

from .._shared.exceptions import HypertoolsBackendError


# this isn't threadsafe, but neither is matplotlib so that's probably okay
# https://matplotlib.org/faq/howto_faq.html#working-with-threads
BACKEND_WARNING = None
HYPERTOOLS_BACKEND = None
IPYTHON_INSTANCE = None
IS_NOTEBOOK = None
reset_backend = None
switch_backend = None


# TODO look through source for IPython.core.pylabtools.configure_inline_support
def init_backend():
    """
    Runs when hypertools is initially imported and sets the matplotlib
    backend used for animated/interactive plots.

    Returns
    -------
    None

    Notes
    -----
    Sets the following module-scoped variables:

    HYPERTOOLS_BACKEND : str
        The matplotlib backend used for interactive or animated
        plots.
    IPYTHON_INSTANCE : ipykernel.zmqshell.ZMQInteractiveShell or None
        The IPython InteractiveShell instance for the current
        IPython kernel, if any.  Otherwise, None.
    BACKEND_WARNING : str or None
        The warning to be issued upon trying to create an
        interactive or animated plot, if any.  Otherwise, None.  This is
        set under two conditions:
            1. No compatible interactive backends are available
            2. Hypertools was imported into a notebook and the
               notebook-native interactive backend (nbAgg) is not
               available.  Tthis should never happen, but theoretically
               could if the ipython/jupyter/jupyter-core/notebook
               installation is faulty.
    switch_backend : function
        The function called to switch to the temporary backend prior to
        plotting. `_switch_notebook_backend` if running in a Jupyter
        notebook, otherwise, `matplotlib.pyplot.switch_backend`.
    reset_backend : function
        The function called to switch back to the original backend after
        plotting. `_reset_backend_notebook` if running in a Jupyter
        notebook, otherwise `matplotlib.pyplot.switch_backend`.
    """
    global BACKEND_WARNING, \
        HYPERTOOLS_BACKEND, \
        IPYTHON_INSTANCE, \
        IS_NOTEBOOK, \
        reset_backend, \
        switch_backend

    curr_backend = mpl.get_backend()

    try:
        # function exists in namespace if hypertools was imported from
        # IPython shell or Jupyter notebook
        IPYTHON_INSTANCE = get_ipython()
        assert 'IPKernelApp' in IPYTHON_INSTANCE.config
        IS_NOTEBOOK = True
        # if running in a notebook, should almost always use nbAgg. May
        # eventually let user override this with environment variable
        # (e.g., to use ipympl, widget, or WXAgg in JupyterLab), but
        # switching backends in IPython is already a nightmare
        try:
            mpl.use('nbAgg')
            working_backend = 'nbAgg'
        except ImportError:
            BACKEND_WARNING = ("Failed to switch to interactive notebook "
                               "backend ('nbAgg'). Falling back to inline "
                               "static plots.")
            working_backend = 'inline'

        switch_backend = _switch_backend_notebook
        reset_backend = _reset_backend_notebook

    except (NameError, AssertionError):
        # NameError: imported from script
        # AssertionError: imported from IPython shell
        IS_NOTEBOOK = False
        # (excluding WebAgg - no way to test in advance if it will work)
        backends = ('TkAgg', 'Qt5Agg', 'Qt4Agg', 'WXAgg', 'GTK3Agg')
        if sys.platform == 'darwin':
            # prefer cocoa backend on Mac - pretty much guaranteed to
            # work, appears to be faster, and Mac does NOT like Tkinter
            backends = ('MacOSX', *backends)

        # TODO: document setting environment variable
        # check for configurable environment variable
        env_backend = getenv("HYPERTOOLS_BACKEND")
        if env_backend is not None:
            # prefer user-specified backend, if set
            if env_backend.lower() in tuple(map(str.lower, backends)):
                backends = (backends[:backends.index(HYPERTOOLS_BACKEND)],
                            *backends[backends.index(HYPERTOOLS_BACKEND) + 1:])

            backends = (env_backend, *backends)

        for b in backends:
            try:
                mpl.use(b)
                working_backend = b
                break

            except ImportError:
                # raised if backend's depencencies aren't installed
                continue

        else:
            BACKEND_WARNING = ("Failed to switch to any interactive backend "
                               f"({', '.join(backends)}. Falling back to 'Agg'.")
            working_backend = 'Agg'

        if env_backend is not None and working_backend.lower() != env_backend.lower():
            # The only time a plotting-related warning should be issued
            # on import rather than on call to hypertools.plot is if
            # $HYPERTOOLS_BACKEND specifies an incompatible backend,
            # since that will have been set manually.
            warnings.warn("failed to set matplotlib backend to backend "
                          f"specified in environment ('{env_backend}'). "
                          f"Falling back to '{working_backend}'")

        switch_backend = reset_backend = _switch_backend_regular

    finally:
        # restore backend
        mpl.use(curr_backend)
        HYPERTOOLS_BACKEND = working_backend


def set_interactive_backend(newbackend):
    global HYPERTOOLS_BACKEND

    if newbackend == 'module://ipykernel.pylab.backend_inline':
        newbackend = 'inline'

    if HYPERTOOLS_BACKEND != newbackend:
        if IS_NOTEBOOK:
            # running in Jupyter notebook
            try:
                _switch_backend_notebook(newbackend)
                HYPERTOOLS_BACKEND = newbackend
                BACKEND_WARNING = None
            except KeyError as e:
                raise ValueError(f"{newbackend} is not a valid matplotlib "
                                 f"backend for IPython") from e


def _switch_backend_regular(backend):
    if backend == 'inline':
        backend = 'module://ipykernel.pylab.backend_inline'

    try:
        plt.switch_backend(backend)
    except Exception as e:
        if isinstance(e, (ImportError, ModuleNotFoundError)):
            err_msg = (f"Failed to switch the plotting backend to "
                       f"{backend}. You may be missing required dependencies, "
                       "or this backend may not be available for your system")
        else:
            err_msg = ("An unexpected error occurred while trying to switch "
                       f"the plotting backend to {backend}")

        raise HypertoolsBackendError(err_msg) from e


def _switch_backend_notebook(backend):
    """
    Handles switching the matplotlib backend when running in a Jupyter
    notebook

    Parameters
    ----------
    backend : str
        the interactive matplotlib backend to switch to

    Returns
    -------
    None

    Notes
    -----
    1. `flush_figures` is a post-cell execution callback that
       `plt.show()`s & `plt.close()`s all figures created in a cell so
       that later `plt.plot()` calls create new figures. There's a weird
       circular matplotlib/IPython interaction where:
         - `matplotlib.pyplot` (via `IPython.core.pylabtools`) registers
            `flush_figures` when it's imported into an IPython
            environment
         - The `%matplotlib inline` magic command also registers a
           `flush_figures` call each it's run, whether or not one has
           been registered already
         - IPython runs `%matplotlib inline` if it detects
           `matplotlib.pyplot` has been imported and no backend is set
           in the same cell.
       So depending on import order, whether imports happen across
       multiple cells, and whether/when/how many times the backend has
       been switched, there may be any number of `flush_figures`
       callbacks registered. Switching to the interactive notebook
       backend unregisters one `flush_figures` callback but leaves the
       other(s), and creating an interactive figure with `flush_figures`
       registered closes the figure immediately after the cell executes
       and causes the matplotlib event loop to throw an error. So we
       need to ensure all `flush_figures` instances are unregistered
       before plotting.
    2. For some unfathomable reason, IPython prints some warning to the
       screen rather than actually using the warnings module.  We need
       to catch one of these as an exception, so we temporarily suppress
       and capture stdout.


    """
    # ipykernel is only guaranteed to be installed if running in notebook
    from ipykernel.pylab.backend_inline import flush_figures
    if backend == 'module://ipykernel.pylab.backend_inline':
        backend = 'inline'

    tmp_stdout = StringIO()
    exc = None

    with redirect_stdout(tmp_stdout):
        try:
            IPYTHON_INSTANCE.run_line_magic('matplotlib', backend)
        except KeyError as e:
            exc = e
            IPYTHON_INSTANCE.run_line_magic('matplotlib', '-l')

    output_msg = tmp_stdout.getvalue().strip()
    if exc is not None:
        # just in case something else was somehow sent to stdout while
        # redirected, or if we managed to catch a different KeyError
        backends_avail = output_msg.splitlines()[-1]
        raise ValueError(f"{backend} is not a valid IPython plotting "
                         f"backend.\n{backends_avail}") from exc

    elif output_msg.startswith('Warning: Cannot change to a different GUI toolkit'):
        try:
            _switch_backend_regular(backend)
        except HypertoolsBackendError as e:
            err_msg = (f"Failed to switch plotting backend to {backend}.\n via "
                       f"IPython with the following message:\n\t{output_msg}\n"
                       f"Fell back to switching via matplotlib and failed with "
                       f"the above error")
            raise HypertoolsBackendError(err_msg) from e

    if backend != 'inline':
        while flush_figures in IPYTHON_INSTANCE.events.callbacks['post_execute']:
            IPYTHON_INSTANCE.events.unregister('post_execute', flush_figures)


def _reset_backend_notebook(backend):
    """
    Handles resetting the matplotlib backend after displaying an
    animated/interactive plot in a Jupyter notebook by registering a
    "one-shot" self-destructing pre_cell_run callback to the next cell

    Parameters
    ----------
    backend : str
        the matplotlib backend prior to running `hypertools.plot`

    Returns
    -------
    None

    Notes
    -----
    Changing the matplotlib backend in a Jupyter notebook immediately
    closes any open figures (meaning animation and interactivity stop),
    so we can't do it as part of the function call or register it as a
    post-execution hook for the current cell. We get around this by
    registering a callback function that runs *before* the *next* cell
    is run, resets the backend, and unregisters itself. This way, the
    animation runs and the plot is interactive until the user runs the
    next cell, but the backend is reset before any code is executed. And
    because the callback "self-destructs," we won't force later figures
    to close unnecessarily ("changing" the backend to the current backend
    still does this) and doing this multiple times won't pollute the
    callback list, which can slow down cell execution.

    We also have to define and register the callback inside a wrapper
    function, since we need to reference the backend we're switching to
    using the same syntax as `matplotlib.pyplot.switch_backend`. IPython
    callbacks have to have the same signature as the prototype for the
    event they're registered to, and the pre_run_cell prototype takes no
    arguments. And since the callback needs to reference the correct
    function object in order to unregister itself, we can't just wrap it
    in `functools.partial`.
    """
    def _deferred_reset_cb():
        # TODO: add stdout redirection for printed warning message from
        #  ipykernel and fallback to plt.switch_backend
        _switch_backend_notebook(backend)
        IPYTHON_INSTANCE.events.unregister('pre_run_cell', _deferred_reset_cb)

    IPYTHON_INSTANCE.events.register('pre_run_cell', _deferred_reset_cb)


def _get_runtime_args(func, *func_args, **func_kwargs):
    """
    Does some quick introspection to determine runtime values assigned
    to all parameters of a function for a given call, whether passed as
    args, kwargs, or defaults.

    Parameters
    ----------
    func : function
        The function to introspect
    func_args : tuple
        positional arguments passed to `func` at runtime
    func_kwargs : dict
        keyword arguments passed to `func` at runtime

    Returns
    -------
    runtime_vals : dict
        parameter : value mapping of runtime values
    """
    func_signature = inspect.signature(func)
    bound_args = func_signature.bind(*func_args, **func_kwargs)
    bound_args.apply_defaults()
    return bound_args.arguments


def manage_backend(plot_func):
    """
    Decorator for hypertools.plot that prevents unexpected changes to
    matplotlib rcParams (https://github.com/ContextLab/hypertools/issues/243)
    and handles temporarily changing the matplotlib backend for
    interactive and animated plots, as necessary.

    Parameters
    ----------
    plot_func : function
        Function around which to do setup and teardown. In this case,
        `hypertools.plot`.

    Returns
    -------
    plot_wrapper : function
        The decorated function.
    """
    @wraps(plot_func)
    def plot_wrapper(*args, **kwargs):
        # record current rcParams
        curr_rcParams = mpl.rcParams.copy()
        backend_switched = False
        try:
            curr_backend = mpl.get_backend().lower()
            plot_kwargs = _get_runtime_args(plot_func, *args, **kwargs)
            if plot_kwargs.get('animate') or plot_kwargs.get('interactive'):
                tmp_backend = plot_kwargs.get('mpl_backend')
                if tmp_backend == 'auto':
                    tmp_backend = HYPERTOOLS_BACKEND.lower()

                if tmp_backend not in ('disable', curr_backend):
                    if BACKEND_WARNING is not None:
                        warnings.warn(BACKEND_WARNING)

                    switch_backend(tmp_backend)
                    backend_switched = True

            return plot_func(*args, **kwargs)

        finally:
            if backend_switched:
                reset_backend(curr_backend)

            with warnings.catch_warnings():
                # if the matplotlibrc was cached from <=v3.3.0, there's a TON
                # of harmless (as of v3.2.0) MatplotlibDeprecationWarnings
                # about rcParams fields related to axes.Axes3D objects
                warnings.simplefilter('ignore', mpl.MatplotlibDeprecationWarning)
                # restore rcParams prior to plot
                mpl.rcParams.update(**curr_rcParams)

    return plot_wrapper
