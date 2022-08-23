# PWS

### Build:
<!-- [![<ORG_NAME>](https://circleci.com/<VCS>/<ORG_NAME>/<PROJECT_NAME>.svg?style=svg)](<LINK>) -->
[![CircleCI](https://circleci.com/gh/kiotapay/pms.svg?style=svg&circle-token=90ce5f9f69e9c08d676417a95da329999147a1a3)](<LINK>)


<!-- # Example for specific branch:
[![CircleCI](https://circleci.com/gh/circleci/circleci-docs/tree/teesloane-patch-5.svg?style=svg)](https://circleci.com/gh/circleci/circleci-docs/?branch=teesloane-patch-5) -->

[![CircleCI](https://circleci.com/gh/kiotapay/pms.svg?style=svg&circle-token=90ce5f9f69e9c08d676417a95da329999147a1a3)](<LINK>)

## Deployment
Project API demo is hosted on [Heroku](http://herokuapp.com)

## Prerequisites

-   Git
-   [VS Code](https://code.visualstudio.com)
-   [Python 3.8](https://www.python.org)
-   [Postman](https://www.getpostman.com)
-	[PostgreSQL](https://www.postgresql.org/)

## Installation
-  Setup SSH keys [Git SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
-   Clone the repo

```
$ git clone git@github.com:kiotapay/pms.git
```

-   Create and set a virtual environment
```
$ cd pms && virtualenv env && python3 -m venv env
```

-   Activate the virtual environment

```
$ source env/bin/activate
```

-   Install dependencies

```
$ pip install -r requirements.txt

```

-   Set the environment variables

```
$ mv .env.example .env
$ source .env

```

-   Run the app

```
$ flask run

```

-   Testing

```
$ pytest --cov=app

```


## Endpoints (V2)

|         HTTP       |URI                          |ACTION                         |
|----------------|-------------------------------|-----------------------------|
|POST|`/api/v1/register`           |Register user            |
|POST|`/api/v1/properties`           |List properties            |


