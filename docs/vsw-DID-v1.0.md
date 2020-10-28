# Introduction
For **vsw** v1, our implementation relies on [ACA-py agent](https://github.com/hyperledger/aries-cloudagent-python)
which currently does not support cross ledger. In this specification, we design an approach that can be implemented
leveraging the existing verifiable credential registry [Sovrin network](https://sovrin.org/developers/).

Sovrin network consists of 3 instances of networks running in Indy Node.
 - BuilderNet: for development testing (aka Sandbox)
 - StagingNet: for deployment testing (aka POC)
 - MainNet: for operational deployment
 
Our development work can use the two testing networks, using the BuilderNet for development and the StagingNet for
Proof of Concept deployment.

# vsw v1 DID and Verifiable Credential Features
Most of the existing DID methods identify an actor who can exercise control in an ecosystem (being **active**),
for example a human or a human organization or an automated system. In **vsw**, we need a new type of DID that identifies a
passive object (i.e. a unit of software) that is controlled by an active DID. Software also has
unique challenges in identifying various degree of specificity and complex dependencies to meet dynamic needs that emerge in
modern software ecosystems.

## DIDs used in vsw
**vsw** v1 uses various types of DIDs. One is to identify an active participant in the **vsw** ecosystem, e.g. a developer,
a tester, an auditor, and so on. The other type is to identify a unit of software, which we describe in more detail
below. For both types, we use **did:sov** which is implemented using Indy Node and is compatible with ACA.py agent.

For the DIDs representing participants who issue credentials, they need Public DIDs (aka Write DIDs) to write to the ledger.
For example, suppose a company Happy Software, Inc. publishes a game HappyBird. The company will need a public DID to issue
credentials about the software HappyBird. Suppose an independent testing organization Games Unlimited wants to publish its
evaluation of HappyBird, it will also be issuing credentials and need a public DID. General game players will not need a public
DID as they only verify credentials presented by the registry.

In the ACA-py agent, Peer DIDs are used for those who do not need to issue credentials by their own public DIDs. Ordinary
consumers of software, e.g. the game players, do not necessary need a public DID. Peer DIDs are used to facilitate the 
credential verification process (request for proof, and presentation of proof). If an individual software developers wants
to publish credentials about any software, then he or she is acting as a credential issuer and will need a public DID.

## vsw Repository Roles
The **vsw** repository may play multiple roles. It is important that we differentiate these roles. The most important role
it plays is as the **holder** of verifiable credentials issued. As a holder, it can interact with a consumer answering his/her
proof request with a presentation of proof. The consumer can accept the proof as if it is from the issuer (**transitive trust**).
In this role, the **vsw** repository is a convenient digital **registry** where consumers can request for verifiable information.
Note that the role of a verifiable credential registry does not imply a "centralized" authority because the trust rests with
the issuers, not the holder.

During the transition period until public DIDs are widely available and adopted, we may provide a convenience utility to
allow individual developers to rely on **vsw** to issue credentials on their behalf as a proxy. In this role, we will allocate
a commonly known public DID for **vsw** to issue these credentials. With the credentials, the developer of the software is
identified as the true developer, by name and email address, for instance. 

Finally, **vsw** may also serve as the storage system for the published software where consumers can verify its credentials
as well as downloading safely using hashlink to ensure its integrity. This role can be played by other storage systems as
well.

## Authenticated Controllers
Knowing who developed a piece of software is a critical factor for users to decide whether or how much
to trust this software. In **vsw**, this is represented by the **Controller** of the software's DID. This entity (person
or organization or automated system) is identified by the active participant DID. The **software**, in contrast,
is identified by a **passive** DID. These concepts are further discussed in the [Proposed DID Core Appendix](https://github.com/w3c/did-core/issues/373).
In the diagram below, we illustrate graphically the controller relationship.

![Controller Relationship](assets/Controller-relationship-v1.png).

## Semantic Versioning
**vsw** is designed to enable developers and other parties to publish verifiable credentials about a unit of software.
The prerequisite of achieving this is to have a DID uniquely identifying the given unit of software. In common
software development practice, the concept of a unit of software is often fluent and vague, however,
with various degree of specificity. For example, when a child says, "I love to play HappyBird.", she is refering
generally about the App named "HappyBird". While a software tester says, "HappyBird 1.0.1 build
is broken", she is refering to a specific version's the software bearing the name "HappyBird".
We need to design the **software DID** to accomodate these kinds of variants. Specifically, we are to support
the Semantic Versioning functions as defined by [SemVer](https://semver.org).
In the diagram below, we illustrate graphically the semantic versioning relationship.

![Semantic Versioning Relationship](assets/Semantic-versioning-v1.png).

### Sub-Versioning
Semantic Versioning uses X.Y.Z format, where X is a Major release, Y is a Minor release and Z is a Patch release.
Developers may choose to allocate a **software DID** for each Minor release and Major release as shown in the above
example (or a different variation). A need arises when a user likes to download a specific patch release, e.g. 1.0.1,
which does not have its own DID. In such cases, the patch versions must be listed in the parent DID Document with a series of
cryptographic hashlinks (see next section) which can be dereferenced using DID URL. This scheme implies that the DID Document
will be updated every time that a new patch is produced. 

**Implementation note**: I'm not certain if ACA-py or Indy Node currently supports DID URL dereferencing. If not, then the
above procedure can be implemented by first DID resolution (locating the DID Document), then parse the DID Document to
locate the field which contains the list of patches.

### LATEST
This above design also supports other naming of versions, e.g. LATEST can also be expressed with DID URL path.
LATEST is defined as the last patch in the DID Document's patch list. The concept of LATEST is fined to the
current minor or major release that the DID identifies. In other words, it does not go up to a parent (see below).

### Predecessor, Successor and Parent
A user (consumer of software) who knows the DID of HappyBird 1.1 may want to find out information about its
predecessor HappyBird 1.0. [SemVer](https://semver.org) defines predecessor ordering. Similarly, one may want to
know the successor version of the software identified by the DID, which is HappyBird 1.2.

**vsw** also defines superset (**parent**) relationship. For example, HappyBird 1.1.0's **parent** is *HappyBird 1*, whose
**parent** is in turn *HappyBird*.

## Cryptographic Hashlink
In traditional software distribution systems, the software image and its SHA integrity check are often separate.
It therefore leaves a gap where the hosting system could make changes without the users noticing. A cryptographic hashlink
is designed close this gap and, at the same time, allow flexibility in repository systems where the software image is hosted. 
The hashlink can be a field in the DID document and a hashlink in the DID URL. Dereferencing operation of this DID URL
is successful only if the referenced file produces an identical hash. With a cryptographic hashlink, a user will know if
a file has been changed either intentionally or accidentally, or maliciously (e.g. by an attacker).
In the diagram below, we show an example of **hl** hashlink that, when dereferenced, returns unchanged software image.
For details of hashlink, please refer to this [IETF Draft](https://tools.ietf.org/html/draft-sporny-hashlink-05).

![Hashlink](assets/Hashlink-DID-URL-v1.png).

Hashlink and hashlink dereferencing does not involve DID resoltion, so this feature can be implemented in **vsw** on
top of the **did:sov** method without causing issues.

# vsw Schemas

## vsw Participant Credential Schema
**vsw** **MAY** need to be able to issue credentials to participants. This schema is to define data fields for the type of credentials
that can adequately identify a developer, tester, auditor etc. For example, name and some contact information
such as email address. This credential links an email address and a name to a user who does not have to be an issuer, i.e. 
general users or consumers.

Note that since it is a very basic schema, there should have a published schema already. **vsw-repo** writes a credential definition
using its public DID to the ledger.

## vsw Software Credential Schema
We do need to define a schema that supports the **vsw** features defined above.
See Issue [#4](https://github.com/verifiablesoftware/vsw/issues/4).
**vsw-repo** publishes at least one software credential schema (or multiples eventually) to the ledger using its public DID.
Other developers may use their own credential schema as well.

## vsw Software Test Credential Schema
We also need to define a schema that supports software test credentials.
See Issue [#40](https://github.com/verifiablesoftware/vsw/issues/40)
**vsw-repo** publishes at least one software credential schema (or multiples eventually) to the ledger using its public DID.
Other testers may use their own credential schema as well.

## Publish Schema
The **vsw-repo** acts on behalf of the ecosystem to define and publish schema, as defined above.  
Others can define and publish additional schema as well. This is typically done as a common act of the ecosystem, so it's a good
practice for **vsw-repo** do publish standard ones.

# vsw Credentials

## Issuer DID (aka Write DID)
In **vsw** v1, there are many issuer of software credentials, e.g. developers, testers.

To become an issuer of software credentials, the participant must register a public DID (in Sovrin ledger). 
We envision that the company (or the department within that company) who develops HappyBird would have one
such public DID. (In Sovrin network, this DID costs $10 and every rotation of the keys costs another $10. This fee
reflects the cost of all future verification of identify related to this issuer. )

For participants who do not wish to or do not need to be an issuer, in **vsw**, the vsw repository can proxy as a
common issuer on behalf of these participants. These participants already have a peer DID and may
have been issued a participant credential which they can use to prove their identify (i.e. the name and email address
information contained in the credential). The vsw-repo can issue the
software credential with a field that states who is the origin of the claims (i.e. the name and email address etc.)

The choice of using one's own issuer DID or the common proxy should be enabled by an option in the **vsw register**
command. Note that the default case is when one has a public DID to issue these credentials. If a participant chooses
to use the proxy, the credential will lose some trust level because the consumer must now trust the proxy. On the other
hand, in an open and transparent software ecosystem, the particpant can check the proxy's honesty by
verifying the credential he/she asks the proxy to issue.

## vsw Credential Definition
Before issuing credentials, an issuer must first define credentials using pre-defined schemas, In simple cases, a credential
definition only uses claims from a single Schema, but it could also combine claims from multiple schemas.

Each issuer has to do this step using their own public DID.

For the common default issuer **vsw-repo**, it needs to
  - define a participant credential which the vsw-repo will administer during **vsw register**
  - define a software credential, see **vsw publish**
  - define a software test credential (or software attest claims), see **vsw attest**
  - others TBD

All participants who are also issuers have similar requirements to define all credentials they wish to issue individually.
For example, a developer will need to define a software credential. A tester will need to define a test result credential.
These definitions uses a schema and binds with the issuer's DID.

This option should also be implemented in **vsw register** command as a subcommand.

## vsw Credential Issuance
With the credential definitions written to the ledger, an issuer can start issue credentials. This is done by
 - **vsw register** for participants
 - **vsw publish** for software by the developers
 - **vsw attest** for software by the testers/others
 
 Additional types of credentials are TBD.
 
## vsw Credential Revocation
TBD

# References
