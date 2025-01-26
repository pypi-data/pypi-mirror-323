import typer
from rich.console import Console
import os
import sys
import requests

app = typer.Typer(no_args_is_help=True)


@app.command()
def init(
    service_name: str = typer.Option(
        prompt="Service Name", default=os.path.basename(os.getcwd())
    ),
    version: str = typer.Option(prompt="Version", default="1.0.0"),
    description: str = typer.Option(prompt="Description", default=""),
    license: str = typer.Option(prompt="License", default=""),
    python_version: str = typer.Option(
        prompt="Python Version",
        default=f"{sys.version_info.major}.{sys.version_info.minor}",
    ),
):
    """
    Initialization function for service template
    """
    authors = typer.prompt("Authors (comma separated)", default="").split(",")
    console = Console()
    console.print("\n\n[cyan]Initializing service template[/cyan]")
    console.print(f"Service Name: [bold green3]{service_name}[/bold green3]")
    console.print(f"Version: [bold green3]{version}[/bold green3]")
    console.print(f"Description: [bold green3]{description}[/bold green3]")
    console.print(f"License: [bold green3]{license}[/bold green3]")
    console.print(f"Python Version: [bold green3]{python_version}[/bold green3]")
    console.print(f"Author: [bold green3]{authors}[/bold green3]")
    console.print('readme: [bold green3]"README.md"[/bold green3]')

    dirs = [
        "app/api/v1/routers/",
        "app/core/",
        "app/schemas/",
        "app/logs/",
        "app/tests/",
    ]

    for dir in dirs:
        os.makedirs(os.path.dirname(dir), exist_ok=True)

    files = [
        "app/api/v1/routers/__init__.py",
        "app/core/__init__.py",
        "app/schemas/__init__.py",
        "app/main.py",
        "app/core/config.py",
        "Dockerfile",
        "docker-compose.yaml",
        ".env",
        ".env.example",
        "README.md",
    ]

    for file in files:
        with open(file, "w") as f:
            pass

    with open(".gitignore", "w") as f:
        url = "https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore"
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            content = response.text
            f.write(content)

    with open(".dockerignore", "w") as f:
        url = "https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore"
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            content = response.text
            f.write(content)

    os.system(f"uv init --python {python_version}")
    os.remove("hello.py")

    with open("makefile", "w") as f:
        f.write(
            f"""format:
\t@black .
\t@isort .

lint:
\t@flake8 .
\t@mypy .
"""
        )

    with open("pyproject.toml", "w") as f:
        f.write(
            f"""[project]
name = "{service_name}"
version = "{version}"
description = "{description}"
readme = "README.md"
authors = {authors}
requires-python = ">={python_version}"
dependencies = []

[tool.black]
line-length = 79

[tool.isort]
profile = "black"

[tool.mypy]
ignore_missing_imports = true

[project.scripts]
{service_name.replace("-","_")} = "{service_name.replace("_","-")}:main"
"""
        )

    os.system("uv add fastapi[all]")
    os.system("uv add --dev isort black mypy flake8 types-requests")

    os.system("git init -b main")
    os.system("git add .")
    os.system('git commit -m "Initial commit"')


@app.command()
def status():
    """
    Status for service template
    """
    Console().log("Status: [green3]Healthy[/green3]")


if __name__ == "__main__":
    app()
