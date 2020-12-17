# VSW User Manual

The `vsw` tool enables simple management of verified software. It allows you to
securely download software packages from trusted developers using a familiar
command line interface.

## Setup

The first step of the `vsw` setup is to create your wallet. A wallet provides
the keys necessary for securely communicating with the repository, as well as a
secure place to store credentials. To setup a new wallet, run:

```
vsw setup
```

This will create a file, _.vsw_wallet_ in your home directory. If you already
have an existing wallet, place it in the same location, then you can skip this
step.

## Installing Software

Now you can begin installing software with `vsw`.

```
vsw install example/foo
```

The above example will look for a package `foo` from developer `example` in the
registry. If it is found, it will be downloaded and verified. The verification
process ensures that the software was properly published and signed by the
specified developer. If successful, the package is installed in a subdirectory
of the current directory, in this case _vsw_packages/example/foo/_. If this is
package contains a binary, it will be symlinked in _vsw_packages/bin/_.

To install the package globally, use the `-g` flag:

```
vsw install -g example/foo
```

This performs the same process as the local install, except that it installs the
package to the global vsw directory, _/usr/local/lib/vsw_packages_ and symlinks
binaries into _/usr/local/bin/_.

## Developer Registration

_NOTE: This step is required only for developers that will be submitting
software to the registry. If you are a user, and will only download software,
you may skip this step._

In order to submit your software to the registry, you must first register an
account. This establishes your identity with the registry, which will be
associated with all publications. To register, you will use the following
command:

```
vsw register
```

This command will prompt you for a username, then register your account with
that username. Since it uses the key in your wallet, there is no need for a
password. Once the username has been successfully registered, you can optionally
verify a web domain, email address, or GitHub account. Verifying one or more of
these allows your vsw account to be linked with your other public identities,
enhancing your trustworthiness to your customers. Follow the directions provided
on the command line to complete this step.

## Publishing a Package

A registered developer may publish a package to the repository. A package could
technically be any digital asset, but the focus of this tool is for publishing
software libraries and executables. To create a package, you must create a
_vsw_package.json_ file in your directory. This is a configuration file that
describes the package and how it should be distributed, using JSON formatting.
It must contain the following fields:

```json
{
  "name": "foo",
  "version": "1.0.0"
}
```

You can also create this file interactively using the command:

```
vsw init
```

This will prompt you for the various fields of the file and generate it for you.

With this file in place, you can run the following command to publish a package:

```
vsw publish
```

This will package up all files in the current directory and send them to the
repository to be published, allowing users to then install this package using
(assuming username `example`):

```
vsw install example/foo
```

Additional fields in _vsw_package.json_ allow you to modify the default
behavior:

- `description` specifies a short description of the package that will show in
  listings and searches.
- `keywords` provides search terms to help users find your package
- `homepage` specifies a URL that users may want to visit to learn more about
  this package.
- `bin` specifies a list of binary files that should be symlinked to the _bin/_
  directory so that they can easily be included in the users' path.
- `files` specifies a list of files or directories that should be included in
  the package. By default, all files in the current directory are included in
  the package, except for those specified in the file _.vswignore_ or if that
  file does not exist, _.gitignore_. If this field is used, then instead of
  using the _\*ignore_ file as a blocklist, the list in this field serves as an
  allowlist, meaning only those files listed are included in the package.
