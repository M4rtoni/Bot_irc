# Bot_irc

This is a dirty code for an IRC Bot controlable by the cmd lib in python (only 2.7).

The bot can auto reply form simple and structured request

There is two version :
  - direct control : the cmd controlor running over the main program,
  - remote control : with socket you connect to the bot and his connect to the IRC server.

Prefer local control !

You need specefic lib to run bot :
  - ConfigParser and io (load stats)
  - croniter (get cron task for VDM and DTC)
  - dateutil.parser (check delta between to date)
  - An old version of Irclib and Ircbot (run the bot)

The bot can get five diffrents agruments :
  - `name` (-n) use to change name of your bot (use has IRC Pseudo, default : `Bot`)
  - `serveur` (-s) use to change serveur (default : `irc.worldnet.net`)
  - `channel` (-c) use to change channel (default : `#Channel`, prefer to wrap with quotes `#` don't pass very well in args) 
  - `password` (-p) use to add a password (default no password save, note that his appear in plaintext)
  - `prompt` (--prompt) use to change default color in your prompt, there are 7 distinct tags (exclusif to `bot_local.py`) :
    - `%host%` in red
    - `%time%` in green
    - `%channel%` in blue
    - `%private%` in red
    - `%pseudo%` in green
    - `%pseudo_private%` in green
    - `%pseudo_other%` in yellow

Exemple of change tag to get host in yellow with no font : `--prompt "\033[0;34m%host%\033[0m"`
