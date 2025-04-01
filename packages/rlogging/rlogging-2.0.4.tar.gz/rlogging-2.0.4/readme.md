# rLogging

A set of tools to improve the observability of applications

[![PyPI](https://img.shields.io/pypi/v/rlogging)](https://pypi.org/project/rlogging/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rlogging)](https://pypi.org/project/rlogging/)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=rocshers_rlogging&metric=coverage)](https://sonarcloud.io/summary/new_code?id=rocshers_rlogging)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=rocshers_rlogging&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=rocshers_rlogging)

[![Downloads](https://pypi.rocshers.com/badges/svg/packages/rlogging/downloads/total)](https://clickpy.clickhouse.com/dashboard/rlogging)
[![GitLab stars](https://img.shields.io/gitlab/stars/rocshers/python/rlogging)](https://gitlab.com/rocshers/python/rlogging)
[![GitLab last commit](https://img.shields.io/gitlab/last-commit/rocshers/python/rlogging)](https://gitlab.com/rocshers/python/rlogging)

## Functionality

- Formatters
  - **JsonFormatter** - Convert log to json
  - **ElkFormatter** - Convert log to json for ELK parsing (one-dimensional array)
- Adapters
  - **HttpLoggerAdapter**
  - **HttpLoggerAdapter**
- Django
  - **DjangoLoggerAdapter**
  - **LoggingMiddleware**

## Contribute

Issue Tracker: <https://gitlab.com/rocshers/python/rlogging/-/issues>  
Source Code: <https://gitlab.com/rocshers/python/rlogging>

Before adding changes:

Normal logging setup with new classes

```bash
make install
```

After changes:

```bash
make format test
```
