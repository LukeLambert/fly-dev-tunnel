FROM nginx:alpine
RUN apk add --no-cache python3
COPY generate.py /root
COPY 09-generate-config.sh /docker-entrypoint.d
