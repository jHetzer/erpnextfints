# Archiv
Please checkout:

https://github.com/phamos-eu/kefiya

# ERPNextFinTS


[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4160a988f6f245b78917af5b6a717915)](https://app.codacy.com/manual/jHetzer/erpnextfints?utm_source=github.com&utm_medium=referral&utm_content=jHetzer/erpnextfints&utm_campaign=Badge_Grade_Dashboard)

FinTS Connector for ERPNext (Germany)

This app allows to import bank information from german banks into ERPNext.\
The app currently allows to import "receive" and "pay" payment entries.
The goal is to provide a stable and revision prove solution to sync (German) bank information with ERPNext.\
Best-case scenario: the functionality gets integrated into ERPNext as regional feature.

## Requirements
Python 3.4 <\
[Python FinTS](https://github.com/raphaelm/python-fints) (will be installed)

## Installation
```bash
    cd bench/project/folder
    bench get-app erpnextfints https://github.com/jHetzer/erpnextfints
    bench --site [sitename] install-app erpnextfints
    bench --site [sitename] enable-scheduler   
```
## Features
-  [x] FinTS Login
-  [x] Basic FinTS Import
-  [x] Save data as JSON and attach it
-  [x] Add import scheduler
-  [x] Support 'Pay' payment entry type
-  [x] Bank Account Wizard
-  [x] Interactive progress display
-  [x] Complete improving code style (PEP8 / ESLint)
-  [x] Payment / Sale auto assignment (unattended / wizard)

## ToDo

-  [ ] Unit tests / Cypress-tests
-  [ ] Improve import logs
-  [ ] Legal way to publish/get FinTS URL's
[https://www.hbci-zka.de/register/bedingungen_bankenliste.htm](https://www.hbci-zka.de/register/bedingungen_bankenliste.htm)
-  [ ] ...

### License

MIT License
