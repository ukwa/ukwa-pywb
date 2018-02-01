UKWA API Integration Test
-------------------------

This set of services, described by a Docker Compose file, will simulate the APIs used for playback of web archive at the UK Web Archive. It consists of:

 - Our production version of OutbackCDX, from back when it was called tinycdxserver
 - A one-node Hadoop 'cluster'
 - An OpenWayback instance configured to use the above (for comparison)
 - A `populate` service, which waits a while, then pushes the CDX data to the cdx server and uplaods the WARC file to HDFS via WebHDFS.

If it all spins up correctly, these URLs should work:

 - http://localhost:50070/explorer.html#/ to observe the WARC file in HDFS
 - http://localhost:9090/tc?url=http%3A%2F%2Facid.matkelly.com%2F to see what's in the CDX server
 - http://localhost:8080/wayback/*/http://acid.matkelly.com/ to access the content via OpenWayback


