# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import array
import mmap


import numpy as np
import pytest


from numcodecs.compat import ensure_bytes, ensure_contiguous_ndarray, PY2


def test_ensure_bytes():
    bufs = [
        b'adsdasdas',
        bytes(20),
        np.arange(100),
        array.array('l', b'qwertyuiqwertyui')
    ]
    for buf in bufs:
        b = ensure_bytes(buf)
        assert isinstance(b, bytes)


def test_ensure_contiguous_ndarray_shares_memory():
    typed_bufs = [
        ('u', 1, b'adsdasdas'),
        ('u', 1, bytes(20)),
        ('i', 8, np.arange(100, dtype=np.int64)),
        ('f', 8, np.linspace(0, 1, 100, dtype=np.float64)),
        ('i', 4, array.array('i', b'qwertyuiqwertyui')),
        ('i', 8, array.array('l', b'qwertyuiqwertyui')),
        ('u', 4, array.array('I', b'qwertyuiqwertyui')),
        ('u', 8, array.array('L', b'qwertyuiqwertyui')),
        ('f', 4, array.array('f', b'qwertyuiqwertyui')),
        ('f', 8, array.array('d', b'qwertyuiqwertyui')),
        ('u', 1, mmap.mmap(-1, 10))
    ]
    for typ, siz, buf in typed_bufs:
        a = ensure_contiguous_ndarray(buf)
        assert isinstance(a, np.ndarray)
        if PY2 and isinstance(buf, array.array):  # pragma: py3 no cover
            # array.array does not expose buffer interface on PY2 so type information
            # is not propagated correctly, so skip comparison of type and itemsize
            pass
        else:
            assert a.dtype.kind == typ
            assert a.dtype.itemsize == siz
        if PY2:  # pragma: py3 no cover
            assert np.shares_memory(a, np.getbuffer(buf))
        else:  # pragma: py2 no cover
            assert np.shares_memory(a, memoryview(buf))


def test_ensure_contiguous_ndarray_object_array_raises():
    a = np.array([u'Xin chào thế giới'], dtype=object)
    for e in [a, memoryview(a)]:
        with pytest.raises(ValueError):
            ensure_contiguous_ndarray(e)
    with pytest.raises(TypeError):
        ensure_contiguous_ndarray(a.tolist())


def test_ensure_contiguous_ndarray_memoryview_writable():
    for writeable in [False, True]:
        a = np.arange(100)
        a.setflags(write=writeable)
        m = ensure_contiguous_ndarray(a)
        assert m.flags.writeable == writeable
        m = ensure_contiguous_ndarray(memoryview(a))
        assert m.flags.writeable == writeable
        if PY2:
            m = ensure_contiguous_ndarray(np.getbuffer(a))
            assert m.flags.writeable == writeable
