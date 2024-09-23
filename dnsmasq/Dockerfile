FROM ubuntu:22.04

RUN apt-get update && apt-get install -y dnsmasq && rm -rf /var/lib/apt/lists/*

EXPOSE 53 53/udp

CMD ["dnsmasq", "-k"]