# HCW Py SDK

Healthcare worker @Home SDK, the Open Source Telehealth. This package provide SDK for more easy integration with HCW, especially for form builder.

* Website: [https://hcw-at-home.com](https://hcw-at-home.com)
* SDK documentation: [https://hcw-home.github.io/hcw-docs/python/](https://hcw-home.github.io/hcw-docs/python/)

# Build and publish this package

```
python -m build
twine upload -r pypi dist/*
```

# This add test on HCW as well

simply configure your .env and run with

```
pytest test.py
```
