from abc import ABCMeta, abstractmethod


class CRUDBase(object):
    """
    Many of the sub-components of OrderSystem follow a CRUD style of operation. To unify the programming experience,
    all sub-components that follow this style will extend CRUDBase, which is a collection of methods that every
    CRUD-type class should consist of
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def index(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass
