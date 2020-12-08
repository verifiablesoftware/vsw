# Web Interface for VSW Repo

The VSW repository needs some web-based interface to handle interactions that do
not make sense to occur over DIDComm. This document describes these interfaces.

## Web

### The Basics

The repository should have a home page with basic information about VSW:

- Documentation explaining how verifiable software works and why it exists
- Download link for vsw tools
- Installation instructions for vsw tools
- Usage instructions for vsw tools

If the repo's DID and invitation are not hard-coded into the tool, then they
should be provided on this site as well.

### Software Listing and Search

Visitors to the website should be able to browse the software listings in the
repo and search through these listings.

## Rest API

A REST API should provide programmatic access to the same information provided
on the website:

- Retrieve repo's public DID
- Retrieve repo's invitation
- Retrieve a list of packages available in the repo
- Search packages in the repo
