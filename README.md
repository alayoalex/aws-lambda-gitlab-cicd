# aws-lambda-gitlab-cicd

Python scripts to generate cicd gitlab pipeline to manage aws lambda functions.

# Proximas funcionalidades del script

- Dar la oportunidad de seleccionar que lambdas se quieren desplegar
    * Todas las lambdas de un modulo
    * Elegir una lambda en específico
    * Elegir un grupo de lambdas proporcionando una lista de sus números
    * Elegir aquellas lambdas que se hayan modificado basado en el commit
- Elegir a qué ambiente actualizar, si a dev, qa o prod
- Proporcionar información al usuario de eventos (logging)
- Añadir configuraciones especificas a cada stage de cada lambda


## Ejemplos de comandos
python pipelines.py -d --module src/elroi-login
python pipelines.py -d -c

## Librerias de Python necesarias
- python -m pip install GitPython
- python -m pip install dotenv

## Comandos
usage: pipelines.py [-h] [--see | --deploy] [--mod | --module [MODULE] | --all | --go | --commit | --list [LIST ...]]

optional arguments:
  -h, --help            show this help message and exit
  --see, -s             List all lambda function in the repository
  --deploy, -d          Create deployment job in the GitLab Pipeline
  --mod, -m             List all lambda function in the repository separated by module
  --module [MODULE]     List all lambda function in the repository separated by module
  --all, -a             Deploy or list all lambdas of the repository
  --go                  If the lambdas to modify are written in Go
  --commit, -c          Deploy or list lambdas that have been modified in the last commit
  --list [LIST ...], -l [LIST ...]
                        Deploy specific lambdas introducing its numbers

NOTA: La funcionalidad de generar pipeline dependiendo del último commit debe tener en cuenta que no se pueden generar jobs de Go junto con los de Python y Javascript, sino separados. Jobs Python y Javascript si pueden ir en el mismo pipeline, pero Jobs de Go no pueden ir junto a ellos porque llevan una configuracion diferente.

>> python pipelines.py -s --commit
>> python pipelines.py -d --commit
>> python pipelines.py -d --commit --go

DOCS

https://levelup.gitconnected.com/aws-lambda-in-production-deploy-a-monorepo-with-gitlab-ci-4ecc84f89263?gi=32a69c41617b
https://gntrm.medium.com/aws-lambda-in-production-deploy-python-functions-through-gitlab-ci-9c4aa1392600
