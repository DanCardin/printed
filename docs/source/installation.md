# Installation/Usage

Depending on the kind of user you are and your usecase, one or the other of the
installation/usage methods may be more or less appropriate.

### Docker

Usage through Docker will be most appropriate for those who:

- are looking to run it as a service which passively syncs subscribed series
- aren't familiar with python/python tooling

Sources:

- @Dockerhub:
  [printed](https://hub.docker.com/repository/docker/dancardin/printed)

The tool can be run (very basically) like so
`docker run -v  ./printed:/app/printed -itd printed`

or alternatively with `docker-compose`

```yaml
version: "3.8"

name: printed
services:
  watch:
    image: dancardin/printed:latest
    restart: always
    command: watch
    volumes:
      - "${PWD}:/data"

  # optionally

  web:
    image: dancardin/printed:latest
    restart: always
    command: web --host 0.0.0.0
    ports:
      - 8000:8000
    volumes:
      - "${PWD}:/data"
```

In either case you can `docker exec` into the container to interact with the
`printed` CLI (until such a time as there is a web UI).

### Python

Python installation will be most appropriate for those who:

- Will be locally running the CLI ad-hoc rather than as a "service"
- are familiar with python/python tooling

Printed can either be installed directly through PyPi

```bash
pip install printed
# or
pipx install printed
```

and then invoked with the CLI: `printed`

### Environment Variables

The CLI (and thus docker) will read from the following environment variables,
which in turn correspond to the indicated CLI flags as defaults.

These will most often be useful in configuring docker/docker-compose where it
may be more convenient to configure environment variables than it is to supply
CLI flags.

- `PRINTED_PATH`: `printed web --root-path`
