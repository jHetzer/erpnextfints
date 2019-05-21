# Test Setup
ERPNextFinTS can be tested with the node.js module [Open-Fin-TS-JS-Client](https://www.npmjs.com/package/open-fin-ts-js-client)

## Installation
```
mkdir FinTS
cd FinTS
git clone https://github.com/jschyma/open_fints_js_client
cd open_fints_js_client/
npm install
node dev/Run_FinTSServer.js
```
`npm install` will display some errors. For tests these can be ignored.

```
HEY! USE SCREEN -bash-4.2# node dev/Run_FinTSServer.js
Listening at IP 127.0.0.1 on port 3000
FinTS server running at: 127.0.0.1:3000/cgi-bin/hbciservlet
```
![enter image description here](https://user-images.githubusercontent.com/28366175/58055628-a19bdf00-7b5e-11e9-9734-cb5a45c88e37.gif)

(Selection not recorded)

### Login Information:
```
from fints.client import FinTS3PinTanClient
f = FinTS3PinTanClient(
    "12345678",
    "test1",
    "1234",
    "http://localhost:3000/cgi-bin/hbciservlet"
)
f.get_sepa_accounts()
```
