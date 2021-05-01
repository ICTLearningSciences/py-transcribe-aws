py-transcribe-aws
===================

Simple library for running batch transcribe jobs in AWS. Implemented on the [py-transcribe](https://github.com/ICTLearningSciences/py-transcribe) framework to make your code transcribe-platform agnostic and easy to test.

Python Installation
-------------------

```
pip install py_transcribe_aws
```

## Usage

### Setting the implementation module path

Set ENV var `TRANSCRIBE_MODULE_PATH`, e.g.

```bash
export TRANSCRIBE_MODULE_PATH=transcribe_aws
```

or pass the module path at service-creation time, e.g.

```python
from transcribe import init_transcription_service


service = init_transcription_service(
    module_path="transcribe_aws"
)
```

### Basic usage

Your code generally should not need to access any of the implementations in this module directly. See [py-transcribe](https://github.com/ICTLearningSciences/py-transcribe) for docs on usage of the framework.

### ENV/config vars

The following config vars can be set in ENV or passed in code, e.g. `init_transcription_service(config={})`. Most env vars have two accepted versions and the version with a `TRANSCRIBE_` prefix has higher precedence.

*TRANSCRIBE_AWS_REGION|AWS_REGION*

(required)

The region hosting the S3 bucket to which source audio (or video) files will be uploaded for transcription

*TRANSCRIBE_AWS_ACCESS_KEY_ID|AWS_ACCESS_KEY_ID*

(required)

*TRANSCRIBE_AWS_SECRET_ACCESS_KEY|AWS_SECRET_ACCESS_KEY*

(required)

*TRANSCRIBE_AWS_S3_BUCKET_SOURCE*

(required)

Bucket where source will be uploaded and then passed to AWS Transcribe

AWS Configuration
-----------------

### Using Terraform

This repo includes a terraform module for setting up all the necessary infrastructure to run transcribe.

You can include the terraform module, like this:

```hcl
module "transcribe_aws" {
    source                  = "git::https://github.com/ICTLearningSciences/py-transcribe-aws.git?ref=tags/{CHANGE_TO_LATEST_VERSION}"
    transcribe_namespace    = "YOUR_NAMESPACE"
}
```

...and then the module exposes all the (sensitive) env vars for running transcribe in an output map, which you can use like

```hcl
resource "some_server_type" {
    # set TRANSCRIBE_AWS_ACCESS_KEY_ID, TRANSCRIBE_AWS_SECRET_ACCESS_KEY, etc. in some server-resource env
    env = module.transcribe_aws.transcribe_env_vars  
}
```


### If You're Setting up Permissions Manually...

If you setting up AWS infrastructure manually (as opposed to using the terraform aboice), the AWS IAM used must have permissions to read/write/delete from the configured source bucket and also use AWS Transcribe

A minimal(ish) policy to allow the above might look like this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:*Object"],
            "Resource": "arn:aws:s3:::${YOUR_S3_BUCKET_NAME}/*"
        },
        {
            "Effect": "Allow",
            "Action": ["transcribe:*"],
            "Resource": "*"
        }
    ]
}
```


Development
-----------

Run tests during development with

```
make test-all
```

Once ready to release, create a release tag, currently using semver-ish numbering, e.g. `1.0.0(-alpha.1)`