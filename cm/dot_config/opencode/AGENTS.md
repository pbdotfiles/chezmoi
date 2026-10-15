# Python environments

When `PIXI_PROJECT_MANIFEST` is set, a pixi environment is active. Install packages with `pixi add --manifest-path "$PIXI_PROJECT_MANIFEST" <pkg>` (conda-forge) or `pixi add --manifest-path "$PIXI_PROJECT_MANIFEST" --pypi <pkg>` (PyPI only), never with `pip install` or `conda install`, so the package is recorded in the environment's `pixi.toml` and `pixi.lock`. Always pass `--manifest-path`: without it, pixi targets the current folder's own pixi project, if there is one.
