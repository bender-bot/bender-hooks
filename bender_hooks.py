import functools
import inspect


def _get_only_args_spec(f):
    spec = inspect.getargspec(f)
    assert spec.varargs is None, 'func %s cannot contain *args' % f
    assert spec.keywords is None, 'func %s cannot contain ***kwargs' % f
    assert spec.defaults is None, 'func %s cannot contain defaults' % f
    return spec


def make_decorator(hook_decl, inputs=()):
    '''
    Responsible for turning a hook declaration into a decorator.

    :param callable hook_decl:

        The definition that will be turn into a decorator. Example::

            def grettings(greet, name):
                """
                Called in scripts that want to print greetings.

                :param greet: unicode
                :param name: unicode
                """

        If any code is placed inside the given definition it will be ignored.

    :type inputs: tuple | list
    :param inputs:
        Parameters that must be given to decorator. Example::

            dec = bender_hooks.make_decorator(foo, inputs=('alpha', 'bravo'))

            @dec('A', 'B')
            def my_func():
                pass

            my_func.inputs['alpha'] == 'A'
            my_func.inputs['bravo'] == 'B'

    :rtype: callable
    :returns:
        The created decorator.

    :raises HookError: when given arguments are not valid.
    '''
    hook_spec = _get_only_args_spec(hook_decl)
    inputs = inputs if type(inputs) in (tuple, list) else [inputs]

    def make_decorated(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        decorated.hook_name = hook_decl.__name__
        decorated.spec = spec = _get_only_args_spec(f)

        diff_specs = set(spec.args).difference(hook_spec.args)
        diff_specs.discard('self')
        if diff_specs:
            msg = 'function <{name}>: argument names {args} are not valid for '\
                  'hook "{hook}"'
            raise HookError(msg.format(name=f.__name__, args=list(diff_specs),
                                       hook=hook_decl.__name__))
        return decorated

    if inputs:
        def decorator(*args):
            def inner(f):
                wrapped = make_decorated(f)
                wrapped.inputs = dict((k, args[i]) for (i, k) in enumerate(inputs))
                return wrapped
            return inner
    else:
        def decorator(f):
            inner = make_decorated(f)
            inner.inputs = {}
            return inner

    return decorator


def call(hook, **kwargs):
    '''
    Responsible for invoking given ``hook``. As hooks not necessarily defines all arguments, this
    function will make sure that the given one will satisfy the ``hook``. Example::

        def foo(a, b):
            """
            My decorator definition.
            """

        # Creating decorator.
        dec = bender_hooks.make_decorator(foo)

        # Decorating. Only one parameter defined.
        @foo
        def bar(b):
            print(b)

        # Invoking.
        bender_hooks.call(bar, a=1) # Invalid: ``a`` is not defined at ``bar``
        bender_hooks.call(bar, b=2) # Valid
        bender_hooks.call(bar, c=3) # Invalid: ``c`` is not defined at ``bar`` neither ``foo``
        bender_hooks.call(bar, a=1, b=2) # Valid: ``a`` is defined at ``foo`` but will be ignored.
        bender_hooks.call(bar, b=2, c=3) # Invalid
        bender_hooks.call(bar, a=1, b=2, c=3) # Invalid

    :param callable hook:
        Already decorated function.

    :returns:
        It depends on what will be returned by given ``hook``.

    :raises HookError: if given ``hook`` is not decorated.
    '''
    if not hasattr(hook, 'hook_name'):
        raise HookError('%s is not a hook' % hook)
    if hook.spec.args:
        accepts_kwargs = set(hook.spec.args).intersection(kwargs)
        new_kwargs = dict((k, kwargs[k]) for k in accepts_kwargs)
    else:
        new_kwargs = {}
    return hook(**new_kwargs)


def find_hooks(obj, hook_name):
    '''
    Responsible for search at ``obj`` hooks with the given ``hook_name``.

    :param obj:
        Object (can be a module or instance) to search for hooks.

    :param unicode hook_name:
        Name of hook to search.

    :rtype: list(callable)
    :returns:
        All hooks found into the given ``obj``.
    '''
    result = []
    for name in dir(obj):
        value = getattr(obj, name)
        if getattr(value, 'hook_name', None) == hook_name:
            result.append(value)
    return result


def call_all_hooks(obj, hook_name, **kwargs):
    '''
    Responsible for search and invoke all hooks with the given ``hook_name`` under ``obj``.

    .. seealso:: :func:`.find_hooks`
    .. seealso:: :func:`.call`
    '''
    for hook in find_hooks(obj, hook_name):
        call(hook, **kwargs)
    return None


def call_unique_hook(obj, hook_name, **kwargs):
    '''
    Responsible for search and invoke a hook with the given ``hook_name`` under ``obj``, making sure
    that only one hook exists.

    :raises HookError: if more than one hooks are found.

    .. seealso:: :func:`.find_hooks`
    .. seealso:: :func:`.call`
    '''
    found = find_hooks(obj, hook_name)
    if len(found) > 1:
        raise HookError(
            '%s can implement %s at most one time' % (obj, hook_name))
    elif len(found) == 1:
        return call(found[0], **kwargs)


class HookError(RuntimeError):
    '''
    Error raised for expected and known cases of |bh|.
    '''
