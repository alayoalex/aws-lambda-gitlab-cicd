import os
from git import Repo


def get_modified_lambdas(path):
    repo = Repo(os.path.abspath('.'))
    # TODO Aquí está harcodeada la rama (dev), pero debería ponerse automática.
    tree = repo.heads.dev.commit.diff('HEAD~1')
    modified_lambdas = []
    for item in tree:
        if item.b_path.split('/')[0] == 'src':
            modified_lambdas.append(item.b_path)
    return modified_lambdas
