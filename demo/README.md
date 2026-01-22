# Demo with thingsboard + postgres

init: ` docker compose -f docker-compose-thingsboard.yml run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard`

run: `docker compose -f docker-compose-thingsboard.yml  up`

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout server_key.pem -out server_cert.pem -sha256 -days 9650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=nginx" -addext "subjectAltName=DNS:thingsboard,DNS:localhost"