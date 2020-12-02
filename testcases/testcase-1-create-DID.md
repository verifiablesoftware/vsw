<pre>
command: vsw register


Synopsis: create a new DID

Description:

this test case will create keys (signing and encryption keys) for a new DID (owned by the
caller of the library). Identity’s DID must be either explicitly provided, or taken as the
first 16 bit of verkey. Saves the Identity DID with keys in a secured Wallet (.MyWallet), so that it 
can be used to sign and encrypt transactions.

Execution Steps:
	1- mkdir ~/myproject
	2- cd ~/myprojeect
	3- vsw register

Expected output:
.MyWallet

Example of relative and absolute DID URL:

{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:example:123456789abcdefghi",
  "verificationMethod": [{
    "id": "did:example:123456789abcdefghi#key-1",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:example:123456789abcdefghi",
    "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }, ...],
  "authentication": [
	// a relative DID URL used to reference a verification Method above

    "#key-1"
  ]
}

In the example above, the relative DID URL value will be transformed to an absolute DID URL value of did:example:123456789abcdefghi#key-1. 
</pre>

