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

    -n, --name: The wallet name
    -p: this will start agent, and print DID and verykey, for test environment, if you don't register DID and verkey, please go to https://selfserve.sovrin.org/ to register.
    
2. `vsw init`

    -c,--connection, --connection: this option will init the connection with repo
    
    -s,--schema: this will init schema name and create credential definition

3. `vsw publish`
    publish your software credential
    This needs you provide software name and version, software did information.
    
4. `vsw verify`
    Verify if the software credential is correct. the following parameters are needed.
    -s,--software-name: The software name
    -u,--url: The download url
    -i,--issuer-did: The issuer did

5. `vsw list`

    List all the necessary information in the console
    -c, --connection: list the connections.
    -w, --wallet: list the wallet information.
    -sc, --schema: list the schema ids.
    -s, --status: list the agent status.
    -i, --issue_credential_records: list the issue credential records.
    -p, --present_proof: list the present proof records.
    -cs, --credentials: list the credential records.
    --cd, --credential_definition: list all the credential definition records.      
    
6. `vsw exit`
    Exit agent
    

# Verifiable Software

This project consists of the code for the client command line interface for interacting with that a [VSW repo](https://github.com/verifiablesoftware/vsw-repo).

For informal discussions, we use slack : vswhq.slack.com
Anyone is welcome to join the slack channel using this invitation link: https://join.slack.com/t/vswhq/shared_invite/zt-kxvaycqc-v5dSDLfpUVevtrZsHsOr9Q
Slack invitation link is timed. The above link is going to expired on Feb 12, 2021. We will try to watch and update the link timely. In case we missed it, or it isn't working for you, please file a github issue to alert us. Welcome to the vsw project.
