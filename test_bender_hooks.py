import bender_hooks as hooks
import pytest


def test_simple_hook():

    def my_spec(x, y):
        """spec docs"""

    dec = hooks.make_decorator(my_spec)

    class Impl(object):
        @dec
        def my_hook_1(self, x, y):
            assert (x, y) == (1, 20)
            return 'my_hook_1'

        @dec
        def my_hook_2(self, x):
            assert x == 1
            return 'my_hook_2'

        @dec
        def my_hook_3(self):
            return 'my_hook_3'

    assert Impl.my_hook_1.hook_name == 'my_spec'
    assert Impl.my_hook_2.hook_name == 'my_spec'
    assert Impl.my_hook_3.hook_name == 'my_spec'
    impl = Impl()
    assert hooks.call(impl.my_hook_1, x=1, y=20) == 'my_hook_1'
    assert hooks.call(impl.my_hook_2, x=1, y=20) == 'my_hook_2'
    assert hooks.call(impl.my_hook_3, x=1, y=20) == 'my_hook_3'


def test_hook_with_input():

    def my_spec(x, y):
        """spec docs"""

    dec = hooks.make_decorator(my_spec, inputs='title')

    @dec('Hook 1')
    def my_hook_1(x, y):
        assert x == 1
        assert y == 20
        return 'my_hook_1'

    @dec('Hook 2')
    def my_hook_2(x):
        assert x == 1
        return 'my_hook_2'

    assert hooks.call(my_hook_1, x=1, y=20) == 'my_hook_1'
    assert my_hook_1.inputs['title'] == 'Hook 1'

    assert hooks.call(my_hook_2, x=1, y=20) == 'my_hook_2'
    assert my_hook_2.inputs['title'] == 'Hook 2'


@pytest.mark.parametrize('spec', [
    lambda *args: None,
    lambda *args, **kwargs: None,
    lambda **kwargs: None,
    lambda x=10: None,
])
def test_invalid_specs(spec):
    with pytest.raises(AssertionError):
        hooks.make_decorator(spec)


def test_hooks_call():
    def spec_a(x, y):
        """spec docs"""
    def spec_b(z):
        """spec docs"""
    a = hooks.make_decorator(spec_a)
    b = hooks.make_decorator(spec_b)

    calls = []

    class Impl(object):

        @a
        def hook_1(self):
            calls.append('hook_1')

        @a
        def hook_2(self):
            calls.append('hook_2')

        @b
        def hook_3(self):
            calls.append('hook_3')
            return 'hook_3'

    impl = Impl()
    assert hooks.find_hooks(impl, 'spec_a') == [impl.hook_1, impl.hook_2]
    assert hooks.find_hooks(impl, 'spec_b') == [impl.hook_3]

    assert hooks.call_all_hooks(impl, 'spec_a', x=1, y=20) is None
    assert hooks.call_all_hooks(impl, 'spec_b', z=40) is None
    assert calls == ['hook_1', 'hook_2', 'hook_3']

    calls[:] = []
    assert hooks.call_unique_hook(impl, 'spec_b', z=40) == 'hook_3'
    assert calls == ['hook_3']
    with pytest.raises(hooks.HookError):
        hooks.call_unique_hook(impl, 'spec_a', x=1, y=20)


def test_invalid_impl_signature():
    def spec(x, y):
        """spec docs"""
    dec = hooks.make_decorator(spec)

    with pytest.raises(hooks.HookError):
        @dec
        def foo(xx, yy):
            pass

    with pytest.raises(hooks.HookError):
        class Impl(object):
            @dec
            def foo(self, xx, yy):
                pass
