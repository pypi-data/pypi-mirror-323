import os

class ContexDirectory:
    def __init__(self, path):
        self.path = path
        self.original = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original)
        return False
    
def create_gitlab_ci():
    """
    Create a gitlab-ci.yml file for python project.
    """
    
    with open('gitlab-ci.yml','w') as f:
        f.write("""stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: python:3.9
  script:
    - pip install poetry
    - poetry install
    - poetry build

test:
  stage: test
  image: python:3.9
  script:
    - pip install pytest
    - poetry install
    - pytest

deploy:
  stage: deploy
  image: python:3.9
  script:
    - poetry install
    - python manage.py deploy
""")