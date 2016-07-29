# Bot_irc

This is a dirty code for an IRC Bot controlable by the classical lib cmd in python (only for python2.7).

The bot can auto reply form simple and structured request

There is two version :
  - direct control : the cmd controlor running over the main program,
  - remote control : with socket you connect to the bot and his connect to the IRC server.

You need specefic lib to run bot :
  - ConfigParser and io (load stats)
  - croniter (get cron task for VDM and DTC)
  - dateutil.parser (check delta between to date)
  - An old version of Irclib and Ircbot (to run the bot)
