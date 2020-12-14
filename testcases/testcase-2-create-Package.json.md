<pre>
name: create vsw package.json

Synopsis: Initialize vsw env

this test case will  be used to create the package.json file based on the user input only if the package.json file does not exist in the current directory. this command should prompt the user to enter the following fields if the the package.json file does not exist:
Package name:
version:
description:
repository: (i.e. Github repo):
search key words: (space separated)
author:
license:
DID:


if the package.json file does exist then the user should only be prompted to only enter
Package name:
version:
description
Repository (i.e. Github repo):

Execution Steps:
    1- cd ~/myproject
    2- vsw init


Expected output:

vsw_package.json
{
  "name": "testpckg",
  "version": "1.0.0",
  "description": "test package"
  },
  "repository": {
    "type": "git",
    "url": "local file"
    "sha": "sha-reference"
  },
  "keywords": [
    "testpckg",
    "testpackage"
  ],
  "author": "your name",
  "license": "Apache",
  "DID":  "did:example:12345"
}
</pre>
