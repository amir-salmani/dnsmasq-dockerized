FROM alpine:3.14

RUN apk add --no-cache stunnel

COPY stunnel.conf /etc/stunnel/stunnel.conf

CMD ["stunnel"]