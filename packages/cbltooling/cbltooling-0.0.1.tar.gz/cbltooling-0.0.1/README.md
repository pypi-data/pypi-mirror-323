# `cbltools`

> Python tooling for the Computational Biomechanics Lab

This repository is intended to collect, organize, and document various
scripts and tools that the [Computational Biomechanics Lab at TU Delft](https://www.tudelft.nl/me/over/afdelingen/biomechanical-engineering/research/biomechatronics-human-machine-control/computational-biomechanics-lab) uses.

Read [📖 the documentation](https://computationalbiomechanicslab.github.io/cbltooling) for
more info.

# Build notes

```bash
python -m pip install --upgrade build
python -m build
# test upload:
# python3 -m twine upload --repository testpypi dist/*
```

