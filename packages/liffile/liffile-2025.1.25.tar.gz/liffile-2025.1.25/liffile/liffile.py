# liffile.py

# Copyright (c) 2023-2025, Christoph Gohlke
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Read Leica image files (LIF).

Liffile is a Python library to read image and metadata from Leica image files
(LIF). LIF files are written by LAS X software to store collections of images
and metadata from microscopy experiments.

:Author: `Christoph Gohlke <https://www.cgohlke.com>`_
:License: BSD 3-Clause
:Version: 2025.1.25

Quickstart
----------

Install the liffile package and all dependencies from the
`Python Package Index <https://pypi.org/project/liffile/>`_::

    python -m pip install -U liffile[all]

See `Examples`_ for using the programming interface.

Source code and support are available on
`GitHub <https://github.com/cgohlke/liffile>`_.

Requirements
------------

This revision was tested with the following requirements and dependencies
(other versions may work):

- `CPython <https://www.python.org>`_ 3.10.11, 3.11.9, 3.12.8, 3.13.1 64-bit
- `NumPy <https://pypi.org/project/numpy>`_ 2.2.2
- `Xarray <https://pypi.org/project/xarray>`_ 2025.1.1 (recommended)
- `Matplotlib <https://pypi.org/project/matplotlib/>`_ 3.10.0 (optional)
- `Tifffile <https://pypi.org/project/tifffile/>`_ 2025.1.10 (optional)

Revisions
---------

2025.1.25

- Initial alpha release.

Notes
-----

`Leica Microsystems GmbH <https://www.leica.com/>`_ is a manufacturer of
microscopes and scientific instruments for the analysis of micro and
nanostructures.

This library is in its early stages of development. It is not feature-complete.
Large, backwards-incompatible changes may occur between revisions.

Specifically, the following features are currently not implemented:
related Leica file formats (XLEF, XLLF, LOF, LIFEXT), image mosaics and
pyramids, partial image reads, reading non-image data like FLIM/TCSPC,
and heterogeneous channels.

This library has been tested with a limited number of version 2 files only.

The Leica Image File format is documented at:

- Leica Image File Formats - LIF, XLEF, XLLF, LOF. Version 3.2.
  Leica Microsystems GmbH. 21 September 2016.
- Annotations to Leica Image File Formats for LAS X Version 3.x. Version 1.4.
  Leica Microsystems GmbH. 24 August 2016.

Other implementations for reading Leica LIF files are
`readlif <https://github.com/Arcadia-Science/readlif>`_ and
`Bio-Formats <https://github.com/ome/bioformats>`_ .

Examples
--------

Read image and metadata from a LIF file:

>>> with LifFile('tests/data/FLIM.lif') as lif:
...     for image in lif.series:
...         name = image.name
...     image = lif.series['Fast Flim']
...     assert image.shape == (1024, 1024)
...     assert image.dims == ('Y', 'X')
...     lifetimes = image.asxarray()
...
>>> lifetimes
<xarray.DataArray 'Fast Flim' (Y: 1024, X: 1024)> Size: 2MB
array([[...]],
      shape=(1024, 1024), dtype=float16)
    Coordinates:
      * Y        (Y) float64... 0.0005564
      * X        (X) float64... 0.0005564
Attributes...
    path:           FLIM_testdata.lif/sample1_slice1/FLIM Compressed/Fast Flim
    F16:            {'Name': 'F16',...
    TileScanInfo:   {'Tile': {'FieldX': 0,...
    ViewerScaling:  {'ChannelScalingInfo': {...

View the image and metadata in a LIF file from the console::

    $ python -m liffile tests/data/FLIM.lif

"""

from __future__ import annotations

__version__ = '2025.1.25'

__all__ = [
    '__version__',
    'imread',
    'logger',
    'LifFile',
    'LifImage',
    'LifImageSeries',
    'LifFileError',
    'LifMemoryBlock',
]

import logging
import os
import re
import struct
import sys
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property
from typing import TYPE_CHECKING, final, overload
from xml.etree import ElementTree

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from typing import IO, Any, Literal

    from numpy.typing import DTypeLike, NDArray
    from xarray import DataArray

    OutputType = str | IO[bytes] | NDArray[Any] | None

import numpy


@overload
def imread(
    file: str | os.PathLike[Any] | IO[bytes],
    /,
    *,
    series: int | str = 0,
    asrgb: bool = True,
    squeeze: bool = True,
    out: OutputType = None,
    asxarray: Literal[False] = ...,
) -> NDArray[Any]: ...


@overload
def imread(
    file: str | os.PathLike[Any] | IO[bytes],
    /,
    *,
    series: int | str = 0,
    asrgb: bool = True,
    squeeze: bool = True,
    out: OutputType = None,
    asxarray: Literal[True] = ...,
) -> DataArray: ...


def imread(
    file: str | os.PathLike[Any] | IO[bytes],
    /,
    *,
    series: int | str = 0,
    asrgb: bool = True,
    squeeze: bool = True,
    out: OutputType = None,
    asxarray: bool = False,
) -> NDArray[Any] | DataArray:
    """Return image from file.

    Dimensions are returned in order stored in file.

    Parameters:
        file:
            File name or seekable binary stream.
        series:
            Index or name of image to return.
            By default, the first image in the file is returned.
        asrgb:
            Return RGB samples in RGB order, not storage order.
            If true, the returned array data might not be contiguous.
        squeeze:
            Remove dimensions of length one from images.
        out:
            Specifies where to copy image data.
            If ``None``, create a new NumPy array in main memory.
            If ``'memmap'``, directly memory-map the image data in the file.
            If a ``numpy.ndarray``, a writable, initialized array
            of compatible shape and dtype.
            If a ``file name`` or ``open file``, create a memory-mapped
            array in the specified file.
        asxarray:
            Return image data as xarray.DataArray instead of numpy.ndarray.

    Returns:
        :
            Image data as numpy array or xarray DataArray.

    """
    data: NDArray[Any] | DataArray
    with LifFile(file, squeeze=squeeze) as lif:
        image = lif.series[series]
        if asxarray:
            data = image.asxarray(asrgb=asrgb, out=out)
        else:
            data = image.asarray(asrgb=asrgb, out=out)
    return data


class LifFileError(Exception):
    """Exception to indicate invalid Leica Image File structure."""


@final
class LifFile:
    """Leica Image File.

    ``LifFile`` instances are not thread-safe. All attributes are read-only.

    ``LifFile`` instances must be closed with :py:meth:`LifFile.close`,
    which is automatically called when using the 'with' context manager.

    All properties are read-only.

    Parameters:
        file:
            File name or seekable binary stream.
        mode:
            File open mode if `file` is file name.
            The default is 'r'. Files are always opened in binary mode.
        squeeze:
            Remove dimensions of length one from images.

    Raises:
        LifFileError: File is not a Leica image file or is corrupted.

    """

    filename: str
    """Name of file or empty if binary stream."""

    version: int
    """File version."""

    name: str
    """Name of file from XML header."""

    datetime: datetime
    """File creation date from XML header."""

    xml_header: str
    """XML object description."""

    xml_element: ElementTree.Element
    """XML header root element."""

    memory_blocks: dict[str, LifMemoryBlock]
    """Object memory blocks."""

    _fh: IO[bytes]
    _close: bool  # file needs to be closed
    _squeeze: bool  # remove dimensions of length one from images

    def __init__(
        self,
        file: str | os.PathLike[Any] | IO[bytes],
        /,
        *,
        squeeze: bool = True,
        mode: Literal['r', 'r+'] | None = None,
    ) -> None:
        if isinstance(file, (str, os.PathLike)):
            if mode is None:
                mode = 'r'
            else:
                if mode[-1:] == 'b':
                    mode = mode[:-1]  # type: ignore[assignment]
                if mode not in {'r', 'r+'}:
                    raise ValueError(f'invalid mode {mode!r}')
            self.filename = os.fspath(file)
            self._close = True
            self._fh = open(self.filename, mode + 'b')
        elif hasattr(file, 'seek'):
            self.filename = ''
            self._close = False
            self._fh = file
        else:
            raise ValueError(f'cannot open file of type {type(file)}')

        self._squeeze = bool(squeeze)

        fh = self._fh
        # binary header
        try:
            id0, size, id1, lenxml = struct.unpack('<IIBI', fh.read(13))
        except Exception as exc:
            self.close()
            raise LifFileError('not a LIF file') from exc
        if id0 != 0x70 or id1 != 0x2A or size != 2 * lenxml + 5:
            self.close()
            raise LifFileError(
                f'not a LIF file {id0=:02X}, {size=}, {id1=:02X}, {lenxml=}'
            )
        self.xml_header = fh.read(lenxml * 2).decode('utf-16-le')
        self.xml_element = ElementTree.fromstring(self.xml_header)
        self.version = int(self.xml_element.attrib['Version'])

        element = self.xml_element.find('./Element')
        if element is not None:
            self.name = element.attrib.get('Name', '')
        else:
            self.name = ''

        element = self.xml_element.find('./Element/Data/Experiment/TimeStamp')
        if element is not None:
            high = int(element.attrib['HighInteger'])
            low = int(element.attrib['LowInteger'])
            sec = (((high << 32) + low) - 116444736000000000) // 10000000
            self.datetime = datetime.fromtimestamp(sec, timezone.utc)
        else:
            self.datetime = datetime.fromtimestamp(0)

        self.memory_blocks = {}
        while True:
            try:
                memoryblock = LifMemoryBlock(fh, self.version)
            except OSError:
                break
            self.memory_blocks[memoryblock.id] = memoryblock

    @property
    def filehandle(self) -> IO[bytes]:
        """File handle."""
        return self._fh

    @cached_property
    def series(self) -> LifImageSeries:
        """Return image series in file."""
        return LifImageSeries(self)

    @property
    def flim_rawdata(self) -> dict[str, Any]:
        """Return settings from SingleMoleculeDetection/RawData XML element."""
        # TODO: move this into LifFlimCompressed class
        rawdata = self.xml_element.find(
            './/Element/Data/SingleMoleculeDetection/Dataset/RawData'
        )
        if rawdata is None:
            return {}
        flim_rawdata: dict[str, Any] = xml2dict(rawdata)['RawData']
        flim_rawdata.pop('Channels', None)
        flim_rawdata.pop('Dimensions', None)
        return flim_rawdata

    def close(self) -> None:
        """Close file handle and free resources."""
        if self._close:
            try:
                self._fh.close()
            except Exception:
                pass

    def __enter__(self) -> LifFile:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        if self.filename:
            name = os.path.basename(self.filename)
        elif hasattr(self._fh, 'name') and self._fh.name:
            name = os.path.basename(self._fh.name)
        else:
            name = self.name
        return f'<{self.__class__.__name__} {name!r}>'

    def __str__(self) -> str:
        return indent(
            repr(self),
            f'filename: {self.filename}',
            f'datetime: {self.datetime}',
            *(repr(image) for image in self.series),
        )


@final
class LifImage:
    """Single image in LIF file.

    All properties are read-only.

    Parameters:
        parent:
            Underlying LIF file.
        xml_element:
            XML element of image.
        path:
            Path of image in image tree.

    """

    parent: LifFile
    """Underlying LIF file."""

    xml_element: ElementTree.Element
    """XML element of image."""

    path: str
    """Path of image in image tree."""

    def __init__(
        self,
        parent: LifFile,
        xml_element: ElementTree.Element,
        path: str,
        /,
    ) -> None:
        self.parent = parent
        self.xml_element = xml_element
        self.path = path

    @property
    def name(self) -> str:
        """Name of image."""
        return os.path.split(self.path)[-1]

    @cached_property
    def _dimensions(self) -> tuple[LifDimension, ...]:
        """Dimension properties from DimensionDescription XML element."""
        dimensions = []
        labels = set()
        for i, dim in enumerate(
            self.xml_element.findall(
                './Data/Image/ImageDescription/Dimensions/DimensionDescription'
            )
        ):
            dim_id = int(dim.attrib['DimID'])
            label = DIMENSION_ID.get(dim_id, 'Q')
            if label in labels:
                logger().warning(f'duplicate dimension {label!r}')
                label = f'{label}{i}'
            labels.add(label)
            dimensions.append(
                LifDimension(
                    label,
                    dim_id,
                    int(dim.attrib['NumberOfElements']),
                    float(dim.attrib['Origin']),
                    float(dim.attrib['Length']),
                    dim.attrib['Unit'],
                    int(dim.attrib['BytesInc']),
                    int(dim.attrib['BitInc']),
                )
            )
        return tuple(
            sorted(dimensions, key=lambda x: x.bytes_inc, reverse=True)
        )

    @cached_property
    def _channels(self) -> tuple[LifChannel, ...]:
        """Channel properties from ChannelDescription XML element."""
        channels = []
        for channel in self.xml_element.findall(
            './Data/Image/ImageDescription/Channels/ChannelDescription'
        ):
            data_type = int(channel.attrib['DataType'])
            resolution = int(channel.attrib['Resolution'])

            if data_type == 0:
                dtype = 'u'
            elif data_type == 1:
                dtype = 'f'
            else:
                raise ValueError(f'invalid {data_type=}')

            if 0 < resolution <= 8:
                itemsize = 1
                if dtype == 'f':
                    raise ValueError(f'invalid dtype {dtype}{itemsize}')
            elif resolution <= 16:
                itemsize = 2
            elif resolution <= 32:
                itemsize = 4
            elif resolution <= 64:
                itemsize = 8
            else:
                raise ValueError(f'invalid {resolution=}')

            channels.append(
                LifChannel(
                    numpy.dtype(f'<{dtype}{itemsize}'),
                    data_type,
                    int(channel.attrib['ChannelTag']),
                    resolution,
                    channel.attrib['NameOfMeasuredQuantity'],
                    float(channel.attrib['Min']),
                    float(channel.attrib['Max']),
                    channel.attrib['Unit'],
                    channel.attrib['LUTName'],
                    bool(channel.attrib['IsLUTInverted']),
                    int(channel.attrib['BytesInc']),
                    int(channel.attrib['BitInc']),
                )
            )

        return tuple(channels)

    @cached_property
    def dtype(self) -> numpy.dtype[Any]:
        """Numpy data type of image array.

        Raises:
            ValueError: channel data types are heterogeneous.

        """
        channels = self._channels
        dtype = channels[0].dtype

        if len(channels) > 1 and any(dtype != c.dtype for c in channels):
            raise ValueError(
                'heterogeneous channel data types not supported. '
                'Please share the file at https://github.com/cgohlke/liffile'
            )

        return dtype

    @cached_property
    def sizes(self) -> dict[str, int]:
        """Map dimension names to lengths."""
        squeeze = self.parent._squeeze
        channels = self._channels
        nchannels = len(channels)
        if nchannels <= 1:
            return {
                dim.label: dim.number_elements
                for dim in self._dimensions
                if not squeeze or dim.number_elements > 1
            }

        # insert channels where other dimensions are discontiguous
        # TODO: verify with channel BytesInc
        sizes = {}
        stride = self.dtype.itemsize
        ch = 0
        for i, dim in enumerate(reversed(self._dimensions)):
            if squeeze and dim.number_elements < 2:
                continue
            if stride != dim.bytes_inc:
                # assert stride * len(channels) == d[2]
                size = dim.bytes_inc // stride
                ax = 'S' if i == 0 else 'C' if 'C' not in sizes else f'C{ch}'
                if ax != 'S':
                    ch += 1
                sizes[ax] = size
                nchannels //= size
            sizes[dim.label] = dim.number_elements
            stride = dim.number_elements * dim.bytes_inc
        if nchannels > 1:
            ax = 'C' if 'C' not in sizes else f'C{ch}'
            sizes[ax] = nchannels

        return dict(reversed(list(sizes.items())))

    @property
    def shape(self) -> tuple[int, ...]:
        """Shape of image."""
        return tuple(self.sizes.values())

    @property
    def dims(self) -> tuple[str, ...]:
        """Name of dimensions in image."""
        return tuple(self.sizes.keys())

    @property
    def ndim(self) -> int:
        """Number of image dimensions."""
        return len(self.sizes)

    @property
    def nbytes(self) -> int:
        """Number of bytes consumed by image."""
        size = 1
        for i in self.sizes.values():
            size *= int(i)
        return size * self.dtype.itemsize

    @property
    def size(self) -> int:
        """Number of elements in image."""
        size = 1
        for i in self.sizes.values():
            size *= int(i)
        return size

    @property
    def itemsize(self) -> int:
        """Length of one array element in bytes."""
        return self.dtype.itemsize

    @cached_property
    def coords(self) -> dict[str, NDArray[Any]]:
        """Mapping of image dimension names to coordinate variables."""
        # TODO: add channel names. Channels may be in several dimensions
        squeeze = self.parent._squeeze
        coords = {}
        for dim in self._dimensions:
            if squeeze and dim.number_elements == 1:
                continue
            coords[dim.label] = numpy.linspace(
                dim.origin, dim.length, dim.number_elements, endpoint=True
            )
        return coords

    @cached_property
    def attrs(self) -> dict[str, Any]:
        """Image metadata from Attachment XML elements."""
        attrs = {'path': self.parent.name + '/' + self.path}
        attrs.update(
            (attach.attrib['Name'], xml2dict(attach)['Attachment'])
            for attach in self.xml_element.findall('./Data/Image/Attachment')
        )
        return attrs

    @cached_property
    def memory_block(self) -> LifMemoryBlock:
        """Memory block containing image data."""
        memory = self.xml_element.find('./Memory')
        if memory is None:
            raise IndexError('Memory element not found in XML')
        mbid = memory.get('MemoryBlockID')
        if mbid is None:
            raise IndexError('MemoryBlockID attribute not found in XML')
        return self.parent.memory_blocks[mbid]

    @property
    def timestamps(self) -> NDArray[numpy.datetime64]:
        """Return time stamps of frames from TimeStampList XML element."""
        timestamp = self.xml_element.find('./Data/Image/TimeStampList')
        if timestamp is None:
            return numpy.asarray([], dtype=numpy.datetime64)
        timestamps: Any
        if timestamp.find('./TimeStamp') is not None:
            # LAS < 3.1
            text = ElementTree.tostring(timestamp).decode()
            timestamps = numpy.fromstring(
                ' '.join(re.findall(r'HighInteger="(\d+)"', text)),
                dtype=numpy.uint64,
                sep=' ',
            )
            timestamps <<= 32
            timestamps += numpy.fromstring(
                ' '.join(re.findall(r'LowInteger="(\d+)"', text)),
                dtype=numpy.uint32,
                sep=' ',
            )
        elif timestamp.text is not None:
            # LAS >= 3.1
            timestamps = numpy.fromiter(
                (int(x, 16) for x in timestamp.text.split()),
                dtype=numpy.uint64,
            )
        else:
            return numpy.asarray([], dtype=numpy.datetime64)
        # FILETIME to POSIX
        timestamps -= 116444736000000000
        timestamps //= 10000
        return timestamps.astype(  # type: ignore[no-any-return]
            'datetime64[ms]'
        )

    def frames(self) -> Iterator[NDArray[Any]]:
        """Return iterator over all frames in image."""
        raise NotImplementedError

    def asarray(
        self,
        *,
        asrgb: bool = True,
        mode: str = 'r',
        out: OutputType = None,
    ) -> NDArray[Any]:
        """Return image data as array.

        Dimensions are returned in order stored in file.

        Parameters:
            asrgb:
                Return RGB samples in RGB order, not storage order.
                If true, the returned array might not be contiguous.
            mode:
                Memmap file open mode. The default is read-only.
            out:
                Specifies where to copy image data.
                If ``None``, create a new NumPy array in main memory.
                If ``'memmap'``, directly memory-map the image data in the
                file if possible; else create a memory-mapped array in a
                temporary file.
                If a ``numpy.ndarray``, a writable, initialized array
                of :py:attr:`shape` and :py:attr:`dtype`.
                If a ``file name`` or ``open file``, create a
                memory-mapped array in the specified file.

        Returns:
            :
                Image data as numpy array.

        """
        data = self.memory_block.read_array(
            self.parent.filehandle, self.shape, self.dtype, mode=mode, out=out
        )
        if asrgb and self.dims[-1] == 'S' and self.shape[-1] == 3:
            # TODO: verify order using self._channels strides and ids
            data = data[..., ::-1]
        return data

    def asxarray(
        self,
        *,
        asrgb: bool = True,
        mode: str = 'r',
        out: OutputType = None,
    ) -> DataArray:
        """Return image data as xarray.

        Dimensions are returned in order stored in file.

        Parameters:
            asrgb:
                Return RGB samples in RGB order, not storage order.
                If true, the returned array might not be contiguous.
            mode:
                Memmap file open mode. The default is read-only.
            out:
                Specifies where to copy image data.
                If ``None``, create a new NumPy array in main memory.
                If ``'memmap'``, directly memory-map the image data in the
                file if possible; else create a memory-mapped array in a
                temporary file.
                If a ``numpy.ndarray``, a writable, initialized array
                of :py:attr:`shape` and :py:attr:`dtype`.
                If a ``file name`` or ``open file``, create a
                memory-mapped array in the specified file.

        Returns:
            :
                Image data and select metadata as xarray DataArray.

        """
        from xarray import DataArray

        return DataArray(
            self.asarray(asrgb=asrgb, mode=mode, out=out),
            coords=self.coords,
            dims=self.dims,
            name=self.name,
            attrs=self.attrs,
        )

    def __repr__(self) -> str:
        # TODO: make columns configurable?
        # such that it can be set to os.get_terminal_size().columns
        columns = 115
        path = self.path
        dtype = self.dtype
        sizes = ', '.join(f'{k}: {v}' for k, v in self.sizes.items())
        r = f'<{self.__class__.__name__} {path!r}  ({sizes})  {dtype}>'
        if len(r) > columns:
            path = '… ' + self.path[len(r) - columns - 2 :]
            r = f'<{self.__class__.__name__} {path!r}  ({sizes})  {dtype}>'
        return r

    def __str__(self) -> str:
        return indent(repr(self))


@final
class LifImageSeries(Sequence[LifImage]):
    """Sequence of images in LIF file."""

    __slots__ = ('_parent', '_images')

    _parent: LifFile
    _images: dict[str, LifImage]

    def __init__(self, parent: LifFile) -> None:
        self._parent = parent
        self._images = {
            path.split('/', 1)[-1]: LifImage(
                parent, image, path.split('/', 1)[-1]
            )
            for path, image in LifImageSeries._image_iter(parent.xml_element)
        }

    @staticmethod
    def _image_iter(
        xml_element: ElementTree.Element,
        base_path: str = '',
        /,
    ) -> Iterator[tuple[str, ElementTree.Element]]:
        """Return iterator of image paths and XML elements."""
        elements = xml_element.findall('./Children/Element')
        if len(elements) < 1:
            elements = xml_element.findall('./Element')
        for element in elements:
            name = element.attrib['Name']
            if base_path == '' or base_path.endswith(name):
                path = name
            else:
                path = f'{base_path}/{name}'
            image = element.find('./Data/Image')
            if image is not None:
                yield path, element
            # else:
            #     # FLIM/TCSPC
            #     image = element.find('./Data/SingleMoleculeDetection')
            #     if image is not None:
            #         yield path, image
            if element.find('./Children/Element/Data') is not None:
                # sub images
                yield from LifImageSeries._image_iter(element, path)

    def findall(
        self, key: str, /, *, flags: int = re.IGNORECASE
    ) -> tuple[LifImage, ...]:
        """Return all images with matching path pattern.

        Parameters:
            key:
                Regular expression pattern to match LifImage.path.
            flags:
                Regular expression flags.

        """
        pattern = re.compile(key, flags=flags)
        images = []
        for path, image in self._images.items():
            if pattern.search(path) is not None:
                images.append(image)
        return tuple(images)

    def paths(self) -> Iterator[str]:
        """Return iterator over image paths."""
        return iter(self._images.keys())

    def __getitem__(  # type: ignore[override]
        self,
        key: int | str,
        /,
    ) -> LifImage:
        """Return image at index or first image with matching path."""
        if isinstance(key, int):
            return self._images[tuple(self._images.keys())[key]]
        if key in self._images:
            return self._images[key]
        pattern = re.compile(key, flags=re.IGNORECASE)
        for path, image in self._images.items():
            if pattern.search(path) is not None:
                return image
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._images)

    def __iter__(self) -> Iterator[LifImage]:
        return iter(self._images.values())

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} len={len(self._images)}>'

    def __str__(self) -> str:
        return indent(
            repr(self), *(repr(image) for image in self._images.values())
        )


@final
class LifMemoryBlock:
    """Object memory block.

    Parameters:
        fh: File handle.
        version: LIF file version.

    """

    __slots__ = ('id', 'offset', 'size')

    id: str
    """Identity of memory block."""

    offset: int
    """Byte offset of memory block in file."""

    size: int
    """Size of memory block in bytes."""

    def __init__(
        self,
        fh: IO[bytes],
        version: int,
        /,
    ):
        if version == 1:
            fmtstr = '<IIBIBI'
            size = 18
        else:
            fmtstr = '<IIBQBI'
            size = 22
        buffer = fh.read(size)
        if len(buffer) != size:
            raise OSError
        id0, _, id1, size1, id2, strlen = struct.unpack(fmtstr, buffer)
        if id0 != 0x70 or id1 != 0x2A or id2 != 0x2A:
            raise LifFileError(
                f'memory block {id0=}, {id1=}, {id2=} corrupted'
            )

        buffer = fh.read(strlen * 2)
        if len(buffer) != strlen * 2:
            raise OSError
        self.id = buffer.decode('utf-16-le')
        self.offset = fh.tell()
        self.size = size1
        fh.seek(self.offset + self.size)
        if fh.tell() - self.offset != self.size:
            raise OSError

    def read(self, fh: IO[bytes], /) -> bytes:
        """Return memory block from file."""
        fh.seek(self.offset)
        buffer = fh.read(self.size)
        if len(buffer) != self.size:
            raise OSError(f'read {len(buffer)} bytes, expected {self.size}')
        return buffer

    def read_array(
        self,
        fh: IO[bytes],
        /,
        shape: tuple[int, ...],
        dtype: DTypeLike,
        *,
        mode: str = 'r',
        out: OutputType = None,
    ) -> NDArray[Any]:
        """Return NumPy array from file.

        Parameters:
            fh:
                Open file handle to read from.
            shape:
                Shape of array to read.
            dtype:
                Data type of array to read.
            mode:
                Memmap file open mode. The default is read-only.
            out:
                Specifies where to copy image data.
                If ``None``, create a new NumPy array in main memory.
                If ``'memmap'``, directly memory-map the image data in the
                file if possible; else create a memory-mapped array in a
                temporary file.
                If a ``numpy.ndarray``, a writable, initialized array
                of `shape` and `dtype`.
                If a ``file name`` or ``open file``, create a
                memory-mapped array in the specified file.

        """
        dtype = numpy.dtype(dtype)
        nbytes = product(shape) * dtype.itemsize
        if nbytes > self.size:
            raise ValueError(
                f'array size={nbytes} > memory block size={self.size}'
            )
        if nbytes != self.size:
            logger().warning(f'{self!r} != array size={nbytes}')

        if isinstance(out, str) and out == 'memmap':
            return numpy.memmap(  # type: ignore[no-any-return]
                fh,  # type: ignore[call-overload]
                dtype=dtype,
                mode=mode,
                offset=self.offset,
                shape=shape,
                order='C',
            )

        data = create_output(out, shape, dtype)
        if data.nbytes != nbytes:
            raise ValueError('size mismatch')

        fh.seek(self.offset)
        try:
            n = fh.readinto(data)  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            data[:] = numpy.frombuffer(fh.read(nbytes), dtype).reshape(
                data.shape
            )
            n = nbytes

        if n != nbytes:
            raise ValueError(f'failed to read {nbytes} bytes, got {n}')

        if out is not None:
            if hasattr(out, 'flush'):
                out.flush()

        return data

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.id!r} size={self.size}>'


@dataclass
class LifChannel:
    """Attributes of Image/ChannelDescription XML element."""

    dtype: numpy.dtype[Any]
    """Numpy dtype from data_type and resolution."""
    data_type: int
    """Data type, integer (0) or float (1)."""
    channel_tag: int
    """Gray (0), Red (1), Green (2), or Blue (3)."""
    resolution: float
    """Bits per pixel."""
    name_of_measured_quantity: str
    """Name of measured quantity."""
    min: float
    """Physical value of lowest gray value."""
    max: float
    """Physical value of highest gray value."""
    unit: str
    """Physical unit."""
    lut_name: str
    """Name of Look Up Table."""
    is_lut_inverted: bool
    """Look Up Table is inverted."""
    bytes_inc: int
    """Distance from the first channel in bytes."""
    bit_inc: int
    """Bit distance."""


@dataclass
class LifDimension:
    """Attributes of Image/DimensionDescription XML element."""

    label: str
    """Label of dimension."""
    dim_id: int
    """Type of dimension."""
    number_elements: int
    """Number of elements."""
    origin: float
    """Physical position of first element."""
    length: float
    """Physical length from first to last element."""
    unit: str
    """Physical unit."""
    bytes_inc: int
    """Distance from one element to the next."""
    bit_inc: int
    """Bit distance."""


DIMENSION_ID = {
    # 0: 'C',  # sample, channel
    1: 'X',
    2: 'Y',
    3: 'Z',
    4: 'T',
    5: 'λ',  # emission wavelength
    6: 'A',  # rotation ?
    7: 'N',  # XT slices
    8: 'Q',  # T slices ?
    9: 'Λ',  # excitation wavelength
    10: 'M',  # mosaic position
    11: 'L',  # loop
}

CHANNEL_TAG = {
    0: 'Gray',
    1: 'Red',
    2: 'Green',
    3: 'Blue',
}


def create_output(
    out: OutputType,
    /,
    shape: tuple[int, ...],
    dtype: DTypeLike,
) -> NDArray[Any] | numpy.memmap[Any, Any]:
    """Return NumPy array where images of shape and dtype can be copied."""
    if out is None:
        return numpy.zeros(shape, dtype)
    if isinstance(out, numpy.ndarray):
        out.shape = shape
        return out
    if isinstance(out, str) and out[:6] == 'memmap':
        import tempfile

        tempdir = out[7:] if len(out) > 7 else None
        with tempfile.NamedTemporaryFile(dir=tempdir, suffix='.memmap') as fh:
            return numpy.memmap(fh, shape=shape, dtype=dtype, mode='w+')
    return numpy.memmap(out, shape=shape, dtype=dtype, mode='w+')


def xml2dict(xml_element: ElementTree.Element, /) -> dict[str, Any]:
    """Return XML as dictionary.

    Parameters:
        xml: XML element to convert.

    """
    sep = ','

    def astype(value: Any, /) -> Any:
        # return string value as int, float, bool, tuple, or unchanged
        if not isinstance(value, str):
            return value
        if sep and sep in value:
            # sequence of numbers?
            values = []
            for val in value.split(sep):
                v = astype(val)
                if isinstance(v, str):
                    return value
                values.append(v)
            return tuple(values)
        for t in (int, float):
            try:
                return t(value)
            except (TypeError, ValueError):
                pass
        return value

    def etree2dict(t: ElementTree.Element, /) -> dict[str, Any]:
        key = t.tag
        d: dict[str, Any] = {key: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(etree2dict, children):
                for k, v in dc.items():
                    dd[k].append(astype(v))
            d = {
                key: {
                    k: astype(v[0]) if len(v) == 1 else astype(v)
                    for k, v in dd.items()
                }
            }
        if t.attrib:
            d[key].update((k, astype(v)) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[key]['value'] = astype(text)
            else:
                d[key] = astype(text)
        return d

    return etree2dict(xml_element)


def indent(*args: Any) -> str:
    """Return joined string representations of objects with indented lines."""
    text = "\n".join(str(arg) for arg in args)
    return "\n".join(
        ("  " + line if line else line) for line in text.splitlines() if line
    )[2:]


def product(iterable: Iterable[int], /) -> int:
    """Return product of integers."""
    prod = 1
    for i in iterable:
        prod *= int(i)
    return prod


def logger() -> logging.Logger:
    """Return logging.getLogger('liffile')."""
    return logging.getLogger(__name__.replace('liffile.liffile', 'liffile'))


def main(argv: list[str] | None = None) -> int:
    """Command line usage main function.

    Preview image and metadata in specified files or all files in directory.

    ``python -m liffile file_or_directory``

    """
    from glob import glob

    if argv is None:
        argv = sys.argv

    if len(argv) > 1 and '--doctest' in argv:
        import doctest

        try:
            import liffile.liffile as m
        except ImportError:
            m = None  # type: ignore[assignment]
        doctest.testmod(m, optionflags=doctest.ELLIPSIS)
        return 0

    imshow: Any
    try:
        from tifffile import imshow
    except ImportError:
        imshow = None

    xarray: Any
    try:
        import xarray
    except ImportError:
        xarray = None

    if len(argv) == 1:
        files = glob('*.lif')
    elif '*' in argv[1]:
        files = glob(argv[1])
    elif os.path.isdir(argv[1]):
        files = glob(f'{argv[1]}/*.lif')
    else:
        files = argv[1:]

    for fname in files:
        if os.path.splitext(fname)[-1].lower() not in {'.lif'}:
            continue
        try:
            with LifFile(fname) as lif:
                print(lif)
                print()
                if imshow is None:
                    break
                for i, image in enumerate(lif.series):
                    im: Any
                    if xarray is not None:
                        im = image.asxarray()
                    else:
                        im = image.asarray()
                    print(im)
                    print()
                    pm = 'RGB' if image.dims[-1] == 'S' else 'MINISBLACK'
                    try:
                        imshow(
                            im,
                            title=repr(image),
                            show=i == len(lif.series) - 1,
                            photometric=pm,
                            interpolation='None',
                        )
                    except Exception as exc:
                        print(fname, exc)
        except Exception as exc:
            # enable for debugging
            print(fname, exc)
            continue
    return 0


if __name__ == '__main__':
    sys.exit(main())
