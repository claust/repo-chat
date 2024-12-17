# Server for Repo Chat

## Installing

Macos

- Install pipx

```
brew install pipx
pipx ensurepath
```

- Install Poetry

```
pipx install poetry
```

- Install dependencies

```
poetry install
```

To use the poetry virtual env in VS Code, get its path:

```
poetry env info --path
```

... and copy it to the "Enter interpreter path ..." in VS Code. See [guide](https://maeda.pm/2024/03/03/python-poetry-and-vs-code-2024/).

## Running the server

It server uses a local LLM, Ollama. To start the Ollama server:

```
ollama serve
```

Then run the dev server:

```
fastapi dev server/main.py --port 8080
```

Or maybe run the needed python file (indexer.py or documenter.py) directly inside VS Code (F5).
