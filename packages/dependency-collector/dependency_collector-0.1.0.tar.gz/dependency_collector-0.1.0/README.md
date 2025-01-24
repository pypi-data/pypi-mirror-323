# Dependency collector

Python software for local retrieval of project dependencies managed by [uv](https://docs.astral.sh/uv/). The idea comes from this [comment](https://github.com/astral-sh/uv/issues/3163#issuecomment-2481505055) while waiting for this to be integrated into uv.

The project consists of a simple call to the `pip download` command and is intended for use with uv tool. 

I prefer this to using pip directly, as it allows me to define alias for my usual commands.

```batch
uv tool install dependency-collector
collect --package pandas -d .\wheelouse --python-version 3.10
```