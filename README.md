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

    **newwallet:** create new wallet
    
    &emsp;&emsp;&emsp;&emsp;name: the wallet name
      
    &emsp;&emsp;&emsp;&emsp;-k,--key: the wallet key
      
    **wallet:** start the created wallet
    
    &emsp;&emsp;&emsp;&emsp;name: the wallet name
    
    &emsp;&emsp;&emsp;&emsp;-k,--key: the wallet key
      
    **connection:** create connection
    
    **creddef:** create credential definition
    
    &emsp;&emsp;&emsp;&emsp; -s,--schema: the schema name
      
2. `vsw publish`

    publish your software credential
    
    -c,--cred-file: The cred json file path
    
3. `vsw verify`

    Verify if the software credential is correct. the following parameters are needed.
    
    -p,--proof-request: The proof request json file path

4. `vsw list`

    List all the necessary information in the console
    
    -c, --connection: list the connections.
    
    -w, --wallet: list the wallet information.
    
    -sc, --schema: list the schema ids.
    
    -s, --status: list the agent status.
    
    -p, --present_proof: list the present proof records.
    
    -cs, --credentials: list the credential records.
    
    --cd, --credential_definition: list all the credential definition records.
    
5. `vsw exit`
    Exit aca-py agent, close vsw controller, localtunnel etc.
    

# Verifiable Software

This project consists of the code for the client command line interface for interacting with that a [VSW repo](https://github.com/verifiablesoftware/vsw-repo).

For informal discussions, we use slack : vswhq.slack.com
Anyone is welcome to join the slack channel using this invitation link: https://join.slack.com/t/vswhq/shared_invite/zt-kxvaycqc-v5dSDLfpUVevtrZsHsOr9Q
Slack invitation link is timed. The above link is going to expired on Feb 12, 2021. We will try to watch and update the link timely. In case we missed it, or it isn't working for you, please file a github issue to alert us. Welcome to the vsw project.
