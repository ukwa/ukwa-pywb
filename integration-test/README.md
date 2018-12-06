UKWA API Integration Test
-------------------------

This set of services, described by a Docker Compose file, will simulate the APIs used for playback of web archive at the UK Web Archive. It consists of:

 - Our production version of OutbackCDX, from back when it was called tinycdxserver
 - A one-node Hadoop 'cluster'
 - An OpenWayback instance configured to use the above (for comparison)
 - A `populate` service, which waits a while, then pushes the CDX data to the cdx server and uplaods the WARC file to HDFS via WebHDFS.

If it all spins up correctly, these URLs should work:

 - http://localhost:50070/explorer.html#/ to observe the WARC file in HDFS
 - http://localhost:9090/tc?q=type:urlquery+url:http%3A%2F%2Facid.matkelly.com%2F to see what's in the CDX server
 - http://localhost:8080/wayback/*/http://acid.matkelly.com/ to access the content via OpenWayback
 - http://localhost:8081/qa-access/*/http://acid.matkelly.com/ to access content with no exclusions in pywb

### Pywb Test Collections

The pywb config defines three collections, using the same data. They are also listed by visiting http://localhost:8081/
For example, the sample page can be accessed in the 3 collections as follows:

* http://localhost:8081/qa-acccess/*/http://acid.matkelly.com/ provides access with no exclusions or locks, designed to simulate QA system access
* http://localhost:8081/open-access/*/http://acid.matkelly.com/ provides access with an allow list and block list, and no locks, designed to simulate open accces
* http://localhost:8081/reading-room/*/http://acid.matkelly.com/ provides access with single-concurrent lock use and a block list, designed to simulate reading room setup


The archived version of the 'acid test' page looks pretty poor in OWB, although it renders okay in proxy mode (use `localhost:8090` as your proxy for that to work).


### Automated Feature Testings ###

Some automated tests are set up to verify specific features. Once 

    docker-compose run populate

has run successfully, you should be able to run the tests using


    docker-compose run test


