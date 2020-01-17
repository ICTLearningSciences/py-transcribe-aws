py-transcribe-aws
===================

AWS Transcribe implementation of [py-transcribe](https://github.com/ICTLearningSciences/py-transcribe)

Python Installation
-------------------

```
pip install --user -e git+https://github.com/ictlearningsciences/py-transcribe-aws.git@{release-tag}#egg=transcribe
```

With pip

```
pip install git+https://github.com/ictlearningsciences/py-transcribe-aws.git@{release-tag}#egg=transcribe_aws
```

...in a pip `requirements.txt` use this syntax:

```
transcribe_aws @ git+https://github.com/ictlearningsciences/py-transcribe-aws.git@{release-tag}#egg=transcribe_aws
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

The following config vars can be set in ENV or passed in code, e.g. `init_transcription_service(config={})`

#### AWS_REGION 

(required)

The region hosting the S3 bucket to which source audio (or video) files will be uploaded for transcription

#### AWS_ACCESS_KEY_ID 

(required)

#### AWS_SECRET_ACCESS_KEY

(required)

#### TRANSCRIBE_AWS_S3_BUCKET_SOURCE

(required)

Bucket where source will be uploaded and then passed to AWS Transcribe

### AWS Permissions

The AWS IAM used must have permissions to read/write/delete from the configured source bucket and also use AWS Transcribe

TODO: give exact details on minimum permissions/policies.


Development
-----------

Run tests during development with

```
make test-all
```

Once ready to release, create a release tag, currently using semver-ish numbering, e.g. `1.0.0(-alpha.1)`