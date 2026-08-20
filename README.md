# multiply — a solution

An answer to `multiply/v1@1.0.0`: the element-wise product of two integer
vectors.

## What is yours

`solve.py`. Three functions:

```
init(Point)         -> state     setup. Called once per point, not measured.
run(state, Inputs)  -> Outputs   the answer. Measured, and only this.
free(state)                      optional.
```

## What is not

`main.py` and `fherma.py` are generated from the specification's signature, and
the runner writes its own copies over them before building. The clock lives in
`main.py`, so a measurement taken with the author's copy would be a measurement
the author wrote. Editing them locally is fine and changes nothing about how it
is measured.

## Running it yourself

```
fherma-lang emit --testing --out bundle spec.fherma     # the bundle, once
python bundle/main.py make /tmp/p --point '{"N":1024}' --seeds 1-5
python main.py /tmp/p
python bundle/main.py verify /tmp/p
```

## Submitting

Push this directory to a repository, then point an implementation at the
repository and the commit. The commit is what is measured — a branch moves.
# fherma2-mult-kernel-test
