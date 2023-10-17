
# RSS Reader

API Based app that scrap rss link, creates feed and posts

[![GitHub Actions](https://github.com/mohamedmansor/rss-reader/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mohamedmansor/rss-reader/actions?workflow=CI)
 [![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/) [![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Stack Used

+ Docker

+ Docker Compose

+ PostgreSQL

+ Redis

+ Python

+ Django Rest Framework v. 3.13.1

+ Celery v. 5.2.3

+ Celery Beat v. 2.2.1

+ Flower v. 1.0.0

+ Mailpit (Locally)

## Docker

+ Docker; if you don’t have it yet, follow the [installation_instructions](https://docs.docker.com/install/#supported-platforms)

+ Docker Compose; refer to the official documentation for the [installation_guide](https://docs.docker.com/compose/install/)

+ See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

## Basic Commands

Then you can build the environment, this can take a while especially the first time you run this particular command on your development system:

> If make command is not installed use `sudo apt install make` command to install it.

```bash

make  build

```

To run server normally command:

```bash

make  up

```

To open bash or excute any manage.py commands:

```bash

make  bash

```

To create superuser:

```bash

make  createsuperuser

```

To make fast migration instead of opening bash:

```bash

make  makemigrations

make  migrate

```

To run unittests (with running Django container):

```bash

make  test_local

```

To down the stack :

```bash

make  down

```

## Flower

In order to view celery tasks status and workers assigned to. Visit [flower page](http://0.0.0.0:5555/)

#### Credentials

> The below credentials is a testing credentials.
```
FLOWER_USER = YRlBlTRxboEMyjZWiHKHtMZUurfgZnvk
FLOWER_PASSWORD = kIKWW2F7lupL1uphv8p9ND1tTTp4XWoywKXKRd9dqNRQKSOhC7Zkm1Y7fOdIDP2W
```


## API Swagger docs

The app APIs follows OAS to make it easy to service consumer integration. [API Docs](http://0.0.0.0:8000/api/docs/)
> NOTE you should up the stack using the above `$ make up` command to be able to view the DOCs


## Email Server

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container.

Container mailpit will start automatically when you will run all docker containers.

Please check [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html) for more details how to start all containers.

With Mailpit running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

## Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.

The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

### Scout APM
Scout Application Monitoring is a lightweight, production-grade application monitoring service built for modern development teams.

Update `.env/.production/.django` with the following settings
```

SCOUT_MONITOR=True
SCOUT_KEY=<YOUR_SCOUT_KEY>
SCOUT_NAME=RSS Reader Production

```

## Deployment

The following details how to deploy this application.

## What's Next?

+ Using caching on the GET APIs Views and ORM
  + Cache on the ORM level using 3rd party package like: [Django Cacheops](https://github.com/Suor/django-cacheops)
  + Cache on the View level using either the base DRF decorators.
  + Most importantly invalidate
+ ~~Integrating scout APM~~
+ Update `make deploy` command to deploy stack

## License

Open source licensed under the MIT license (see LICENSE file for details).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
