from __future__ import print_function
import os
import aerospike
import yaml
import json

from lib.cuckoo.common.exceptions import CuckooReportError
from lib.cuckoo.common.abstracts import Report

class UploadAerospike(Report):
    """Saves analysis results in Aerospike"""

    def run(self, results):
        try:
            # Configure the client
            stream = open("/opt/rb/var/rb-sequence-oozie/conf/aerospike.yml", 'r')
            data = yaml.load(stream)
            config = {'hosts':[]}

            for server in data['general']['aerospike']['servers']:
              list = ()
              host = server.split(":")[0]
              port = int(server.split(":")[1])
              config['hosts'].append((host,port))
 
            # Create a client and connect it to the cluster
            try:
              client = aerospike.client(config).connect()
            except:
              import sys
              print("failed to connect to the cluster with", config['hosts'])
              sys.exit(1)
           
            # Extract SHA256 from report.json
            local_path = str(self.analysis_path)
            id = local_path.split('/')[-1]

            json_file = "%s/reports/report.json" % local_path
            with open(json_file) as data_file:
                data = json.load(data_file)
            sha = data["target"]["file"]["sha256"]
 
            # Records are addressable via a tuple of (namespace, set, key)
            key = ('malware', 'controlFiles', str(sha))

            try:
              # Write a record
              client.put(key, {
                'cuckoo_report': id, 
                'hash': str(sha)
                 })
            except Exception as e:
              import sys
              print("error: {0}".format(e), file=sys.stderr)

            # Read a record
            (key, metadata, record) = client.get(key)
            
            # Close the connection to the Aerospike cluster
            client.close()

        except (UnicodeError, TypeError, IOError) as e:
            raise CuckooReportError("Failed to generate Aerospike entry: %s" % e)

