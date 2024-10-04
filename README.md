<!--
Avoid using this README file for information that is maintained or published elsewhere, e.g.:

* metadata.yaml > published on Charmhub
* documentation > published on (or linked to from) Charmhub
* detailed contribution guide > documentation or CONTRIBUTING.md

Use links instead.
-->

# elastic-charm

Charmhub package name: elastic-charm

<!-- Describe your charm in one or two sentences. -->
This charm deploys a charm on aws ec2 instance and assigns an elastic ip to its leader unit when provided as a config option.

## Other resources

<!-- If your charm is documented somewhere else other than Charmhub, provide a link separately. -->
The instances need to have instance roles with the following permissions:
- ec2:AssociateAddress
- ec2:DescribeAddresses
