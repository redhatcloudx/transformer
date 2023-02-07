# RHEL Cloud image locator

This project is a work in progress with a goal of making it easier to find Red
Hat Enterprise Linux™ at various public cloud providers.


## Development guide

[Poetry] is used for dependency management and centralized configuration for testing and
linting tools. Start by [installing poetry] and then clone the repository.

After cloning, run the following:

```console
poetry install
```

Pre-commit hooks are used to ensure that code passes the linter checks before you push.
Prepare the pre-commit hooks on your computer by running some commands:

```console
poetry run pre-commit install
poetry run pre-commit run --all-files
```

You can quickly run tests with `poetry run pytest` or run the full pre-commit suite with
`poetry run pre-commit run --all-files`. Or, simply start a commit (such as `git commit -m "Fixed the bug"`) and the pre-commit checks run automatically.

If you need to add more Python packages to poetry, run the following:

```console
# For packages that this project requires in production
poetry add foo

# For packages that are only needed for linting, testing, or development work
poetry add --group dev bar
```

## Locator API server

### Running the Flask server locally
You can run the API server locally by using the cloudimagedirectory cli command `serve`:
`poetry run cloudimagedirectory-updater serve --file-path <path to formatted image data> --dev`

```console
Usage: cloudimagedirectory-updater serve [OPTIONS]

  Host API endpoint to serve cloud provider image data.

Options:
  -f, --file-path TEXT  Path to JSON image data file.
  -p, --port INTEGER    Port to run Locator API at.  [default: 5000]
  -h, --host TEXT       Address to run Locator API at.  [default: 0.0.0.0]
  -d, --dev             Run in development mode.
  --help                Show this message and exit
```

While running the dev server, the swagger documenation will be available at
http://127.0.0.1:5000/apidocs/ by default.

### Configuring the Flask server
The API server will read its configuration on boot from the .env file located in
`src/cloudimagedirectory/api/.env`.

### How to build the API container on your local system
1. Build the container from within the cloudimagedirectory directory:
```
podman build -f Containerfile -t cloudimagedirectory:latest .
```

2. Run the container, forward the Flask default port 5000 and mount a json file containing test data to
`/opt/cloudimagedirectory/opt/cloudimagedirectory/data/image-data.json`.
```
podman run -p 5000:5000  -v ./tests/api/testdata/formatted_images.json:/opt/cloudimagedirectory/data/image-data.json:Z cloudimagedirectory
```
Mind that this is only meant for local testing and should not run like this in production. The Z operator at the end of the
volume mount is necessary for SELinux and applies the same (MCS)[https://en.wikipedia.org/wiki/Multi_categories_security]
labels to the mounted data that the container will run with. For more information see this former (Project Atomic)[https://projectatomic.io/blog/2015/06/using-volumes-with-docker-can-cause-problems-with-selinux/] article (now CoreOS).

## Running tests

Use poetry to run pytest:

```commandline
# Run all tests, including end-to-end tests that call out to cloud APIs:
poetry run pytest

# Skip any tests that communicate remotely:
poetry run pytest -m "not e2e"
```

[Poetry]: https://python-poetry.org/
[installing poetry]: https://python-poetry.org/docs/#installation

## Secrets

End-to-end tests and the CLI both require access to cloud provider APIs.
Secrets must be available via environment variables for each cloud.

### AWS

Access the IAM dashboard inside the AWS cloud console and click _Policies_.
Click _Create policy_ and then click the _JSON_ tab on the next screen.
Paste in the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeImages",
                "ec2:DescribeImageAttribute"
            ],
            "Resource": "*"
        }
    ]
}
```

Click through the _Next_ buttons, add a name for the policy, and create the policy.

Back on the IAM dashboard, click _Users_ and then _Add users_.
Enter a username on the next screen and tick the _Access key - Programmatic access_ checkbox.
Click _Next_, then _Attach existing policies directly_.
Search for the policy you just created in the list.
Click the _Next_ buttons and finally _Create user_.

On the next screen, copy the access key ID and secret access key.
Both of these credentials must be set as environment variables before end-to-end tests will run and the CLI will function:

* `AWS_ACCESS_KEY_ID`: your access key ID from above
* `AWS_SECRET_ACCESS_KEY`: your secret access key from above

### Azure

Azure requires multiple environment variables:

* `AZURE_CLIENT_ID`: provided when you register your application
* `AZURE_CLIENT_SECRET`: provided when you register your application
* `AZURE_TENANT_ID`: provided when you register your application
* `AZURE_SUBSCRIPTION_ID`: the subscription UUID

### Google

Google requires one environment variable that points to a JSON file or a block of JSON text.

* `GOOGLE_APPLICATION_CREDENTIALS`: path to JSON credentials file or a block of JSON credentials text

## Running the latest Cloud Image Locator backend
1. Pull the newest locator image from quay:
```
podman pull quay.io/cloudexperience/cloud-image-locator:latest
```

2. Run the locator and forward the default port:
```
podman run -p 5000:5000 cloud-image-locator
```
