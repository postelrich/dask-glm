from __future__ import absolute_import, division, print_function

from dask_glm.utils import dot, exp, log1p, sigmoid


class Logistic(object):
    @staticmethod
    def loglike(Xbeta, y):
        enXbeta = exp(-Xbeta)
        return (Xbeta + log1p(enXbeta)).sum() - dot(y, Xbeta)

    @staticmethod
    def pointwise_loss(beta, X, y):
        '''Logistic Loss, evaluated point-wise.'''
        beta, y = beta.ravel(), y.ravel()
        Xbeta = X.dot(beta)
        return Logistic.loglike(Xbeta, y)

    @staticmethod
    def pointwise_gradient(beta, X, y):
        '''Logistic gradient, evaluated point-wise.'''
        beta, y = beta.ravel(), y.ravel()
        Xbeta = X.dot(beta)
        return Logistic.gradient(Xbeta, X, y)

    @staticmethod
    def gradient(Xbeta, X, y):
        p = sigmoid(Xbeta)
        return dot(X.T, p - y)

    @staticmethod
    def hessian(Xbeta, X):
        p = sigmoid(Xbeta)
        return dot(p * (1 - p) * X.T, X)


class Normal(object):
    @staticmethod
    def loglike(Xbeta, y):
        return ((y - Xbeta) ** 2).sum()

    @staticmethod
    def pointwise_loss(beta, X, y):
        beta, y = beta.ravel(), y.ravel()
        Xbeta = X.dot(beta)
        return Normal.loglike(Xbeta, y)

    @staticmethod
    def pointwise_gradient(beta, X, y):
        beta, y = beta.ravel(), y.ravel()
        Xbeta = X.dot(beta)
        return Normal.gradient(Xbeta, X, y)

    @staticmethod
    def gradient(Xbeta, X, y):
        return 2 * dot(X.T, Xbeta) - 2 * dot(X.T, y)

    @staticmethod
    def hessian(Xbeta, X):
        return 2 * dot(X.T, X)


class Poisson(object):
    """
    This implements Poisson regression for count data.
    See https://en.wikipedia.org/wiki/Poisson_regression.
    """

    @staticmethod
    def loglike(Xbeta, y):
        eXbeta = exp(Xbeta)
        yXbeta = y * Xbeta
        return (eXbeta - yXbeta).sum()

    @staticmethod
    def pointwise_loss(beta, X, y):
        beta, y = beta.ravel(), y.ravel()
        Xbeta = X.dot(beta)
        return Poisson.loglike(Xbeta, y)

    @staticmethod
    def pointwise_gradient(beta, X, y):
        beta, y = beta.ravel(), y.ravel()
        Xbeta = X.dot(beta)
        return Poisson.gradient(Xbeta, X, y)

    @staticmethod
    def gradient(Xbeta, X, y):
        eXbeta = exp(Xbeta)
        return dot(X.T, eXbeta - y)

    @staticmethod
    def hessian(Xbeta, X):
        eXbeta = exp(Xbeta)
        x_diag_eXbeta = eXbeta[:, None] * X
        return dot(X.T, x_diag_eXbeta)
