# Printed

[![Actions Status](https://github.com/DanCardin/printed/actions/workflows/test.yml/badge.svg)](https://github.com/dancardin/printed/actions)
[![codecov](https://codecov.io/gh/DanCardin/printed/graph/badge.svg?token=e8T6QN2tTz)](https://codecov.io/gh/DanCardin/printed)
[![Documentation Status](https://readthedocs.org/projects/printed/badge/?version=latest)](https://printed.readthedocs.io/en/latest/?badge=latest)
[![Docker](https://img.shields.io/docker/v/dancardin/printed?label=Docker&style=flat)](https://hub.docker.com/r/dancardin/printed)

- [Full documentation here](https://printed.readthedocs.io/en/latest/).
- [Installation/Usage](https://printed.readthedocs.io/en/latest/installation.html).

A tool for keeping track of 3d prints.

## Quickstart

```bash
❯ printed print add 'Benchy' \
  --cost 1 \
  --material PLA=35 \
  --source-link 'https://printables.com/some-model' \
  --reference-link 'https://amazon.com/some-thing'
❯ printed print list
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ ID ┃ Name                       ┃ Count   ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 1  │ Benchy                     │ 0       │
└────┴────────────────────────────┴─────────┘
❯ printed print print 'Benchy'
```

## Web

The tool also ships with a web service which can be used to view and manage
prints.

![Web Example](docs/web.png)
