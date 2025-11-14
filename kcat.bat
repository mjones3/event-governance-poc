@echo off
REM kcat wrapper script for Windows
REM Usage: kcat.bat -L (to list topics)
REM        kcat.bat -C -t topic-name (to consume)

docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b redpanda:9092 %*
