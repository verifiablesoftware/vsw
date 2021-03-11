# How to package vsw?
cd vsw project root directory, then execute the following command.

`python setup.py sdist bdist_wheel`

# How to upload to pypi.org
For production: 

`twine upload dist/*`

For test: 

`twine upload --repository testpypi dist/*`

# How to install vsw with pip
For production: 

`pip install vsw`

For test: 

`pip install -i https://test.pypi.org/simple/ vsw`

For local install, 

cd dist/, then execute the following command

`pip install vsw-x.x.x-py3-none-any.whl`

If you have already locally installed it before, need to uninstall it firstly.

`pip uninstall vsw-x.x.x-py3-none-any.whl`

# How to run vsw
1. `vsw setup`

    this will start agent, and print DID and verykey, for test environment, if you don't register DID and verkey, please go to https://selfserve.sovrin.org/ to register.
2. `vsw init`

    -c: this option will init the connection with repo
    
    --schema: this will init schema name and create credential definition

3. `vsw publish`
    publish your software credential
    
4. `vsw verify`
    verify if the software credential is correct. the following parameters are needed.
    --software-name
    --url
    --issuer-did
5. `vsw exit`
    exit agent
    

# Verifiable Software

This project consists of the code for the client command line interface for interacting with that a [VSW repo](https://github.com/verifiablesoftware/vsw-repo).

For informal discussions, we use slack : vswhq.slack.com
Anyone is welcome to join the slack channel using this invitation link: https://join.slack.com/t/vswhq/shared_invite/zt-kxvaycqc-v5dSDLfpUVevtrZsHsOr9Q
Slack invitation link is timed. The above link is going to expired on Feb 12, 2021. We will try to watch and update the link timely. In case we missed it, or it isn't working for you, please file a github issue to alert us. Welcome to the vsw project.
