# Bot_irc

This is a dirty code of an IRC Bot command by cmd lib in python (prefer 2.7).

The bot can auto reply form simple and structured request

There is two version :
  -  direct control : the cmd controlor running over the main program, 
  -  remote control (obsolete and depreciated) : with socket you connect to the bot and his connect to the IRC serve . 

Prefer local control !

You need specefic lib to run bot :
  - cmd.Cmd to get a simple and modular CLI
  - threading.Thread to run bot and cmd
  - ConfigParser and io (load stats)
  - croniter (get cron task for VDM and DTC)
  - dateutil.parser (check delta between to date)
  - An old version of irclib and ircbot (run the bot), some feature have been change !

The bot can get five diffrents agruments :
  - `name` (-n) use to change name of your bot (use has IRC Pseudo, default : `Bot`)
  - `serveur` (-s) use to change serveur (default : `irc.worldnet.net`)
  - `channel` (-c) use to change channel (default : `#Channel`, prefer to wrap with quotes `#` don't pass very well in CLI args) 
  - `password` (-p) use to add a password (default no password save, note that his appear in plaintext)
  - `ssl` (--ssl) use a `bool` to active or not ssl beetwen bot and server
  - `port` (--port) use a given port to set port use to connect to the server
  - `prompt` (--prompt) use to change default color in your prompt, there are 7 distinct tags (exclusif to `bot_local.py`) :
    - `%host%` in red
    - `%time%` in green
    - `%channel%` in blue
    - `%private%` in red
    - `%pseudo%` in green
    - `%pseudo_private%` in green
    - `%pseudo_other%` in yellow

Exemple of change tag to get host in yellow with no font : `--prompt "\033[0;34m%host%\033[0m"`

You can change manualy default setting !

Add your own functions for more fun !

## Install

Clone the project:
```bash
git clone https://github.com/M4rtoni/Bot_irc.git
cd Bot_irc
```
Install the project:
```bash
pip install -r requirements.txt
sudo python setup.py install
```

## Run

Let's go !
```bash
python bot_local.py
```

And may be more incomming
