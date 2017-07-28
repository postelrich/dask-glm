import pytest
import numpy as np
import dask.array as da

from dask_glm import utils
from dask.array.utils import assert_eq


def test_normalize_normalizes():
    @utils.normalize
    def do_nothing(X, y):
        return np.array([0.0, 1.0, 2.0])
    X = da.from_array(np.array([[1, 0, 0], [1, 2, 2]]), chunks=(2, 3))
    y = da.from_array(np.array([0, 1, 0]), chunks=(3, ))
    res = do_nothing(X, y)
    np.testing.assert_equal(res, np.array([-3.0, 1.0, 2.0]))


def test_normalize_doesnt_normalize():
    @utils.normalize
    def do_nothing(X, y):
        return np.array([0.0, 1.0, 2.0])
    X = da.from_array(np.array([[1, 0, 0], [1, 2, 2]]), chunks=(2, 3))
    y = da.from_array(np.array([0, 1, 0]), chunks=(3, ))
    res = do_nothing(X, y, normalize=False)
    np.testing.assert_equal(res, np.array([0, 1, 2]))


def test_normalize_normalizes_if_intercept_not_present():
    @utils.normalize
    def do_nothing(X, y):
        return np.array([0.0, 1.0, 2.0])
    X = da.from_array(np.array([[1, 0, 0], [3, 9.0, 2]]), chunks=(2, 3))
    y = da.from_array(np.array([0, 1, 0]), chunks=(3, ))
    res = do_nothing(X, y)
    np.testing.assert_equal(res, np.array([0, 1 / 4.5, 2]))


def test_normalize_raises_if_multiple_constants():
    @utils.normalize
    def do_nothing(X, y):
        return np.array([0.0, 1.0, 2.0])
    X = da.from_array(np.array([[1, 2, 3], [1, 2, 3]]), chunks=(2, 3))
    y = da.from_array(np.array([0, 1, 0]), chunks=(3, ))
    with pytest.raises(ValueError):
        res = do_nothing(X, y)


def test_add_intercept():
    X = np.zeros((4, 4))
    result = utils.add_intercept(X)
    expected = np.array([
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
    ], dtype=X.dtype)
    assert_eq(result, expected)


def test_add_intercept_dask():
    X = da.from_array(np.zeros((4, 4)), chunks=(2, 4))
    result = utils.add_intercept(X)
    expected = da.from_array(np.array([
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
    ], dtype=X.dtype), chunks=2)
    assert_eq(result, expected)


def test_sparse():
    sparse = pytest.importorskip('sparse')
    from sparse.utils import assert_eq
    x = sparse.COO({(0, 0): 1, (1, 2): 2, (2, 1): 3})
    y = x.todense()
    assert utils.sum(x) == utils.sum(x.todense())
    for func in [utils.sigmoid, utils.sum, utils.exp]:
        assert_eq(func(x), func(y))


@pytest.fixture
def foo_class():
    class FooClass(utils.RegistryClass):
        pass

    class BarClass(FooClass):
        name = 'bar'
    return FooClass


def test_registryclass_get_passes_through_instance(foo_class):
    x = foo_class()
    assert utils.RegistryClass.get(x) == x


def test_regularizer_get_unnamed_raises(foo_class):
    with pytest.raises(KeyError):
        foo_class().get('foobar')


def test_regularizer_gets_from_name(foo_class):
    assert isinstance(foo_class().get('bar'), foo_class)
