import argparse
import sys
import os
import pipelines_automation as automation

"""
- Listar todas las lambdas
    > python pipelines.py --see --all
- Listar todas las lambdas por modulos
    > python pipelines.py --see --mod
- Listar todas las lambdas modificadas
    > python pipelines.py --see --commit
- Dar la oportunidad de seleccionar que lambdas se quieren desplegar
    * Todas las lambdas de un modulo
        > python pipelines.py -d -a
    * Elegir una lambda en específico
        > python pipelines.py -d -l name
    * Elegir un grupo de lambdas proporcionando una lista de sus números
        > python pipelines.py -d -l 1 2 3
    * Elegir aquellas lambdas que se hayan modificado basado en el commit
        > python pipelines.py -d --commit
- Elegir a qué ambiente actualizar, si a dev, qa o prod
    > python pipelines.py -d -c --commit --env {dev, qa, prod}
- Elegir qué lambdas actualizar, si a dev, qa o prod
    > python pipelines.py --env {dev, qa, prod} --to {dev, qa, prod} --list <number of the lambdas,...>
- Proporcionar información al usuario de eventos (logging)
- Añadir configuraciones especificas a cada stage de cada lambda 
"""


def show_all_lambdas_repo():
    l = automation.get_all_lambdas_from_repo()
    for i in l:
        print('{}   {}   {}   {}'.format(i[0], i[1], i[2], i[3]))


def show_lambdas_by_module():
    lambdas_by_modules = automation.get_lambdas_by_module()
    for k, v in lambdas_by_modules.items():
        print('{}'.format(k))
        for values in v:
            print('\t - {} {}, {}'.format(values[0], values[1], values[2]))
        print()


def show_lambdas_by_commit_diff():
    modified_lambdas = automation.get_lambdas_by_commit_diff()
    print(
        f'\nIt has been modified {len(modified_lambdas)} lambdas in last commit.\n')
    for ml in modified_lambdas:
        print(f'    {ml}')
    print()


def deploy_all_lambdas(go=False):
    lambda_list = automation.get_all_lambdas_from_repo()
    automation.create_gitlab_pipeline(lambda_list, go=go)


def update_all_lambdas_environment(env):
    lambda_list = automation.get_all_lambdas_from_repo()
    automation.update_envs(env, lambda_list)


def deploy_specific_lambdas(selected_lambdas_numbers, go):
    all_lambdas = automation.get_all_lambdas_from_repo()
    lambdas_list = []
    for al in all_lambdas:
        for sl in selected_lambdas_numbers:
            if al[0] == sl:
                lambdas_list.append(al)
    automation.create_gitlab_pipeline(lambdas_list, go=go)


def deploy_range_lambdas(start, end, go):
    all_lambdas = automation.get_all_lambdas_from_repo()
    lambdas_list = []
    if start < 1 or end > len(all_lambdas):
        print('Invalid range. Must be between 1 and {}'.format(len(all_lambdas)))
        sys.exit(1)
    for al in all_lambdas:
        for sl in range(start, end+1):
            if int(al[0]) == sl:
                lambdas_list.append(al)
    automation.create_gitlab_pipeline(lambdas_list, go=go)


def update_range_lambdas_environments(start, end, env):
    all_lambdas = automation.get_all_lambdas_from_repo()
    lambdas_list = []
    if start < 1 or end > len(all_lambdas):
        print('Invalid range. Must be between 1 and {}'.format(len(all_lambdas)))
        sys.exit(1)
    for al in all_lambdas:
        for sl in range(start, end+1):
            if int(al[0]) == sl:
                lambdas_list.append(al)
                break
    automation.update_envs(env, lambdas_list)


def update_specific_lambdas_environments(selected_lambdas_numbers, env):
    all_lambdas = automation.get_all_lambdas_from_repo()
    lambdas_list = []
    for al in all_lambdas:
        for sl in selected_lambdas_numbers:
            if al[0] == sl:
                lambdas_list.append(al)
    automation.update_envs(env, lambdas_list)


def update_environment_lambdas_by_module(module_name, env):
    lambdas_dict = automation.get_lambdas_by_module()
    lambda_list = lambdas_dict.get(module_name, [])
    automation.update_envs(env, lambda_list)


def deploy_lambdas_by_module(module_name, go):
    lambdas_dict = automation.get_lambdas_by_module()
    lambda_list = lambdas_dict.get(module_name, [])
    automation.create_gitlab_pipeline(lambda_list, go=go)


def deploy_lambdas_by_commit_diff(go):
    modified_lambdas = automation.get_lambdas_by_commit_diff()
    all_lambdas = automation.get_all_lambdas_from_repo()
    if len(modified_lambdas) > 0:
        lambdas_list = []
        for ml in modified_lambdas:
            for al in all_lambdas:
                if ml.split('/')[-2] == al[2]:
                    if go and al[3] == 'go':
                        lambdas_list.append(al)
                    elif not go and al[3] != 'go':
                        lambdas_list.append(al)
        automation.create_gitlab_pipeline(lambdas_list, go=go)
    else:
        print("There is not modified lambda functions to deploy.")


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        main_group = parser.add_mutually_exclusive_group()
        main_group.add_argument(
            '--see',
            '-s',
            action="store_true",
            help='List all lambda function in the repository')
        main_group.add_argument(
            '--env',
            # action="store_true",
            nargs=1,
            help='Update the environment of a list of lambdas')
        main_group.add_argument(
            '--deploy',
            '-d',
            action="store_true",
            help='Create deployment job in the GitLab Pipeline')
        secondary_group = parser.add_mutually_exclusive_group()
        secondary_group.add_argument(
            '--mod',
            '-m',
            action="store_true",
            help='List all lambda function in the repository separated by module')
        secondary_group.add_argument(
            '--module',
            nargs="?",
            help='List all lambda function in the repository separated by module')
        secondary_group.add_argument(
            '--range',
            nargs=2,
            type=int,
            help='Update a range of lambda function in the repository')
        secondary_group.add_argument(
            '--all',
            '-a',
            action="store_true",
            help='Deploy or list all lambdas of the repository')
        secondary_group.add_argument(
            '--commit',
            '-c',
            action="store_true",
            help='Deploy or list lambdas that have been modified in the last commit')
        secondary_group.add_argument(
            '--list',
            '-l',
            nargs='*',
            help='Deploy specific lambdas introducing its numbers')
        parser.add_argument(
            '--go',
            action="store_true",
            help='If the lambdas to modify are written in Go')
        args = parser.parse_args()
        return args
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


if __name__ == '__main__':
    this_path = os.getcwd()
    if this_path != automation.get_working_path():
        automation.move_to_working_path()

    args = parse_cli()
    if args.see and args.mod:
        print("Listing all lambdas in the repository")
        show_lambdas_by_module()
    elif args.see and args.commit:
        show_lambdas_by_commit_diff()
    elif args.see:
        print("Listing all lambdas in the repository separated by module")
        show_all_lambdas_repo()
    elif args.env and args.list:  # Update the environment of a list of lambdas
        env = args.env[0]
        if env == 'dev' or env == 'qa':
            print("Update environment '{0}' of lambdas {1}".format(
                env, args.list))
            update_specific_lambdas_environments(args.list, env)
            print("Done")
        else:
            print(
                "Invalid environments. The update must be from 'dev' to 'qa' or from 'qa' to 'prod'.")
    elif args.env and args.range:  # Update the environment of a list of lambdas in a range
        env = args.env[0]
        if env == 'dev' or env == 'qa':
            print("Update environment '{0}' in the range {1}".format(
                env, args.range))
            update_range_lambdas_environments(
                args.range[0], args.range[1], env)
            print("Done")
        else:
            print(
                "Invalid environments. The update must be from 'dev' to 'qa' or from 'qa' to 'prod'.")
    elif args.deploy and args.range:  # Deploy a list of lambdas in a range
        print("Deploy Lambdas in the range {0}".format(args.range))
        deploy_range_lambdas(args.range[0], args.range[1], go=args.go)
        print("Done")
    elif args.env and args.module:  # Update the environment in a module
        env = args.env[0]
        if env == 'dev' or env == 'qa':
            print("Update environment '{0}' of lambdas {1}".format(
                env, args.module))
            update_environment_lambdas_by_module(args.module, env)
            print("Done")
        else:
            print(
                "Invalid environments. The update must be from 'dev' to 'qa' or from 'qa' to 'prod'.")
    elif args.env and args.all:
        update_all_lambdas_environment(args.env[0])
        print("Done")
    elif args.deploy and args.all:
        deploy_all_lambdas(args.go)
        print("Done")
    elif args.deploy and args.commit:
        print("Creating pipeline jobs of all modified lambdas")
        deploy_lambdas_by_commit_diff(args.go)
        print("Done")
    elif args.deploy and args.module != None:
        print("Creating pipeline jobs of an specified git repo module")
        deploy_lambdas_by_module(args.module, args.go)
        print("Done")
    elif args.deploy and args.list:
        print("Creating pipeline jobs of an specified lambdas list:")
        deploy_specific_lambdas(args.list, args.go)
        print("Done")
