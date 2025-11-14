FROM provectuslabs/kafka-ui:v0.7.2

# Import corporate CA certificate into Java truststore
USER root
COPY ca.arc-one.crt /tmp/ca.arc-one.crt
RUN keytool -import -trustcacerts -noprompt -alias corporate-ca \
    -file /tmp/ca.arc-one.crt \
    -keystore /usr/lib/jvm/zulu17-ca/lib/security/cacerts \
    -storepass changeit

USER kafkaui
