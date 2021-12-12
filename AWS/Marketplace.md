## AWS Marketplace Usage

1. Ensure you have the Python package `xGT` installed:
   ```
   $ python3 -m pip install --user xgt
   ```

1. Launch an EC2 instance

1. Connect a python client:
   ```
   $ python3
   >>> import xgt
   >>> server = xgt.Connection(hostname='<public-ip-of-EC2-instance>', userid='xgt')
   ```

1. See [Trovares xGT documentation](docs.trovares.com) for help on writing python scripts, getting data ingested, and writing Cypher queries.

1. If needed, you may ssh connect to the EC2 instance:
 
   ```
   $ ssh -i <path/to/keys.pem> ec2-user@<public-ip-of-EC2-instance>
   ```
