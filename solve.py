"""Element-wise product of two vectors.

The obvious implementation, and deliberately so: this exists to exercise the
whole chain — kernel, specification, bundle, submission, runner — rather than
to be quick. A faster one is what the catalogue is for.
"""
import random
import time

from fherma import Inputs, Outputs, Point, Tensor


def init(p: Point):
    # Nothing follows from the point alone that is worth precomputing: the
    # work is one multiply per element and the length is all that changes.
    return p.N


def run(state, inp: Inputs) -> Outputs:
    time.sleep(random.uniform(1, 5))
    n = state
    a, b = inp.a.data, inp.b.data
    return Outputs(c=Tensor((n,), [a[i] * b[i] for i in range(n)], "i64"))


def free(state) -> None:
    return None
