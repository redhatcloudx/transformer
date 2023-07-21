# Cloud Image Directory

This is an experimental project and a work in progress with the goal of making it easier
to find Red Hat Enterprise Linux™, Fedora and, in the future, a bunch of other linux images
at various public cloud providers.

## Components

This repository contains the tool `cloudimagedirectory-transformer`, which is used to transform the unstructured data provided by `cloud-image-retriever` into a predefined schema for the `directory-frontend`.

It belongs to three other sub projects:

- [cloud-image-retriever](https://github.com/redhatcloudx/cloud-image-retriever): Used to retrieve unstructured image data from public cloud providers.
- [infrastructure](https://github.com/redhatcloudx/infrastructure): Defines the public cloud infrastructure [imagedirectory.cloud](https://imagedirectory.cloud/).
- [directory-frontend](https://github.com/redhatcloudx/cloud-image-directory-frontend) Used to visualize the dataset.

### Architecture diagram

![Architecture diagram](assets/arch-diagram.png)

The Collector(`cloud-image-retriever`) fetches the images from different cloud providers on a predefined interval. This data is then stored in a s3 bucket.
After a successful collection, the transformer(`cloudimagedirectory-transformer`) reads the unstructured image data from the S3 bucket and generates static image content in a consumable format. The transformer also generates lookup tables to allow for efficient searches from e.g. a js single page application. Once the transformation is complete, it's written back into the s3 bucket.
In parallel, frontend code is deployed by putting it into the s3 bucket too. This is done by a [release pipeline](https://github.com/redhatcloudx/cloud-image-directory-frontend/blob/main/.github/workflows/release.yaml).
Finally the S3 bucket gets synchronized with the CDN provider in a reasonable interval.

## Development guide

We use a helpful `Makefile` based on the one from [cookiecutter-poetry](https://fpgmaas.github.io/cookiecutter-poetry/) for setting up the environment, running linters, and running tests.

After cloning, set up your local development environment by running:

```shell
make install
```

Pre-commit hooks are run during the commit process, but you can test your code and run linters at any time with these commands:

```shell
# Run tests only
make test

# Run linters only
make check

# Run tests and then run linters
make test check
```

If you need to add more Python packages to poetry, run the following:

```shell
# For packages that this project requires in production
poetry add foo

# For packages that are only needed for linting, testing, or development work
poetry add --group=dev bar
```