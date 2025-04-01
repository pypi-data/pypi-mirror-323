#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This library is python(numpy) implementation of Welford's algorithm,
which is online and parallel algorithm for calculating variances.

Welfords method is more numerically stable than the standard method as
described in the following blog,
    * Accurately computing running variance: www.johndcook.com/blog/standard_deviation

This library is inspired by the jvf's implementation, which is implemented
without using numpy library.
    * implementaion done by jvf: github.com/jvf/welford
"""
import torch
import copy


class Welford:
    """class Welford

     Accumulator object for Welfords online / parallel variance algorithm.

    Attributes:
        count (int): The number of accumulated samples.
        mean (array(D,)): Mean of the accumulated samples.
        var_s (array(D,)): Sample variance of the accumulated samples.
        var_p (array(D,)): Population variance of the accumulated samples.
    """

    def __init__(self,
            elements=None,
            dtype=torch.float32,
            device=None
        ):
        """__init__

        Initialize with an optional data.
        For the calculation efficiency, Welford's method is not used on the initialization process.

        Args:
            elements (array(S, D)): data samples.
            dtype (torch.dtype): data type to use for calculations.
                default: torch.float32.
        """

        # Initialize instance attributes
        self.__dtype = dtype
        self.__detached = False

        if elements is None:
            self.__device = device
            self.__shape = None
            # current attribute values
            self.__count = 0
            self.__m = None
            self.__s = None
            # previous attribute values for rollbacking
            self.__count_old = None
            self.__m_old = None
            self.__s_old = None

        else:
            self.__device = elements.device if (device is None) else device
            self.__shape  = elements[0].shape
            elements = elements.to(self.__dtype).to(self.__device)
            # current attribute values
            self.__count = elements.shape[0]
            self.__m = torch.mean(elements, axis=0)
            self.__s = torch.var(elements, axis=0, unbiased=False) * elements.shape[0]
            # previous attribute values for rollbacking
            self.__count_old = None
            self.__init_old_with_nan()

    @property
    def count(self):
        return self.__count

    @property
    def mean(self):
        return self.__m

    @property
    def var_s(self):
        return self.__getvars(ddof=1)

    @property
    def var_p(self):
        return self.__getvars(ddof=0)

    def add(self, element, backup_flg=True):
        """ add

        add one data sample.

        Args:
            element (array(D, )): data sample.
            backup_flg (boolean): if True, backup previous state for rollbacking.

        """
        # Initialize if not yet.
        if self.__shape is None:
            self.__device = element.device if (self.__device is None) else self.__device
            self.__shape = element.shape
            self.__m = torch.zeros(element.shape, dtype=self.__dtype).to(self.__device)
            self.__s = torch.zeros(element.shape, dtype=self.__dtype).to(self.__device)
            self.__init_old_with_nan()
            if self.__detached:
                self.detach()
        # argument check if already initialized
        else:
            assert element.shape == self.__shape

        # backup for rollbacking
        if backup_flg:
            self.__backup_attrs()

        element = element.to(self.__dtype).to(self.__device)

        # Welford's algorithm
        self.__count += 1
        delta = element - self.__m
        self.__m += delta / self.__count
        self.__s += delta * (element - self.__m)

    def add_all(self, elements, backup_flg=False):
        """ add_all

        add multiple data samples.

        Args:
            elements (array(S, D)): data samples.
            backup_flg (boolean): if True, backup previous state for rollbacking.

        """
        if self.__shape is None:
            self.__device = elements.device if (self.__device is None) else self.__device
            self.__shape = elements.shape[1:]
            self.__m = torch.zeros(self.__shape, dtype=self.__dtype).to(self.__device)
            self.__s = torch.zeros(self.__shape, dtype=self.__dtype).to(self.__device)
            self.__init_old_with_nan()
            if self.__detached:
                self.detach()


        # backup for rollbacking
        if backup_flg:
            self.__backup_attrs()

        elements = elements.to(self.__dtype).to(self.__device)
        batch_size = elements.shape[0]

        # Compute delta and update mean and S in a batched way
        delta = elements - self.__m
        self.__m += torch.sum(delta, axis=0) / (self.__count + batch_size)
        self.__s += torch.sum(delta * (elements - self.__m), axis=0)

        self.__count += batch_size

    def rollback(self):
        self.__count = self.__count_old
        self.__m[...] = self.__m_old[...]
        self.__s[...] = self.__s_old[...]

    def merge(self, other, backup_flg=True):
        """Merge this accumulator with another one."""
        # backup for rollbacking
        if backup_flg:
            self.__backup_attrs()

        assert other.__shape == self.__shape
        assert other.__dtype == self.__dtype

        count = self.__count + other.__count
        delta = self.__m - other.__m
        delta2 = delta * delta
        m = (self.__count * self.__m + other.__count * other.__m) / count
        s = self.__s + other.__s + delta2 * (self.__count * other.__count) / count

        self.__count = count
        self.__m = m
        self.__s = s

    def __getvars(self, ddof):
        if self.__count <= 0:
            return None
        min_count = ddof
        if self.__count <= min_count:
            return torch.full(self.__shape, torch.nan, dtype=self.__dtype).to(self.__device)
        else:
            return self.__s / (self.__count - ddof)

    def __backup_attrs(self):
        if self.__shape is None:
            pass
        else:
            self.__count_old = self.__count
            self.__m_old[...] = self.__m[...]
            self.__s_old[...] = self.__s[...]

    def __init_old_with_nan(self):
        self.__m_old = torch.empty(self.__shape, dtype=self.__dtype).to(self.__device)
        self.__m_old[...] = torch.nan
        self.__s_old = torch.empty(self.__shape, dtype=self.__dtype).to(self.__device)
        self.__s_old[...] = torch.nan



    def to_inplace(self, device=None, dtype=None):
        """Move the Welford statistics to the specified device and dtype (inplace)."""
        if device is not None:
            self.__device = torch.device(device)
            if self.__m is not None:
                self.__m = self.__m.to(self.__device)
                self.__s = self.__s.to(self.__device)
                self.__m_old = self.__m_old.to(self.__device)
                self.__s_old = self.__s_old.to(self.__device)

        if dtype is not None:
            self.__dtype = dtype
            if self.__m is not None:
                self.__m = self.__m.to(self.__dtype)
                self.__s = self.__s.to(self.__dtype)
                self.__m_old = self.__m_old.to(self.__dtype)
                self.__s_old = self.__s_old.to(self.__dtype)

        return self
    def to(self, device=None, dtype=None):
        """Move the Welford statistics to the specified device and dtype (copy)."""
        new_w: Welford = copy.deepcopy(self)
        new_w.to_inplace(device=device, dtype=dtype)
        return new_w

    def detach(self):
        self.__detached = True
        if not (self.__shape is None):
            self.__m = self.__m.detach()
            self.__s = self.__s.detach()
            self.__m_old = self.__m_old.detach()
            self.__s_old = self.__s_old.detach()
        return self
