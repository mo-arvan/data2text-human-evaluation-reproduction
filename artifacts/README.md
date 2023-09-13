# Setup

## Loading the environment 1 (recommended)

The recommended way to run the code is to download and use the docker container provided as part of this work. This process ensures that the environment is the same as the one used to run the experiments which is important for reproducibility.

```bash

# go to the root of the repository
cd data2text-human-evaluation-reproduction

# download the docker container from Zenodo

# TODO add link to Zenodo

# Load the docker container from provided file

docker load -i artifacts/data2text-human-evaluation-reproduction.tar

```

## Loading the environment 2 (using Dockerfile)

Alternatively, you can build the docker container from the Dockerfile provided in the artifacts folder. Note that different versions of the same software may lead to different results. 

```bash
cd data2text-human-evaluation-reproduction

docker build -t data2text-human-evaluation-reproduction -f artifacts/Dockerfile  artifacts
```


## Exporting the environment

You only need to export the environment if you have made changes to the docker container and want to save and share them.

```bash

docker save -o artifacts/data2text-human-evaluation-reproduction.tar data2text-human-evaluation-reproduction

```