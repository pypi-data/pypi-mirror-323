# Gamesutil

> [!NOTE]
> Installation is supported only for the following: 
> - Windows
> - Linux

> [!NOTE]
> Development requires a fully configured [Dotfiles](https://github.com/florez-carlos/dotfiles) dev environment <br>

## Table of Contents

* [Installation](#installation)
  * [pip](#pip)
  * [manifest](#manifest) 
* [Usage](#usage)
  * [collect](#collect)
  * [inject](#inject) 
* [Development](#development)

## Installation
### Pip
```bash
python3 -m pip install gamesutil
```
### Manifest
Create the Save-Manifest.json <br ><br >
> [!NOTE]
> Any instances of {USER} are automatically replaced by the program with the current user name <br >

The Manifest contains: <br >
- backupSaveLocation: The folder where the cold saves are stored
- saves:
  - save:
    - displayName: The folder name that will be stored in the cold save location
    - location: The location of the hot save
```json
{
  "backupSaveLocation":"F:\\misc\\src\\gamesutil\\saves",
  "saves": [
    {
      "displayName":"My Game Save",
      "location": "C:\\Users\\{USER}\\AppData\\Local\\Game Company\\The Game"
    },
  ]
}
```
In the above sample:
- hot location: "C:\\Users\\{USER}\\AppData\\Local\\Game Company\\The Game" <br >
- cold location: F:\\misc\\src\\gamesutil\\saves\\My Game Save <br >
> [!NOTE]
> Hot location: should point to the directory where the game saves <br >
> Cold location: your backup

## Usage

### Collect

-sm The location of the Save Manifest<br >

```bash
gamesutil collect -sm C:\PATH\TO\SAVE-MANIFEST.JSON
```
This will copy all hot saves listed in the manifest into the cold save location

### Inject

-sm The location of the Save Manifest<br >

```bash
gamesutil inject -sm C:\PATH\TO\SAVE-MANIFEST.JSON
```

This will copy all the cold saves listed in the manifest into the hot save location

## Development

> [!NOTE]
> Development requires a fully configured [Dotfiles](https://github.com/florez-carlos/dotfiles) dev environment <br>

```bash
source init.sh
```

