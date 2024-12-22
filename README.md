# FastAPI JWT Authentication

This a FastAPI JWT authentication app built with Python.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

## Building Procedure
To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you are ready to Run the app

```
$ python main.py
```
Now, You are ready to Access Your App under http://localhost:8000/

## Usage

1. Generate the Bearer Token
```commandline
curl --location 'localhost:8000/token' \
--form 'username="admin"' \
--form 'password="<password>"'
```
2. Access the apps with bearer token
```commandline
curl --location --request GET 'localhost:8000/' \
--header 'Authorization: Bearer <generated_token>' \
--form 'username="username"' \
--form 'password="password"'
```