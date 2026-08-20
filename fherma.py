"""GENERATED from multiply/multiply@1.0.0. Do not edit.

Types derived from the signature. Write the bodies in generate.py and oracle.py;
serialising is the runner's job, so nothing here opens a file.
"""
from dataclasses import dataclass, field
import hashlib
import os
import struct

SPEC = "multiply/multiply@1.0.0"

#: Bits on the wire, by element type.
WIDTHS = {"i8": 8, "i16": 16, "i32": 32, "i64": 64, "u8": 8, "u16": 16, "u32": 32, "u64": 64, "f32": 32, "f64": 64}


@dataclass(frozen=True)
class Point:
    """One field per value parameter, in the order of the signature."""
    N: int           # param N: uint


@dataclass
class Inputs:
    a: "Tensor"     # %a: tensor<N x i64>
    b: "Tensor"     # %b: tensor<N x i64>


@dataclass
class Outputs:
    c: "Tensor"     # %c: tensor<N x i64>


@dataclass
class Verdict:
    passed: bool
    metrics: dict = field(default_factory=dict)


class Tensor:
    """A flat, row-major buffer. Shape is known at run time; the element type
    comes from the signature and fixes the width on the wire."""

    __slots__ = ("shape", "elem", "data")

    def __init__(self, shape, data, elem="i64"):
        self.shape, self.elem, self.data = tuple(shape), elem, list(data)
        if len(self.data) != self.count():
            raise ValueError(f"{len(self.data)} values for shape {self.shape}")

    def count(self):
        total = 1
        for dimension in self.shape:
            total *= dimension
        return total

    def nbytes(self):
        return self.count() * WIDTHS[self.elem] // 8

    def __repr__(self):
        return f"Tensor(shape={self.shape}, elem={self.elem!r}, …)"


class Stream:
    """The only source of randomness on offer.

    block(i) = SHA256(SPEC | seed | i); the stream is block(0) ‖ block(1) ‖ …
    It is the same in every language because it is written down, and it is
    seekable, so generating large inputs parallelises. Anything else — random,
    time, urandom, secrets — makes a generator irreproducible and is rejected.
    """

    def __init__(self, seed: int):
        self._prefix = f"{SPEC}|{seed}"
        self._buffer, self._counter = b"", 0

    def _fill(self, n: int) -> None:
        while len(self._buffer) < n:
            block = f"{self._prefix}|{self._counter}".encode()
            self._buffer += hashlib.sha256(block).digest()
            self._counter += 1

    def bytes(self, n: int) -> bytes:
        self._fill(n)
        head, self._buffer = self._buffer[:n], self._buffer[n:]
        return head

    def bits(self, k: int) -> int:
        return int.from_bytes(self.bytes((k + 7) // 8), "little") & ((1 << k) - 1)

    def below(self, n: int) -> int:
        """Uniform on [0, n). The extra 64 bits keep the bias under 2**-64."""
        return self.bits(n.bit_length() + 64) % n


def encode(tensor: Tensor) -> bytes:
    """A tensor as it goes on the wire: little-endian, row-major, no header.

    The shape travels beside it in case.json rather than inside the bytes, so a
    reader in another language needs no parser — only the width, which the
    signature already fixed.
    """
    if tensor.elem[0] == "f":
        kind = {32: "f", 64: "d"}.get(WIDTHS[tensor.elem])
        if kind is None:
            raise ValueError(f"{tensor.elem} has no wire form yet")
        return struct.pack(f"<{tensor.count()}{kind}", *tensor.data)

    width = WIDTHS[tensor.elem] // 8
    signed = tensor.elem[0] == "i"
    return b"".join(
        int(value).to_bytes(width, "little", signed=signed) for value in tensor.data
    )


def decode(raw: bytes, shape, elem="i64") -> Tensor:
    """The inverse of encode."""
    count = 1
    for dimension in shape:
        count *= dimension

    width = WIDTHS[elem] // 8
    if len(raw) != count * width:
        raise ValueError(f"{len(raw)} bytes for {tuple(shape)} of {elem}")

    if elem[0] == "f":
        kind = {32: "f", 64: "d"}.get(WIDTHS[elem])
        if kind is None:
            raise ValueError(f"{elem} has no wire form yet")
        values = list(struct.unpack(f"<{count}{kind}", raw))
    else:
        signed = elem[0] == "i"
        values = [
            int.from_bytes(raw[i * width : (i + 1) * width], "little", signed=signed)
            for i in range(count)
        ]
    return Tensor(shape, values, elem)


def pack(values, limbs, elem="i64") -> Tensor:
    """Integers wider than a word into `limbs` machine words each, low word first."""
    data = []
    for value in values:
        for index in range(limbs):
            data.append((value >> (64 * index)) & 0xFFFFFFFFFFFFFFFF)
    return Tensor((len(values), limbs), data, elem)


def unpack(tensor: Tensor) -> list:
    """The inverse of pack, for a tensor whose last dimension is the limbs."""
    *head, limbs = tensor.shape
    count = 1
    for dimension in head:
        count *= dimension
    return [
        sum(tensor.data[i * limbs + j] << (64 * j) for j in range(limbs))
        for i in range(count)
    ]


def asset(name: str) -> str:
    """Path to a file in assets/, wherever this bundle happens to be mounted."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", name)
