# Demo with thingsboard + postgres
### Requirements
- `docker`
- `docker-compose`
- [OPTIONAL] `openssl` (for generating self-signed certificate)

Before using the demo, prepare a data folder to be used by the demo edge-gateway:
> `mkdir -p data/edge-gateway`

Define the data path in `.env`:
> `echo"" >> .env && echo "TEG_DATA_PATH=$(realpath data/edge-gateway)" >> .env`

To initialize the demo upon the first use: 
> `docker compose -f docker-compose-thingsboard.yml run --rm -e INSTALL_TB=true -e LOAD_DEMO=true thingsboard`

To run the demo once it has been initialized: 
> `docker compose -f docker-compose-thingsboard.yml up`

Once the demo is up and running:
1. You can access the local thingsboard instance at http://localhost:8080/
2. You can sign in using the default credentials: user: "tenant@thingsboard.org" / pw: "tenant"
3. You can assign the following self-provisioning credentials to the "thermostat" device profile:
   a. Open the device profile "thermostat" 
      -> device provisioning -> edit 
      -> Provision strategy "Allow to create new devices"
   b. Provision device key: cl4ozm17lhwpafnz8jau
   c. Provision device secret: 7jemz65a0498pb5wzuk8
   d. Confirm with "save"
4. The demo edge-gateway will then automatically self-provision and start broadcasting simulated data.
5. You can then import `example_dashboard.json` in "Dashboards"-> "+" -> "Import" and set the dashboard's device alias 
   to the new device's id.

# Create Controller Config File
1. Go to Entities -> Devices and open the thermostat device created by self-provisioning.
2. Open Device details -> Navigate to the Attributes tab -> Select "Shared attributes" in Entitiy attributes scope
3. Create a 2 new attributes with the following details:
   - Key: `FILES`
   - Value (JSON):
   ```json
   {
      "controller_config":{
         "path":"$DATA_PATH/config.json",
         "encoding":"json",
         "write_version":1,
         "restart_controller_on_change":true
      }
   }
   ```

   - Key: `FILE_CONTENT_controller_config`
   - Value (JSON):
   ```json
   {
     "controllerType": "PID",
     "setPoint": 22.0,
     "kp": 1.0,
     "ki": 0.1,
     "kd": 0.01
   }
   ```
4. Wait for config to be created in ./data/edge-gateway/config.json 
5. Change content of the local config file
6. Go to the Dashboard "Example Sensor" and trigger Exit RPC
2. Open Device details -> Navigate to the Attributes tab -> Select "Client attributes" in Entitiy attributes scope
9. Verify that the local change was mirrored to the `FILE_READ_controller_config` attribute

# Additional notes
### [OPTIONAL] Generate self-signed certificate
If you want to generate 
In order to generate a new self-signed certificate, consider using/modifying the following command:
> openssl req -x509 -newkey rsa:4096 -keyout server_key.pem -out server_cert.pem -sha256 -days 9650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=nginx" -addext "subjectAltName=DNS:thingsboard,DNS:localhost"