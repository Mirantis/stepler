import pytest

from stepler.third_party import context


class Error(Exception):
    pass


class EnterError(Exception):
    pass


class ExitError(Exception):
    pass


@context.context
def foo():
    bar = []
    bar.append('enter')
    yield bar
    bar.append('exit')


def test_normal_pass_enter():
    with foo() as y:
        assert 'enter' in y


def test_normal_pass_exit():
    with foo() as y:
        pass
    assert 'exit' in y


def test_raise_inside_context():
    with pytest.raises(Exception) as e:
        with foo():
            raise Error('error')
    assert e.type is Error


def test_raise_inside_context_exit_executed():
    try:
        with foo() as y:
            raise Error('error')
    except Exception:
        pass
    assert 'exit' in y


def test_tb_correct():
    with pytest.raises(Exception) as e:
        with foo():
            pass
            raise Error('error')
            pass
    assert "raise Error('error')" in str(e.traceback[0].statement)


def test_raise_on_enter():
    @context.context
    def foo():
        raise EnterError()
        yield

    with pytest.raises(EnterError):
        with foo():
            pass


def test_raise_on_exit():
    @context.context
    def foo():
        yield
        raise ExitError()

    with pytest.raises(ExitError):
        with foo():
            pass


def test_raise_inside_context_and_on_exit():
    @context.context
    def foo():
        yield
        raise ExitError()

    with pytest.raises(Error):
        with foo():
            raise Error
