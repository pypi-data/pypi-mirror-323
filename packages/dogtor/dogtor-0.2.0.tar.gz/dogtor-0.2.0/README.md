# DOGTOR

Dogtor is a simple package to scaffold your Python project. Using Dogtor you can:

- Create a new Python environment using `venv`.
- Scaffold a new Python package project using `Poetry`.
- Start your project with `Sphinx` documentation already set up.
- Install a list of packages you want to start with in your environment.
- Generate a GitLab CI/CD configuration file.

Dogtor simplifies the initial setup of your Python projects, handling the boilerplate so you can focus on your code.  After the initial scaffolding, Dogtor steps aside, leaving you to work on your project.

## Installation

```bash
pip install dogtor
```

## Usage

### Creating a Virtual Environment

> Create a virtual environment using venv

```bash
dogtor-env -e "project_python_env"
```
This command creates a virtual environment named `project_python_env`.  Remember to activate it before using Dogtor to create your project.

> Activate the virtual environment

```bash
source project_python_env/bin/activate
```

### Scaffolding a New Python Project

> Scaffold a new python project using dogtor. This will create a new python project using poetry. It will also create a new sphinx documentation for the project.

```bash
dogtor-project -p "project_name"
```

This creates a new project named `project_name`.  A `pyproject.toml` file (for Poetry), a basic project structure, and a Sphinx documentation setup will be generated.

> If there is a need for you to scaffold a new python project with requirements already installed, you can do so by passing the path of a requirements file to the dogtor-project command.

```bash
dogtor-project -p "project_name" -r "path_to_requirements_file"
```

> If you also require a gitlab cicd file template for the python package to be created you can pass the -ci flag to the dogtor-project command.

```bash
dogtor-project -p "project_name" -r "path_to_requirements_file" -ci 'gitlab'
```

This will include a basic GitLab CI/CD configuration file in your project.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.  See the `LICENSE` file for details.

```Plain Text
Copyright © 2025, The Short Epoch
```
