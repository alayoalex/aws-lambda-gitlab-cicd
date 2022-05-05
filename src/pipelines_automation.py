import os
from pathlib import Path
import gitpy_wrapper


twospace = 2*" "
fourspace = 4*" "
const_root_relative_folder = 'elroisupplies-serverless-lambdas'
lambdas_directory = 'src'
role_arn = 'arn:aws:iam::$ACCOUNT:role/$ROLE_NAME'
lambda_runtimes = {
    'py': 'python3.8',
    'js': 'nodejs14.x',
    'go': 'Go1.x'
}


def get_working_path():
    absolute_path = Path(os.path.abspath('.'))
    while absolute_path.parts[-1] != const_root_relative_folder:
        absolute_path = absolute_path.parent
    return os.fspath(absolute_path)


def move_to_working_path():
    working_path = get_working_path()
    os.chdir(working_path)


def is_gitlab_template(path, go=False):
    if go == True:
        return os.path.exists(os.path.join(path, '.gitlab-ci-template-go.yml'))
    return os.path.exists(os.path.join(path, '.gitlab-ci-template-py.yml'))


def get_gitlab_template(go=False):
    file = ".gitlab-ci-template-py.yml"
    if go == True:
        file = ".gitlab-ci-template-go.yml"
    with open(file, encoding='utf-8', mode='rt') as f:
        return f.read()


def get_gitlab_update_envs_template():
    file = ".gitlab-ci-template-update-envs-py.yml"
    with open(file, encoding='utf-8', mode='rt') as f:
        return f.read()


def create_stage_for_lambda(name, folder, runtime, role_arn, alias, env=None):
    data = ''
    data += 'deploy_' + name + ':\n'
    data += twospace + 'extends: deploy_main' + '\n'
    data += twospace + 'environment: ' + 'deploy_' + name + '\n'
    data += twospace + 'variables: \n'
    data += fourspace + 'FOLDER: ' + folder + '\n'
    data += fourspace + 'LAMBDA_NAME: ' + name + '\n'
    data += fourspace + 'LAMBDA_ALIAS: ' + alias + '\n'
    data += fourspace + 'LAMBDA_RUNTIME: ' + runtime + '\n'
    data += fourspace + 'ROLE_ARN: ' + role_arn + '\n'
    data += fourspace + 'LAMBDA_HANDLER: index.handler'
    if env != None:
        data += '\n'
        data += fourspace + 'ENV_SOURCE: ' + env + '\n'
        if env == 'dev':
            data += fourspace + 'ENV_NAME: qa' + '\n'
        elif env == 'qa':
            data += fourspace + 'ENV_NAME: prod' + '\n'
    return data


def update_envs(env, lambda_list):
    template_data = get_gitlab_update_envs_template()
    with open(".gitlab-ci.yml", encoding='utf-8', mode='wt') as f:
        print(template_data, file=f)
        for l in lambda_list:
            stage_data = create_stage_for_lambda(
                l[2], l[1], lambda_runtimes[l[3]], role_arn, env, env=env)
            print('\n', file=f)
            print(stage_data, file=f)


def create_gitlab_pipeline(lambda_list, alias='dev', go=False):
    template_data = get_gitlab_template(go=go)
    with open(".gitlab-ci.yml", encoding='utf-8', mode='wt') as f:
        print(template_data, file=f)
        for l in lambda_list:
            stage_data = create_stage_for_lambda(
                l[2], l[1], lambda_runtimes[l[3]], role_arn, alias)
            print('\n', file=f)
            print(stage_data, file=f)


def get_all_lambdas_from_repo():
    result = []
    directory = get_working_path()
    path = os.path.join(directory, lambdas_directory)
    contador = 1

    for foldername, subfolders, filenames in os.walk(path):
        for filename in filenames:
            if filename in ['index.py', 'lambda_function.py']:
                folders_list = foldername.split(os.path.sep)
                folders_list.reverse()
                name = folders_list[0]
                folder_lambda = []
                for i in range(1, len(folders_list)):
                    folder_lambda.append(folders_list[i])
                    if folders_list[i] == 'src':
                        break
                folder_lambda.reverse()
                folder = '/'.join(folder_lambda)
                result.append((
                    str(contador),
                    folder,
                    name,
                    'py'))
                contador += 1
            elif filename in ['index.js', 'lambda_function.js']:
                folders_list = foldername.split(os.path.sep)
                folders_list.reverse()
                name = folders_list[0]
                folder_lambda = []
                for i in range(1, len(folders_list)):
                    folder_lambda.append(folders_list[i])
                    if folders_list[i] == 'src':
                        break
                folder_lambda.reverse()
                folder = '/'.join(folder_lambda)
                result.append((
                    str(contador),
                    folder,
                    name,
                    'js'))
                contador += 1
            elif filename in ['main.go', 'lambda_function.go']:
                folders_list = foldername.split(os.path.sep)
                folders_list.reverse()
                name = folders_list[0]
                folder_lambda = []
                for i in range(1, len(folders_list)):
                    folder_lambda.append(folders_list[i])
                    if folders_list[i] == 'src':
                        break
                folder_lambda.reverse()
                folder = '/'.join(folder_lambda)
                result.append((
                    str(contador),
                    folder,
                    name,
                    'go'))
                contador += 1
    return result


def get_lambdas_by_module():
    l = get_all_lambdas_from_repo()
    temb_lambda_of_module = []
    lambdas_by_modules = {}
    for i in l:
        if i[1] not in lambdas_by_modules.keys():
            lambdas_by_modules[i[1]] = [(i[0], i[1], i[2], i[3])]
        else:
            temb_lambda_of_module = lambdas_by_modules[i[1]]
            temb_lambda_of_module.append((i[0], i[1], i[2], i[3]))
            lambdas_by_modules[i[1]] = temb_lambda_of_module
    return lambdas_by_modules


def get_lambdas_by_commit_diff():
    working_path = get_working_path()
    modified_lambdas = gitpy_wrapper.get_modified_lambdas(working_path)
    # Deleting duplicates folders
    i = 0
    for lambda_path in modified_lambdas:
        lambda_name = lambda_path.split('/')[-2]
        for j in range(i+1, len(modified_lambdas)-1):
            lambda_path2 = modified_lambdas[j]
            lambda_name2 = lambda_path2.split('/')[-2]
            while lambda_name2 == lambda_name:
                modified_lambdas.remove(lambda_path2)
                lambda_path2 = modified_lambdas[j]
                lambda_name2 = lambda_path2.split('/')[-2]
            break  # Because the folders are sorted by Name
        i += 1
    return modified_lambdas

def get_specific_lambdas():
    pass


def define_environment_to_deploy():
    pass


def main():
    this_path = os.getcwd()
    if this_path != get_working_path():
        move_to_working_path()
    if is_gitlab_template(os.getcwd()):
        lambda_list = get_all_lambdas_from_repo()
        create_gitlab_pipeline(lambda_list)


if __name__ == '__main__':
    main()
