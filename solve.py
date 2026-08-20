"""Nonsense answers, at an unpredictable cost.

Nothing here multiplies anything. run() waits a while and returns noise of
the right shape and element type, which is what it takes to exercise the
failing half of the chain — the checker's verdict, the timeout, the spread
in results.json — that a correct answer never reaches.
"""
import random
import time

from fherma import Inputs, Outputs, Point, Tensor

#: The range an i64 element can hold, and so the range the noise draws from.
I64_MIN, I64_MAX = -(2 ** 63), 2 ** 63 - 1


def init(p: Point):
    # Nothing follows from the point alone that is worth precomputing: the
    # length is all that changes, and even that only decides how much noise.
    return p.N


def run(state, inp: Inputs) -> Outputs:
    n = state
    time.sleep(random.uniform(1, 5))
    # The shape and the element type are still honoured; only the values are
    # wrong, so the failure lands on the checker rather than on the reader.
    noise = [random.randint(I64_MIN, I64_MAX) for _ in range(n)]
    return Outputs(c=Tensor((n,), noise, "i64"))


def free(state) -> None:
    return None
