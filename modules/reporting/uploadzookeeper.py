import os
import json
from kazoo.client import KazooClient

from lib.cuckoo.common.exceptions import CuckooReportError
from lib.cuckoo.common.abstracts import Report

class UploadZookeeper(Report):
    """Saves analysis results in Zookeeper node when the proccess has been finished"""

    def run(self, results):
        try:
	    zk = KazooClient(hosts='127.0.0.1:2181', read_only=True)
	    zk.start()

	    local_path = str(self.analysis_path)
	    id = local_path.split('/')[-1]

	    hdfs_path = "/user/cuckoo/%s/dump.pcap" % id
            zk_path = "/rb_malware/pcapanalyzer/tasks/%s" % id
	    
	    # SHA256
  	    json_file = "%s/reports/report.json" % local_path
  	    with open(json_file) as data_file: 
	    	data = json.load(data_file)
	    sha = data["target"]["file"]["sha256"]

            zk_content = "%s %s" % (hdfs_path,str(sha))
	    
   	    print zk_path
            print zk_content
	    # Write in zookeeper
	    zk.create(zk_path,zk_content)
        except (UnicodeError, TypeError, IOError) as e:
            raise CuckooReportError("Failed to generate Zookeeper report: %s" % e)

