# Demo with thingsboard + postgres
### Requirements
- `docker`
- `docker-compose`
- [OPTIONAL] `openssl` (for generating self-signed certificate)


To initialize the demo upon the first use: 
> ` docker compose -f docker-compose-thingsboard.yml run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard`

To run the demo once it has been initialized: 
> `docker compose -f docker-compose-thingsboard.yml  up`

Once the demo is up and running:
1. You can access the local thingsboard instance at http://localhost:8080/
2. You can sign in using the default credentials: user: "tenant@thingsboard.org" / pw: "tenant"
3. You can assign the following self provisioning credentials to the "thermostat" device profile:
   a. Provision device key: cl4ozm17lhwpafnz8jau
   b. Provision device secret: 7jemz65a0498pb5wzuk8
   c. Confirm with "save"
4. The demo edge-gateway will then automatically self-provision and start broadcasting simulated data.
5. You can then import `example_dashboard.json` in "Dashboards"-> "+" -> "Import" and set the dashboard's device alias 
   to the new device's id.

# Generate self-signed certificate
In order to generate a new self-signed certificate, consider using/modifying the following command:
> openssl req -x509 -newkey rsa:4096 -keyout server_key.pem -out server_cert.pem -sha256 -days 9650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=nginx" -addext "subjectAltName=DNS:thingsboard,DNS:localhost"