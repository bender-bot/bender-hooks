.. |bh| replace:: **bender-hooks**

===============
Getting started
===============

First of all you have to create your hook signature. It is much like an interface definition where
you only have to define the parameters and related documentation.

*definitions.py*::

    def grettings(greet, name):
        """
        Called in scripts that want to print greetings.
        
        :param greet: unicode
        :param name: unicode
        """
    
    def goodbye():
        """
        Called in scripts that want to print goodbye messages.
        """

Now you can turn your definition into a decorator using |bh|. This way your decorator will work much
like an interface.

*decorators.py*::

    import bender_hooks
    import definitions
    greetings = bender_hooks.make_decorator(definitions.greetings)
    goodbye = bender_hooks.make_decorator(definitions.goodbye)

With decorator in hands you just have to mark the functions that will be invoked through the hook.
The defined parameters are not mandatory on such functions.

*hello.py*::

    import decorators
    
    @decorators.greetings
    def a(greet, name):
        print("%s, %s!" % (greet, name))
    
    @decorators.greetings
    def b(name):
        print("Hi, %s!" % name)
    
    @decorators.greetings
    def c():
        print("Hi there!")
    
    @decorators.goodbye
    def d():
        print("Farewell!")

As all *grettings* functions are already marked, just ask |bh| to call them::

    >>> import bender_hooks
    >>> import hello
    >>> bender_hooks.call_all_hooks(hello, 'greetings', greet='Welcome', name='John')
    Welcome, John!
    Hi, John!
    Hi there!
    >>> bender_hooks.call_all_hooks(hello, 'goodbye')
    Farewell!

Sometimes it is necessary having just one implementation for a given hook. To make sure of this just
call::

    >>> bender_hooks.call_unique_hook(hello, 'greetings', greet='Welcome', name='John')
    bender_hooks.HookError: <module 'hello' from 'hello.pyc'> can implement greetings at most one time
    >>> bender_hooks.call_unique_hook(hello, 'goodbye')
    Farewell!

This is the basics! For more detailed information please refer to API documentation.
