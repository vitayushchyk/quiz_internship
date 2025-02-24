# **Meduzzen intership**

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=008000&vCenter=true&random=false&width=600&lines=This+is+an+upcoming+app+that+will+be+used,;to+survey+the+company's+employees!)](https://git.io/typing-svg)

## Installation:

### Clone this repository using GitHub Desktop:

![Clone](docs/git-start.png)

## Preparations:

### .env:

Please, make sure that you have a .env in the root folder. Feel free to specify values of environmental variables as you
wish, but make sure that your .env file structured like .env.example.

## Run app:

- Run application:

      fastapi dev main.py

## Run app with Docker:

Firstly, you need to have [Docker](https://docs.docker.com/get-docker/) installed in your system.

- Run application:

      make run_app

## Apply migrations with Alembic

- Create migration. Usage `make create_migrations m="migration message"`:

      make create_migrations

- Apply migrations:

      make migrate

## Run test:

- Run test

      make run_test

## Interactive API docs:

      http://host:port/docs

After you will see the automatic interactive API documentation (provided by Swagger UI):

![OpenAPI](docs/docs.png)

- Run tests:
  pytest

## Poetry:

In this project used [Poetry](https://python-poetry.org/) environment

- Load all needed packages

      poetry install

- Add new package

      poetry add <package_name>

## Contributors:

- [Vita Yushchyk](https://github.com/vitayushchyk)