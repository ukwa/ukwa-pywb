#!/bin/sh

cd /test-data

echo INFO - wait for CDX server to be ready...
sleep 10
echo INFO - send CDX data:
curl -s -XPOST --data-binary @acid.matkelly.com-20140716200357.cdx http://cdx:8080/tc
curl -s -XPOST --data-binary @acidtest-20180203004221.cdx http://cdx:8080/tc
curl -s -XPOST --data-binary @httpbin.cdx http://cdx:8080/tc

echo INFO - wait for HDFS to be ready...
sleep 10
echo INFO - uploading file:
curl -L -i -X PUT -T acid.matkelly.com-20140716200357.warc.gz "http://hadoop:50075/webhdfs/v1/acid.matkelly.com-20140716200357.warc.gz?&op=CREATE&createparent=false&overwrite=false&namenoderpcaddress=hadoop:9000&user.name=root"

curl -L -i -X PUT -T acidtest-20180203004221.warc.gz "http://hadoop:50075/webhdfs/v1/acidtest-20180203004221.warc.gz?&op=CREATE&createparent=false&overwrite=false&namenoderpcaddress=hadoop:9000&user.name=root"

curl -L -i -X PUT -T httpbin-20180218180614.warc.gz "http://hadoop:50075/webhdfs/v1/httpbin-20180218180614.warc.gz?&op=CREATE&createparent=false&overwrite=false&namenoderpcaddress=hadoop:9000&user.name=root"

echo INFO - all done.
