import venv
import argparse

def create(env_name: str='project_env')-> None:
    """
    Description:
    ------------
        This function creates a new python environment.
        If no name is provided, the default name is 'project_env'.
    
    Args:
    -----
        env_name (str): The name of the environment to create.
    
    Returns:
    --------
        None
    """
    venv.create(env_name, with_pip=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup python environment.')
    parser.add_argument('-e', '--env_name', type=str, help='The name of the environment to create.')
    args = parser.parse_args()
    create(args.env_name)