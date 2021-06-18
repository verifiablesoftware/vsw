# Developer's Read Me for VSW Client - Python <!-- omit in toc -->

This project consists of the code for the client command line interface for interacting with that a [VSW repo](https://github.com/verifiablesoftware/vsw-repo).

For informal discussions, we use slack : vswhq.slack.com
Anyone is welcome to join the slack channel using this invitation link:https://join.slack.com/t/vswhq/shared_invite/zt-rcme6kt2-l08LWW_HdF0DVvwYeQIsbg
Slack invitation link is timed. The above link is going to expired on July 7, 2021. We will try to watch and update the link timely. In case we missed it, or it isn't working for you, please file a github issue to alert us. Welcome to the vsw project.


## Table of Contents <!-- omit in toc -->

- [Developing](#developing)
  - [Prerequisites](#prerequisites)
  - [Virtual Environment Installation](#virtual-environment-installation)
  - [Component](#components)
  - [Storage](#storage)
  - [Logger](#logger)
- [How to package vsw](#how-to-package-vsw?)
- [How to upload to pypi.org](#how-to-upload-to-pypi.org)
- [How to install vsw](#how-to-install-vsw-with-pip)
- [How to run vsw](#how-to-run-vsw)


## Developing
### Prerequisites
[`Python: >= 3.6`](https://www.python.org/downloads/)

[`NodeJS: >= 14.15`](https://nodejs.org/en/)

[`Recommend IDE: Pycharm`](https://www.jetbrains.com/pycharm/download/#section=mac)

### Virtual Environment Installation

```
git clone https://github.com/verifiablesoftware/vsw.git
pip3 install virtualenv
cd project root directory
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Components
There are also 3 daemon processes are running at the same time when vsw is running.
You can check them with command below.

```ps -ef|grep vsw```
#### aca-py 
This is used to communicate with aca-py in repo
#### vsw-controller
This is used to receive the notification of webhook from aca-py, also save credential in the local.
#### [localtunnel](https://github.com/localtunnel/localtunnel)
This is used to exposes your localhost to the world for easy testing and sharing! No need to mess with DNS or deploy just to have others test out your changes.

The localtunnel is installed in the following folder when 'pip3 install vsw'  
```~/vsw_tools/localtunnel-master```


### Storage
The wallet information and credential information are saved in the local sqlite database.
The sqlite database file is saved in the following path.

```~/.indy_client```


### Logger
The logger file is placed in the the following folder.

```~/vsw_logs```

There are four logger files in this folder.  
aries-cloud-agent.log (for aca-py)     
lt.log (for localtunnel)  
vsw-controller.log (for vsw controller)     
vsw.log (for vsw)



## How to package vsw?
cd vsw project root directory, then execute the following command.

`python setup.py sdist bdist_wheel`

## How to upload to pypi.org
For production: 

`twine upload dist/*`

For test: 

`twine upload --repository testpypi dist/*`

## How to install vsw with pip
For production: 

`pip install vsw`

For test: 

`pip install -i https://test.pypi.org/simple/ vsw`

For local install, 

cd dist/, then execute the following command

`pip install vsw-x.x.x-py3-none-any.whl`

If you have already locally installed it before, need to uninstall it firstly.

`pip uninstall vsw-x.x.x-py3-none-any.whl`

## How to run vsw
1. `vsw setup`

    **newwallet:** create new wallet
    
    &emsp;&emsp;&emsp;&emsp;name: the wallet name
      
    &emsp;&emsp;&emsp;&emsp;-k,--key: the wallet key
      
    **wallet:** start the created wallet
    
    &emsp;&emsp;&emsp;&emsp;name: the wallet name
    
    &emsp;&emsp;&emsp;&emsp;-k,--key: the wallet key
    
    &emsp;&emsp;&emsp;&emsp;-p,--ports: The ports number, format is (<endpoint_port>,<admin_port>,<webhook_port>)
      
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
    


