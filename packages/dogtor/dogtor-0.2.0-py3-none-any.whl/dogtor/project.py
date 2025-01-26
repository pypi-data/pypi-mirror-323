import os
import subprocess
import argparse
from dogtor.utils import ContexDirectory, create_gitlab_ci

def flash(project_name: str,
           requirements: str='.',
           cicd: str='gitlab') -> None:
    print(f"Project Name: {project_name}")
    print(f"Requirements: {requirements}")
    print(f"CI/CD: {cicd}")
    """
    Description:
    ------------
        This function creates a new poetry project and installs the required dependencies.
    
    Args:
    -----
        project_name -- the name of the project to be created
    
    Returns:
    --------
        None
    """
    folder_path = os.path.join(os.getcwd(),'.')
    with ContexDirectory(folder_path):
        if project_name is None:
            raise ValueError('Project name is required!')
        # 1.0 Activate the virtual environment before and then install poetry
        subprocess.Popen(['python', '-m', 'pip', 'install', 'poetry']).wait()
        # 2.0 Create a new poetry project
        subprocess.Popen(['poetry', 'new', project_name]).wait()
        # 3.0 Move into the project directory to install the dependencies
        try:
            os.chdir(project_name)
        except FileNotFoundError:
            print('Directory not found!')
            return  # Return control to the main process
        # 4.0 Install the required dependencies
        subprocess.Popen(['poetry', 'add', 'sphinx']).wait()
        subprocess.Popen(['poetry', 'install']).wait()
        # Check if requirements.txt file exists
        if requirements is not None:
            if os.path.isfile(requirements):
                # take all the packages from the requirements.txt and install it to the virtual environment
                with open(requirements, 'r') as f:
                    for line in f:
                        subprocess.Popen(['poetry', 'add', line.strip()]).wait()
                subprocess.Popen(['poetry', 'install']).wait()
                print('Dependency added and installed!')
            else:
                print('requirements.txt file not found!')
        else:
            print('requirements.txt file not provided!')
        # 5.0 Create the sphinx documentation
        if not os.path.exists(os.path.join(os.getcwd(),'docs')):
            os.mkdir('docs')
        with ContexDirectory('docs'):
            subprocess.Popen(['sphinx-quickstart',
                            '-q',
                            '-p',f'{project_name}',
                            '-a', 'Author',
                            '-v', '1.0',
                            '-d', 'docs',
                            '-r', '1.0',
                            '-l', 'en',
                            '--sep']).wait()
            print('Dependency added and installed!')
        # 6.0 Create the gitlab-ci.yml file
            if cicd is not None:
                if cicd == 'gitlab':
                    with ContexDirectory(os.path.join(folder_path,project_name)):
                        create_gitlab_ci()
                else:
                    print('Invalid option!')
            else:
                print('No option provided!')
            # Return control to the main process

def main():
    parser = argparse.ArgumentParser(description='Setup poetry project.')
    parser.add_argument('-p', '--project_name', type=str, help='The name of the project', nargs='?')
    parser.add_argument('-r', '--requirements', type=str, help='The path of the requirements file', nargs='?')
    parser.add_argument('-ci', '--cicd', type=str, help='Create a gitlab-ci.yml file', nargs='?')
    args = parser.parse_args()
    flash(project_name=str(args.project_name), requirements=args.requirements, cicd=args.cicd)

    
if __name__ == '__main__':
    main()

