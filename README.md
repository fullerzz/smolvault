# smolvault

smolvault is a self-hosted file storage tool I built to run on my Raspberry Pi.

## Overview

At its core, smolvault is a Python REST API written with [FastAPI](https://fastapi.tiangolo.com) that manages users and files.

File metadata is stored in a SQLite table while the uploaded files themselves are stored in S3.

> [!NOTE]
> When a user requests a file, that file is cached locally on the server for an indeterminate amount of time to improve subsequent download requests.

### IAC - AWS Resources

This project also includes a `terraform` directory containing code to setup IAM resources and an S3 bucket to store the uploaded files.
