# Introduction
The **vsw** DID method specification conforms to the requirements specified in the [DID specification]
(https://w3c-ccg.github.io/did-spec/), currently published by the W3C Credentials Community Group.
For more information about DIDs and DID method specifications, please see the [DID Primer]
(https://w3c-ccg.github.io/did-primer/)

Most of the existing DID methods identify an actor who can exercise control in an ecosystem,
for example a human or a human organization. In vsw, we need a new type of DID that identifies a
passive object (certain piece of software) that are controlled by an active DID. Software also has
unique challenges in identifying various degree of specificity to fit dynamic needs that emerge in
modern software ecosystems.

# Unique Concepts
**vsw** enables developers and other parties to publish verifiable credentials about a piece of software.
The prerequisite of this is to have a DID uniquely identifying the given piece of software. In common
software development practice, the concept of a given piece of software is often fluent and vague, however,
with various degree of specificity. For example, when a child says, "I love to play HappyBird." She refers
generally about the software App named "HappyBird". While a software tester may say, "HappyBird 1.0.1 build
is broken." She refers to a specific version's most current build is not building successfully.
We need to design the **vsw** DID method to accomodate these kinds of variants.

Knowing who developed a piece of software is a critical factor for a user to decide whether or how much
to trust this software. In **vsw**, this is represented by the Controller of the vsw DID. This entity (person
or organization) is identified by another DID using one of the common active DIDs. The **vsw-did**, in contrast,
is a passive DID.

# Illustration

# An Example

# Method Name

# Method Specific Identifier

# CRUD Operations

## Create

## Read (Resolution)

## Update

## Delete (Revoke)

# References
