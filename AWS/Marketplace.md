## AWS Marketplace Usage

1. Ensure you have the Python package `xGT` installed in your environment:
   ```bash
   $ python3 -m pip install --user xgt
   ```
1. Launch an EC2 instanced, with port TCP port 4367 open for incoming connections.

1. Connect a python client:
   ```
   $ python3
   >>> import xgt
   >>> server = xgt.Connection(host='<public-ip-of-EC2-instance>', port=4367, userid='ec2-user')
   ```

1. See [Trovares xGT documentation](docs.trovares.com) for help on writing python scripts, getting data ingested, and writing Cypher queries.

1. If needed, you may ssh connect to the EC2 instance:
 
   ```bash
   $ ssh -i <path/to/keys.pem> ec2-user@<public-ip-of-EC2-instance>
   ```
