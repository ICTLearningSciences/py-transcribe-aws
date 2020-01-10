py-transcribe-aws
===================

AWS Transcribe implementation of [py-transcribe](https://github.com/ICTLearningSciences/py-transcribe)

Python Installation
-------------------

```
pip install --user -e git+https://github.com/ictlearningsciences/py-transcribe-aws.git@{release-tag}#egg=transcribe
```


Development
-----------

Run tests during development with

```
make test-all
```

Once ready to release, create a release tag, currently using semver-ish numbering, e.g. `1.0.0(-alpha.1)`