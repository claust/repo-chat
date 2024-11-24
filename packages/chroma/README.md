# Chroma database for Repo-Chat

## Install

Install Miniconda: https://docs.anaconda.com/miniconda/install/#quick-command-line-install

Create an environment from the `environment.yml`:
````
conda env create -f environment.yml
````


## How to run

Activate the python environment
````
conda activate chroma
````

Update the dependencies, if needed
```
conda env update --file environment.yml --prune
````

Start the chroma server
```
chroma run --path ./repo-chat
````
