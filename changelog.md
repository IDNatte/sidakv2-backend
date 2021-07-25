## 1.1.2 (2021-07-25)

### API Change

### Config Structure Change

### Data Model Change

### Folder Structure Change

### Library upgrade

### Meta update
- [Meta update 1] Enhancing error status for endpoint ```/api/org/info/<org>```

----------------------------------------------------

## 1.1.2 (2021-07-23)

### API Change
- [API Change 1] Add G-Recaptcha endpoint verification

### Config Structure Change
- [Config Structure Change 1] Add ```RECAPTCHA_SECRET``` key to config @ ```flask.config.json```


### Data Model Change

### Folder Structure Change

### Library upgrade

### Meta update

----------------------------------------------------

## 1.1.2 (2021-07-20)

### API Change
- [API Change 1] Disabling organization change-able availability

### Config Structure Change
- [Config Structure Change 1] Restructuring ```common_config.py``` for ```HTTP_HEADER``` response


### Data Model Change

### Folder Structure Change

### Library upgrade

### Meta update

----------------------------------------------------

## 1.1.2 (2021-07-18)

### API Change
- [API Change 1] Add per-user info update (such as email update, Etc.)
- [API Change 2] Add organization info.
- [API Change] Result query is included with banner and organization detail @ endpoint ```/api/public/org```

### Config Structure Change
- [Config Structure Change 1] Add ```common_config.py``` for organizing http header (currently is static config only accepted meaning still need some works on multiple user-defined config key)


### Data Model Change
- [Data Model Change 1] Add ```Organization Detail``` and ```Organization Banner``` for organization data detail

### Folder Structure Change
- [Folder Structure Change 1] Add ```organization``` folder in ```public/upload``` folder for cleaner uploaded file folder structure.

### Library upgrade

### Meta update
- [Meta update 1] Add changelog.md to project starting update 1.1.2 (2021-07-18)

----------------------------------------------------