# azerothcore-namek

This is my containerized AzerothCore 3.3.5a setup. It includes Playerbots, my module collection, my current server configuration, low-level bot mounts, learned-spell changes, and a 24-slot bag for every newly created character.

## Server setup

I run this with Docker Desktop on Windows.

1. Install Git and Docker Desktop.
2. Clone this repository.
3. Copy `.env.example` to `.env`, choose a database password, and keep `.env` private.
4. Run `powershell -ExecutionPolicy Bypass -File .\setup.ps1` from the repository folder.
5. Wait for the database import and worldserver build to finish.
6. Create an account from the worldserver console:

```text
account create USERNAME PASSWORD
account set gmlevel USERNAME 3 -1
```

The active configuration is under `runtime\etc` after setup. The server listens on ports `3724` and `8085` by default.

## Client patch

This setup uses `client\patch-4.mpq`. With WoW completely closed, copy that file into the client's `Data` folder:

```text
C:\path\to\World of Warcraft 3.3.5a\Data\patch-4.mpq
```

Then edit `Data\enUS\realmlist.wtf` and set it to the server's LAN IP:

```text
set realmlist 192.168.1.100
```

Delete the client's `Cache` folder if old client data is still showing, then launch the game.

Do not commit API keys, database dumps, account data, or the generated `.env` file.

