#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#
# File Name         : bot_local.py
# Created By        : Florian MAUFRAIS
# Contact           : florian.maufrais@gmail.com
# Creation Date     : december  22th, 2017
# Version           : 1.2.0
# Last Change       : May  22th, 2017 at 15:50
# Last Changed By   : Florian MAUFRAIS
# Purpose           : This programm use an IRC bot_local and cmd line interface
#                     If you find bugs or want more information please contact !
#
################################################################################

__version__ = '1.2.0'
__all__ = ['Robot', 'getVDM', 'getDTC', 'MyCmd', '__version__']

################################################################################

import argparse, sys, re

bot = {
    'name': 'MyBot',
    'channel': '#Martoni',
    'server': 'irc.worldnet.net',
    'password': None,
    'port': 7000,
    'ssl': True,
    'function': 1
}

if __name__ == "__main__":
    def check_port(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
        elif ivalue > 65536:
            raise argparse.ArgumentTypeError("%s is invalid limit 65536" % value)
        return ivalue
    parser = argparse.ArgumentParser(description='IRC Client including some goods !',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n', dest='name', action='store',
        default=bot['name'], help="Use to change default bot's Name")
    parser.add_argument('-p', dest='password', action='store',
        default=bot['password'], help="Use a Password, not by default")
    parser.add_argument('-c', dest='channel', action='store',
        default=bot['channel'], help="Use to change default bot's Channel ")
    parser.add_argument('-s', dest='server', action='store',
        default=bot['server'], help="Use to change default bot's Server")
    parser.add_argument('--ssl', dest='ssl', action='store', type=bool,
        default=bot['ssl'], help="Use to activate or not ssl")
    parser.add_argument('--port', dest='port', action='store', type=check_port,
        default=bot['port'], help="Int require to change server port")
    parser.add_argument('--prompt', dest='prompt', action='store',
        default=None, help='''Change color and format of tags in prompt
    example : "%%host%%:\\033[0;34m"''')
    
    args = parser.parse_args(sys.argv[1:])
    PROMPT = {'%default%': '\033[0m',
            '%private%': '\033[1;31m',
            '%host%': '\033[0;31m',
            '%pseudo%': '\033[0;32m',
            '%channel%': '\033[1;34m',
            '%pseudo_private%': '\033[0;32m',
            '%time%': '\033[3;36m',
            '%pseudo_other%': '\033[1;35m',
            '%welcome%': '\033[1;32m',
            '%alert%': '\033[1;33m'
        }
    if sys.platform == 'win32':
        PROMPT = {key: '' for key in PROMPT}
        if args.prompt:
            print 'Warring : Prompt has been shutdown for compatibility purpose !'
    else:
        if args.prompt:
            add = re.findall('(%(?:default|host|time|channel|private|pseudo(?:_private|_other|))%):'+\
                '(\\033[[](?:(?:[0-9]|2[1-3]|[3-49][0-7])?;)*(?:[0-9]|2[1-3]|[3-49][0-7])?m)',\
                args.prompt)
            if add:
                for item in add:
                    PROMPT.update({item[1]:item[0]})
            else:
                print '\033[0;33mError during PROMPT processing : InvalidFormat !\033[0m'
                print '\t'+args.prompt
                sys.exit(0)
    
    args = args.__dict__
    args['function_access'] = {}
    args.pop('prompt')

################################################################################

import io, requests, unicodedata, time, string, irclib
from pyparsing import Literal, Word, nums, Combine, Optional, delimitedList, oneOf, alphas, Suppress
from datetime import datetime, timedelta
from ConfigParser import ConfigParser
from ircbot import SingleServerIRCBot
from HTMLParser import HTMLParser
from traceback import extract_tb
from croniter import croniter
from threading import Thread
from dateutil import parser
from random import randint
from cmd import Cmd

################################################################################

def delai(date):
    _min = min(datetime.now().isoformat(), date)
    _max = max(datetime.now().isoformat(), date)
    delta = parser.parse(_max) - parser.parse(_min)
    day = delta.days
    day = (['%s day%s' % (day, ('','s')[day > 1])],[])[day == 0]
    hour = (delta.seconds)/3600
    hour = (['%s hour%s' % (hour, ('','s')[hour > 1])],[])[hour == 0]
    minute = (delta.seconds/60)%60
    minute = (['%s minute%s' % (minute, ('','s')[minute > 1])],[])[minute == 0]
    second = delta.seconds%60
    second = (['%s second%s' % (second, ('','s')[second > 1])],[])[second == 0]
    return ', '.join(day+hour+minute+second)

def getVDM(nb):
    assert type(nb) is int, 'nb must be an int !'
    assert nb > 0, 'nb must be positive !'
    try:
        page=requests.get('http://www.viedemerde.fr/aleatoire', timeout = 1)
    except:
        return []
    if page.ok:
        regex = '<article class="art-panel col-xs-12">(?:.|\n)+?</article>'
        vdm = re.findall(regex, page.content)
        h = HTMLParser()
        result = []
        res = []
        for item in vdm:
            regex = '<div [^>]+>\n<p [^>]+>\n<a [^>]+>\n(?:<span class="icon-piment"></span>&nbsp;\n)?((?:.|\n)+?)\n</a>'
            _vdm = re.findall(regex, item)
            if len(_vdm) == 1:
                result.append(h.unescape(unicodedata.normalize('NFKD', _vdm[0].decode('utf-8'))).encode('utf-8'))
        while result and nb:
            res += [result.pop(randint(0,len(result)-1))]
            nb -= 1
        return res
    else:
        return []

def getDTC(nb):
    assert type(nb) is int, 'nb must be an int !'
    assert type(nb) is int, 'nb must be positive !'
    try:
        page=requests.get('http://danstonchat.com/random.html', timeout = 1)
    except:
        return []
    if page.ok:
        regex = '<div class="item item[0-9]+"><(?:div|p) class="item-content"><a href="[^"]+">((?:.|\n)*?)</a></(?:div|p)><(?:div|p) class="item-meta">(?:.|\n)*?</(?:div|p)></div>'
        dtc = re.findall(regex, page.content)
        h = HTMLParser()
        result = []
        res = []
        for item in dtc:
            result.append(h.unescape(re.sub('<[^>]+>','', unicodedata.normalize('NFKD', item.replace('<br />','\n').decode('utf-8')))).encode('utf-8'))
        while result and nb:
            res += [result.pop(randint(0,len(result)-1))]
            nb -= 1
        return res
    else:
        return []

if __name__ == "__main__":
    ret = []
    def check_get(output, ret):
        i = 0
        while not ret:
            sys.stdout.write('\r%s : %s' % (output, '\\|/-'[i%4]))
            time.sleep(0.3)
            i += 1
    Thread(target = check_get, kwargs = {'output': 'getVDM check', 'ret': ret}).start()
    ret += getVDM(1)
    sys.stdout.write('\rgetVDM check : ')
    if ret:
        print '{%welcome%}OK{%default%}'.format(**PROMPT)
    else:
        ret += ['stop !']
        getVDM = False
        args['function_access']['do_vdm'] = -1
        args['function_access']['do_cronvdm'] = -1
        print '{%alert%}NOK{%default%}'.format(**PROMPT)
    time.sleep(0.5)
    ret = []
    Thread(target = check_get, kwargs = {'output': 'getDTC check', 'ret': ret}).start()
    ret += getDTC(1)
    sys.stdout.write('\rgetDTC check : ')
    if ret:
        print '{%welcome%}OK{%default%}'.format(**PROMPT)
    else:
        ret += ['stop !']
        getDTC = False
        args['function_access']['do_dtc'] = -1
        args['function_access']['do_crondtc'] = -1
        print '{%alert%}NOK{%default%}'.format(**PROMPT)
    time.sleep(0.5)
    del ret

################################################################################

class Stat():
    def __init__(self, name, words, letters, messages, status, urls):
        self.name = name
        self.words = words
        self.letters = letters
        self.messages = messages
        self.status = status
        self.urls = urls
    def update(self, message):
        _url = re.compile('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.messages += 1
        self.words += len(message.split(' '))
        self.letters += len(message) - message.count(' ')
        urls = _url.findall(message)
        self.urls = (self.urls+[{'url' : url, 'date' : datetime.now().isoformat()[:-7]} for url in urls])[-10:]
    def __str__(self):
        return ', '.join(['%s %s' % (getattr(self, value), value) for value in ['words', 'messages', 'letters']])
    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        if key in ['words', 'messages', 'letters', 'status']:
            return getattr(self, key)
        else:
            raise 
    def get(self, *args):
        if len(args) == 0:
            raise TypeError,\
                'get expected at least 1 arguments, got 0'

class cron(Thread, croniter):
    def __init__(self, target, args, expr_format):
        if croniter.is_valid(expr_format):
            Thread.__init__(self)
            self.__target = target
            self.__args = args
            croniter.__init__(self, expr_format)
            self.get_next()
            self.__forceStop = False
            self.__initialized = True
        else:
            self = None
    def start(self):
        if self.__forceStop:
            self._Thread__stopped = False
            self._Thread__started.clear()
        self.__forceStop = False
        Thread.start(self)
    def run(self):
        try:
            if self.__target:
                _next = datetime.fromtimestamp(self.get_current())
                while _next < datetime.now():
                    _next = datetime.fromtimestamp(self.get_next())
                while not self.__forceStop:
                    if  _next < datetime.now():
                        self.__target(*self.__args)
                        _next = datetime.fromtimestamp(self.get_next())
                    time.sleep(0.1)
        except:
            pass
        finally:
            self.__forceStop = True
    def stop(self):
        if self._Thread__started.is_set():
            self.__forceStop = True

################################################################################

class Robot(SingleServerIRCBot):
    __connected = False
    __awake = False
    _prompt = {
        '__prompt__': ('\r<\033[1;32mYou\033[0m> ','\r<You> ')[sys.platform == 'win32'], 
        'host' : '\r<{%host%}Host{%default%},{%time%}{date}{%default%}> ',
        'pubmsg' : '\r<{%pseudo%}{author}{%default%},{%channel%}{channel}{%default%},{%time%}{date}{%default%}> ',
        'privmsg' : '\r<{%pseudo_private%}{author}{%default%},{%private%}private{%default%},{%time%}{date}{%default%}> ',
        'channel' : '\r<{%channel%}{channel}{%default%},{%time%}{date}{%default%}> '
    }
    _cronVDM = {}
    _cronDTC = {}
    _identchars = string.ascii_letters + string.digits + '_'
    _lastkick = None
    _server = None
    def __init__(self,
        name = bot['name'],
        server = bot['server'],
        ssl = bot['ssl'],
        password = bot['password'],
        port = bot['port'],
        channel = bot['channel'],
        **kwargs):
        SingleServerIRCBot.__init__(self, [(server, port)], name, "IRCBot available on : https://git.io/vHtZ6",password=password, ssl=ssl)
        self._name = name
        self._channel = channel
        self._server = server
        self._port = port
        self._ssl = ssl
        self._stdout = kwargs.pop('stdout', sys.stdout)
        self._stat = kwargs.pop('stat', {})
        self._prompt.update(kwargs.pop('prompt', {}))
        self._function = kwargs.pop('function', bot.get('function', True))
        function = kwargs.pop('function_access', {})
        self.__function__ = {
            key[3:]: function[key[3:]] 
            if key[3:] in function and type(function[key[3:]]) is int
            else bot.get('__function__', 0)
            for key in dir(self)
            if key.startswith('do_')
        }
        self.__function_intervall = kwargs.pop('function_intervall', 5)
        self.__next_function = datetime.now()
    def start(self):
        self.__awake = datetime.now().isoformat()
        self.__next_function = datetime.now()
        SingleServerIRCBot.start(self)
    def on_welcome(self, serv, ev):
        self._server = serv
        serv.join(self._channel)
        self.__prompt('host', '{%welcome%}Bot is now connect to {server} !{%default%}\n', server = self._server)
    def on_join(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        channel = ev.target()
        if author == self._name:
            self.__connected = True
            self.__prompt('host', '{%welcome%}Join {channel} on {server} !{%default%}',server = self._server, channel = channel)
            info = self.channels.get(channel, None)
            if not info is None:
                if len(info.users()) <= 1:
                    users = ['%s%s' % (self.__user_mode(aut),aut) for aut in info.users()]
                    self.__prompt('host', '{users} are on line !', users = ', '.join(users))
                else:
                    self.__prompt('host', 'You have no friend !')
        else:
            self.__prompt('host', '{%welcome%}{mode}{author} enter !{%default%}', mode = self.__user_mode(author), author = author)
            if not author in self._stat.keys():
                self._stat.update({author:Stat(irclib.nm_to_u(ev.source()), 0, 0, 0, 0, [])})
    def on_pubmsg(self, serv, ev):
        message = ev.arguments()[0]
        author = irclib.nm_to_n(ev.source())
        channel = ev.target()
        self.__prompt('pubmsg', self.__safe_prompt(message), author = self.__user_mode(author)+author, channel = channel)
        if author in self._stat:
            self._stat[author].update(message)
        else:
            self._stat.update({author:Stat(irclib.nm_to_u(ev.source()), 0, 0, 0, 0, [])})
            self._stat[author].update(message)
    def on_privmsg(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        self.__prompt('privmsg', self.__safe_prompt(message), author = author)
        self.default(author, author, serv, message)
        if self._stat[author].status == -1:
            self.default_admin(author, author, serv, message)
    def on_kick(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        target = ev.arguments()[0]
        reason = ev.arguments()[1]
        self._lastkick = {'target': target,'reason': reason,'date': datetime.now().isoformat()[:8],'author': author}
        self.__prompt('channel', '{%alert%}{author} kick {target} ! {reason}{%default%}', channel = channel, author = self.__user_mode(author)+author,target = target, reason = ('('+reason+')', '')[not reason])
        if target == self._name:
            serv.join(channel)
            self.__prompt('host', '{%welcome%}Bot was kick from {channel} and reconnect !{%default%}', channel = channel)
    def on_part(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        reason = ev.arguments()
        self.__prompt('channel', '{%alert%}{author} has left ! {reason}{%default%}', channel = channel, author = self.__user_mode(author)+author, reason = ('('+' '.join(reason)+')', '')[not reason])
    def on_quit(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        reason = ev.arguments()
        self.__prompt('channel', '{%alert%}{author} quit ! {reason}{%default%}', channel = channel, author = self.__user_mode(author)+author, reason = ('('+' '.join(reason)+')', '')[not reason])
    def on_nick(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        new_author = ev.target()
        self._stat[new_author] = self._stat.pop(author)
        self.__prompt('channel', '{%alert%}{author} has rename in {new_author}{%default%}', channel = self._channel, author = self.__user_mode(author)+author, new_author = new_author)
    def on_action(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        self.__prompt('channel', '{%welcome%}*{author} {action}*{%default%}', channel = channel, author = self.__user_mode(author)+author, action = self.__safe_prompt(message))
        if author in self._stat:
            self._stat[author].update(message)
        else:
            self._stat.update({author:Stat(irclib.nm_to_u(ev.source()), 0, 0, 0, 0, [])})
            self._stat[author].update(message)
    def on_mode(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        topic = ev.arguments()
        self.__prompt('channel', '{%welcome%}{author} change mode : {topic}', channel = channel, author = self.__user_mode(author)+author, topic = topic)
    def on_currenttopic(self, serv, ev):
        channel = ev.arguments()[0]
        topic = ev.arguments()[1]
        self.__prompt('channel', '{%welcome%}Current topic on {channel} : {topic}', channel = channel, topic = topic)
    def on_topic(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        topic = ev.arguments()[0]
        self.__prompt('channel', '\033[1;32mNew topic by {author} : {topic}', channel = channel, author = author, topic = topic)
    def __user_mode(self, user, channel = None):
        if channel is None:
            channel = self._channel
        try:
            info = self.channels[channel]
            return ((((('','+')[info.is_voiced(user)],'%')[info.is_halfop(user)],'@')[info.is_oper(user)],\
                '&')[info.is_admin(user)],'~')[info.is_owner(user)]
        except KeyError:
            return ''
        except Exception, e:
            self.__prompt('host', '{%alert%}{error}{%default%}', error = e.message)
    def __prompt(self, src, message, **kwargs):
        import readline
        origline = readline.get_line_buffer()
        if not message.endswith('\n'):
            message = '%s\n' % message
        args = {}
        args.update(PROMPT)
        args.update(kwargs)
        args.update({'date': datetime.now().time().isoformat()[:8]})
        self._stdout.write('\r'+' '*len(UncolorString(self._prompt['__prompt__'] + origline)))
        self._stdout.write((self._prompt[src]+message).format(**args))
        self._stdout.write(self._prompt['__prompt__'] + origline)
    def __safe_prompt(self, message):
        for mess in re.findall('{[^}]+?(?::[^}]*?)?}', message):
            message = message.replace(mess, '{%s}' % mess)
        return message
    def _parse_message(self, message):
        """Function based on cmd.Cmd.parseline()"""
        line = message.strip()
        if not line:
            return None, None, line
        elif line[0] == '!':
            if not hasattr(self, 'do_'+line[0]):
                return None, None, line
        else:
            return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self._identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line
    def _parse_priv_message(self, message):
        """Function based on cmd.Cmd.parseline()"""
        line = message.strip()
        if not line:
            return None, None, line
        elif not line[:6] in ['!%s' % l for l in ['admin']]:
            return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self._identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line
    def default_admin(self, author, channel, serv, message):
        cmd, arg, line = self._parse_priv_message(message)
        if cmd:
            if cmd == '!admin':
                line = arg.split()
                if len(line) == 2:
                    if line[0] == 'stop' and hasattr(self, 'do_'+line[1]):
                        self.__function__[line[1]] = -1
                        self.__prompt('host', '{%alert%}{function}{%default%} function has been stop', function = line[1])
                        for admin in [admin for admin in self._stat if self._stat[admin].status == -1]:
                            serv.privmsg(admin, '{function} function has been stop'.format(function = line[1]))
                        if line[1] == 'cronVDM':
                            for channel in self.channels:
                                if channel in self._cronVDM:
                                    self._cronVDM[channel].stop()
                        if line[1] == 'cronDTC':
                            for channel in self.channels:
                                if channel in self._cronDTC:
                                    self._cronDTC[channel].stop()
                    elif line[0] == 'reset':
                        if hasattr(self, 'do_'+line[1]):
                            self.__function__[line[1]] = 0
                            self.__prompt('host', '{%alert%}{function}{%default%} function status has been reset', function = line[1])
                            serv.privmsg(author, '{function} function status has been reset'.format(function = line[1]))
                        elif line[1] in self.channels[self._channel].users():
                            self._stat[line[1]].status = 0
                            self.__prompt('host', '{%alert%}{target}{%default%} function status has been reset', target = line[1])
                            serv.privmsg(author, '{target} function status has been reset'.format(target = line[1]))
                    elif line[0] == 'get':
                        if line[1] in self.channels[self._channel].users():
                            self.__prompt('host', '{%alert%}{target}{%default%}{status}', target = line[1], status = self._stat[line[1]])
                            serv.privmsg(author, '{target} function status is {status}'.format(target = line[1], status = self._stat[line[1]]))
                        elif hasattr(self, 'do_'+line[1]):
                            self.__prompt('host', '{%alert%}{function}{%default%}{status}', function = line[1], status = self.__function__[line[1]])
                            serv.privmsg(author, '{function} function status is {status}'.format(function = line[1], status = self.__function__[line[1]]))
                    else:
                        return False
                elif len(line) == 3:
                    if line[0] == 'set':
                        if line[1] in self.channels[self._channel].users() and line[2].isdigit():
                            self._stat[line[1]].status = int(line[2])
                            self.__prompt('host', '{%alert%}{target}{%default%} function status is {%welcome%}{status}{%default%} now !', target = line[1], status = self._stat[line[1]])
                            serv.privmsg(author, '{target} function status is {status} now !'.format(target = line[1], status = self._stat[line[1]]))
                        elif hasattr(self, 'do_'+line[1]) and line[2].isdigit():
                            self.__function__[line[1]] = int(line[2])
                            self.__prompt('host', '{%alert%}{function}{%default%} function status is {%welcome%}{status}{%default%} now !', function = line[1], status = self.__function__[line[1]])
                            serv.privmsg(author, '{function} function status is {status} now !'.format(function = line[1], status = self.__function__[line[1]]))
                        else:
                            return False
                    elif line[0] == 'add':
                        if line[1] in self.channels[self._channel].users() and line[2].isdigit():
                            self._stat[line[1]].status += int(line[2])
                            self.__prompt('host', '{%alert%}{target}{%default%} function status is {%welcome%}{status}{%default%} now !', target = line[1], status = self._stat[line[1]])
                            serv.privmsg(author, '{target} function status is {status} now !'.format(target = line[1], status = self._stat[line[1]]))
                        elif hasattr(self, 'do_'+line[1]) and line[2].isdigit():
                            self.__function__[line[1]] += int(line[2])
                            self.__prompt('host', '{%alert%}{function}{%default%} function status is {%welcome%}{status}{%default%} now !', function = line[1], status = self.__function__[line[1]])
                            serv.privmsg(author, '{function} function status is {status} now !'.format(function = line[1], status = self.__function__[line[1]]))
                        else:
                            return False
                    else:
                        return False
            return True
    def default(self, author, channel, serv, message):
        if author == self._name:
            return
        cmd, arg, line = self._parse_message(message)
        if not line or cmd is None:
            return
        else:
            try:
                if self.__function__[cmd] == -1:
                    return
                elif self._stat[author].status == -1:
                    self.__next_function = datetime.now() + timedelta(0, self.__function_intervall)
                    func = getattr(self, 'do_'+cmd)
                elif self.__next_function > datetime.now():
                    return
                elif self.__function__[cmd] <= self._stat[author].status or self._function:
                    self.__next_function = datetime.now() + timedelta(0, self.__function_intervall)
                    func = getattr(self, 'do_'+cmd)
                else:
                    return
            except AttributeError:
                return
            return func(author, channel, serv, arg)
    def do_help(self, author, channel, serv, message):
        """Print help for documented command"""
        if message:
            try:
                doc = getattr(self, 'do_%s' % message).__doc__
                if doc:
                    self.stdout.write("%s\n" % str(doc))
                    return True
            except AttributeError:
                pass
        else:
            functions = [
                function for function in dir(self.__class__) 
                if function.statswith('do_')
            ]
            for function in functions:
                if self._stat[author].status == -1 or \
                    self.__function__[function] <= self._stat[author].status:
                    doc = getattr(self, function).__doc__
                    if doc:
                        for _doc in doc.split('\n'):
                            serv.privmsg(author, _doc)
                            time.sleep(0.1)
        serv.privmsg(author, 'There is no help for now')
        return True
    def do_lastkick(self, author, channel, serv, message):
        """Print _lastkick saved, it could have no one"""
        if self._lastkick:
            target = self._lastkick['target']
            author = self._lastkick['author']
            reason = self._lastkick['reason']
            delai = delai(self._lastkick['date'])
            serv.privmsg(channel, 'LastKick : {target} was kick by {author}, {delai} ago', target = target, author = author, reason = reason, delai = delai)
            self.__prompt('host', '{%welcome%}LastKick : {target} was kick by {author}, {delai} ago{%default%}', target = target, author = author, reason = reason, delai = delai)
        else:
            serv.privmsg(channel, 'LastKick : No Kick saved !')
            self.__prompt('host', '{%alert%}LastKick : No Kick saved !{%default%}')
        return True
    def do_vdm(self, author, channel, serv, message):
        """Print 1 to N random VDM
        N : must be a digit (positive integer), else N is 1"""
        if getDTC:
            number = 1
            if message.isdigit():
                number = int(message)
            VDMs = getVDM(number)
            for VDM in VDMs:
                serv.privmsg(channel, VDM)
                self.__prompt('host', VDM)
                time.sleep(0.3)
            return True
    def do_dtc(self, author, channel, serv, message):
        """Print 1 to N random DTC
        N : must be a digit (positive integer), else N is 1"""
        if getDTC:
            number = 1
            if message.isdigit():
                number = int(message)
            DTCs = getDTC(number)
            for DTC in DTCs:
                serv.privmsg(channel, DTC)
                self.__prompt('host', DTC)
                time.sleep(0.3)
            return True
    def do_awake(self, author, channel, serv, message):
        """Print time past from bot awake"""
        if self.__awake:
            serv.privmsg(channel, 'Bot awake {} ago !'.format(delai(self.__awake)))
            self.__prompt('host', 'Bot awake {delai} ago !', delai = delai(self.__awake))
    def do_function(self, author, channel, serv, message):
        """Function status modification with a status' argument
        'on' : allowed function for everyone 
        'off' : active limitation for function usage
        No status : Print function status"""
        if message in ['off', 'on', '']:
            status = message == 'on'
        else:
            return False
        if not message:
            serv.privmsg(channel, 'Function are {}'.format(('off', 'on')[self._function]))
            self.__prompt('host', 'Function are {function} !', function = ('off', 'on')[self._function])
        else:
            if status == self._function:
                serv.privmsg(channel, 'Function are already {} !'.format(('off', 'on')[self._function]))
                self.__prompt('host', 'Function are already {function} !', function = ('off', 'on')[self._function])
            else:
                serv.privmsg(channel, 'Function are now {} !'.format(('off', 'on')[status]))
                if author == channel:
                    serv.privmsg(self._channel, 'Function are now {} !'.format(('off', 'on')[status]))
                self.__prompt('host', 'Function are now {function} !', function = ('off', 'on')[status])
                self._function = status
        return True
    def do_stat(self, author, channel, serv, message):
        """"""
        pseudoList = [pseudo for pseudo in message.split() if pseudo in self._stat]
        if not pseudoList:
            pseudoList += [author]
        for pseudo in pseudoList:
            if pseudo in self._stat:
                serv.privmsg(channel, '{pseudo} send {stat}'.format(pseudo = pseudo, stat = self._stat[pseudo]))
                self.__prompt('host', '{pseudo} send {stat}\n', pseudo = pseudo, stat = self._stat[pseudo])
                time.sleep(0.3)
        return True
    def do_cronvdm(self, author, channel, serv, message):
        """Cron feature for VDM printing, max 1 minute per loop with no end
        start : lanch cron for VDM, if is not
        stop : cancel cron for VDM, if is start
        next : print time for next cron VDM loop
        update <expression> : change cron VDM frequency, if <expression> is valid"""
        items = message.split()
        if channel in self._cronVDM:
            if message == 'start':
                if self._cronVDM[channel].is_alive():
                    serv.privmsg(channel, 'cronVDM : already start !')
                    self.__prompt('host', '{%alert%}cronVDM : already start !{%default%}')
                else:
                    serv.privmsg(channel, 'cronVDM : already start !')
                    self.__prompt('host', '{%alert%}cronVDM : already start !{%default%}')
            elif message == 'stop':
                if self._cronVDM[channel].is_alive():
                    serv.privmsg(channel, 'cronVDM : stopped !')
                    self.__prompt('host', '{%alert%}cronVDM : stopped !{%default%}')
                else:
                    serv.privmsg(channel, 'cronVDM : already stopped !')
                    self.__prompt('host', '{%alert%}cronVDM : already stopped !{%default%}')
            elif items[0] == 'update':
                items.pop(0)
                if len(items) > 5:
                    serv.privmsg(channel, 'cronVDM : update refuse ! (possible abuse frequency)')
                    self.__prompt('host', '{%alert%}cronVDM : update refuse ! (possible abuse frequency){%default%}')
                elif croniter.is_valid(' '.join(items[:5])):
                    self._cronVDM[channel].expanded, self._cronVDM[channel].nth_weekday_of_month = croniter.expand(' '.join(items[:5]))
                else:
                    serv.privmsg(channel, 'cronVDM : update refuse !')
                    self.__prompt('host', '{%alert%}cronVDM : update refuse !{%default%}')
            elif message == 'next':
                if self._cronVDM[channel].is_alive():
                    _next = delai(datetime.fromtimestamp(self._cronVDM[channel].get_current()))
                    serv.privmsg(channel, 'cronVDM : next in {next} !'.format(next = _next))
                    self.__prompt('host', '{%alert%}cronVDM : next in {next} !{%default%}', next = _next)
            else:
                return False
        else:
            if not message:
                self._cronVDM[channel] = cron(target = self.do_vdm, expr_format = '0 * * * *', args = (self._name, channel, serv, ''))
            elif croniter.is_valid(' '.join(items[:5])):
                self._cronVDM[channel] = cron(target = self.do_vdm, expr_format = ' '.join(items[:5]), args = (self._name, channel, serv, ''))
            else:
                return False
            self._cronVDM[channel].start()
            serv.privmsg(channel, 'cronVDM : start !')
            self.__prompt('host', '{%alert%}cronVDM : start !{%default%}')
        return True
    def do_crondtc(self, author, channel, serv, message):
        """Cron feature for DTC printing, max 1 minute per loop with no end
        start : lanch cron for DTC, if is not
        stop : cancel cron for DTC, if is start
        next : print time for next cron DTC loop
        update <expression> : change cron DTC frequency, if <expression> is valid"""
        items = message.split()
        if channel in self._cronDTC:
            if message == 'start':
                if self._cronDTC[channel].is_alive():
                    serv.privmsg(channel, 'cronDTC : already start !')
                    self.__prompt('host', '{%alert%}cronDTC : already start !{%default%}')
                else:
                    serv.privmsg(channel, 'cronDTC : start !')
                    self.__prompt('host', '{%alert%}cronDTC : start !{%default%}')
            elif message == 'stop':
                if self._cronDTC[channel].is_alive():
                    serv.privmsg(channel, 'cronDTC : stopped !')
                    self.__prompt('host', '{%alert%}cronDTC : stopped !{%default%}')
                else:
                    serv.privmsg(channel, 'cronDTC : already stopped !')
                    self.__prompt('host', '{%alert%}cronDTC : already stopped !{%default%}')
            elif items[0] == 'update':
                items.pop(0)
                if len(items) > 5:
                    serv.privmsg(channel, 'cronDTC : update refuse ! (possible abuse frequency)')
                    self.__prompt('host', '{%alert%}cronDTC : update refuse ! (possible abuse frequency){%default%}')
                elif croniter.is_valid(' '.join(items[:5])):
                    self._cronDTC[channel].expanded, self._cronDTC[channel].nth_weekday_of_month = croniter.expand(' '.join(items[:5]))
                else:
                    serv.privmsg(channel, 'cronDTC : update refuse !')
                    self.__prompt('host', '{%alert%}cronDTC : update refuse !{%default%}')
            elif message == 'next':
                if self._cronDTC[channel].is_alive():
                    _next = delai(datetime.fromtimestamp(self._cronDTC[channel].get_current()))
                    serv.privmsg(channel, 'cronDTC : next in {next} !'.format(next = _next))
                    self.__prompt('host', '{%alert%}cronDTC : next in {next} !{%default%}', next = _next)
            else:
                return False
        else:
            if not message:
                self._cronDTC[channel] = cron(target = self.do_dtc, expr_format = '0 * * * *', args = (self._name, channel, serv, ''))
            elif croniter.is_valid(' '.join(items[:5])):
                self._cronDTC[channel] = cron(target = self.do_dtc, expr_format = ' '.join(items[:5]), args = (self._name, channel, serv, ''))
            else:
                return False
            self._cronDTC[channel].start()
            serv.privmsg(channel, 'cronDTC : start !')
            self.__prompt('host', '{%alert%}cronDTC : start !{%default%}')
        return True

class MyCmd(Cmd):
    prompt = ('\r<\033[1;32mYou\033[0m> ','\r<You> ')[sys.platform == 'win32']
    def __init__(self, robot):
        Cmd.__init__(self)
        self._robot = robot
    def emptyline(self):
        pass
    def __start_completion(self):
        if self.use_rawinput and self.completekey and hasattr(self, 'old_completer'):
            try:
                try:
                    import readline
                except ImportError:
                    from pyreadline.rlmain import Readline
                    readline = Readline()
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
    def __stop_completion(self):
        if self.use_rawinput and self.completekey and hasattr(self, 'old_completer'):
            try:
                try:
                    import readline
                except ImportError:
                    from pyreadline.rlmain import Readline
                    readline = Readline()
                readline.parse_and_bind(self.completekey+": self-insert")
            except ImportError:
                pass
    def precmd(self, line):
        self.__stop_completion()
        return Cmd.precmd(self, line)
    def postcmd(self, stop, line):
        self.__start_completion()
        return Cmd.postcmd(self, stop, line)
    def completenames(self, text, *ignored):
        channel = self._robot.channels.get(self._robot._channel, None)
        if channel:
            users = [pseudo for pseudo in self._robot.channels.get(self._robot._channel, []) if pseudo.startswith(text)]
        else:
            users = []
        return Cmd.completenames(self, text, *ignored) + users
    def default(self, line):
        if self._robot._server:
            self._robot._server.privmsg(robot.get_channel(),line)
    def completedefault(self, text, line , start_index, end_index):
        channel = self._robot.channels.get(self._robot._channel, None)
        if not channel:
            return []
        if text:
            return [
                address for address in channel.users()
                if address.startswith(text)
            ]
        else:
            return channel.users()
    def do_shell(self, line):
        if line:
            line = line.split()
            cmd = line.pop(0)
            if cmd == 'msg':
                if self._robot._server:
                    self._robot._server.privmsg(line[0],' '.join(line[1:]))
                else:
                    self.stdout.write(('%sBot is not connected !\n' % self._robot._prompt['host']).__format__(**PROMPT))
            elif cmd == 'admin':
                if len(line) == 2:
                    if line[0] == 'stop' and hasattr(self._robot, 'do_'+line[1]):
                        self._robot.__function__[line[1]] = -1
                        self.stdout.write(('%s{%%alert%%}%s{%%default%%} function has been stop\n' % (self._robot._prompt['host'], line[1])).__format__(**PROMPT))
                        if self._robot._server:
                            for admin in [admin for admin in self._robot._stat if self._robot._stat[admin].status == -1]:
                                self._robot._server.privmsg(admin, '{function} function has been stop'.format(function = line[1]))
                        if line[1] == 'cronVDM':
                            for channel in self._robot.channels:
                                if channel in self._robot._cronVDM:
                                    self._cronVDM[channel].stop()
                        if line[1] == 'cronDTC':
                            for channel in self._robot.channels:
                                if channel in self._robot._cronDTC:
                                    self._cronDTC[channel].stop()
                    elif line[0] == 'reset':
                        if hasattr(self._robot, 'do_'+line[1]):
                            self.__function__[line[1]] = 0
                            self.stdout.write(('%s{%%alert%%}%s{%%default%%} function status has been reset\n' % (self._robot._prompt['host'], line[1])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{function} function status has been reset'.format(function = line[1]))
                        elif line[1] in self._robot.channels[self._robot._channel].users():
                            self._stat[line[1]].status = 0
                            self.stdout.write(('%s{%%alert%%}%s{%%default%%} function status has been reset\n' % (self._robot._prompt['host'], line[1])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{target} function status has been reset'.format(target = line[1]))
                    elif line[0] == 'get':
                        if line[1] in self._robot.channels[self._robot._channel].users():
                            self.stdout.write(('%s{%alert%}%s{%default%} function status is %s\n' % (self._robot._prompt['host'], line[1], self._robot._stat[line[1]])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{target} function status is {status}'.format(target = line[1], status = self._robot._stat[line[1]]))
                        elif hasattr(self, 'do_'+line[1]):
                            self.stdout.write(('%s{%alert%}%s{%default%} function status is %s\n' % (self._robot._prompt['host'], line[1], self._robot.__function__[line[1]])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{function} function status is {status}'.format(function = line[1], status = self._robot.__function__[line[1]]))
                elif len(line) == 3:
                    if line[0] == 'set':
                        if line[1] in self._robot.channels[self._robot._channel].users() and line[2].isdigit():
                            self._stat[line[1]].status = int(line[2])
                            self.stdout.write(('%s{%alert%}%s{%default%} function status is {%welcome%}%s{%default%} now !\n' % (self._robot._prompt['host'], line[1], self._robot._stat[line[1]])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{target} function status is {status} now !'.format(target = line[1], status = self._robot._stat[line[1]]))
                        elif hasattr(self, 'do_'+line[1]) and line[2].isdigit():
                            self._robot.__function__[line[1]] = int(line[2])
                            self.stdout.write(('%s{%alert%}%s{%default%} function status is {%welcome%}%s{%default%} now !\n' % (self._robot._prompt['host'], line[1], self._robot.__function__[line[1]])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{function} function status is {status} now !'.format(function = line[1], status = self._robot.__function__[line[1]]))
                    elif line[0] == 'add':
                        if line[1] in self._robot.channels[self._robot._channel].users() and line[2].isdigit():
                            self._robot._stat[line[1]].status += int(line[2])
                            self.stdout.write(('%s{%alert%}%s{%default%} function status is {%welcome%}%s{%default%} now !\n' % (self._robot._prompt['host'], line[1], self._robot._stat[line[1]])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{target} function status is {status} now !'.format(target = line[1], status = self._robot._stat[line[1]]))
                        elif hasattr(self._robot, 'do_'+line[1]) and line[2].isdigit():
                            self.__function__[line[1]] += int(line[2])
                            self._robot.stdout.write(('%s{%alert%}%s{%default%} function status is {%welcome%}%s{%default%} now !\n' % (self._robot._prompt['host'], line[1], self._robot.__function__[line[1]])).__format__(**PROMPT))
                            if self._robot._server:
                                self._robot._server.privmsg(author, '{function} function status is {status} now !'.format(function = line[1], status = self._robot.__function__[line[1]]))
    def complete_shell(self, text, line, start_index, end_index):
        line = line.split()
        channel = self._robot.channels.get(self._robot._channel, None)
        if channel:
            users = [pseudo for pseudo in self._robot.channels.get(self._robot._channel, []) if pseudo.startswith(text)]
        else:
            users = []
        if text:
            if len(line) > 1:
                if line[0] == 'msg':
                    return [
                        address for address in users
                        if address.startswith(text)
                    ]
                elif line[0] == 'admin':
                    return [
                        address for address in users
                        if address.startswith(text)
                    ]
            else:
                return [
                    address for address in ['admin', 'msg']
                    if address.startswith(text)
                ]
        else:
            return self.pseudo
        return []
    def do_quit(self, line):
        return True
    def complete_quit(self, *ignored):
        return []

################################################################################

if __name__ == '__main__':
    ESC = Literal('\x1b')
    integer = Word(nums)
    escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer,';')) + oneOf(list(alphas)))
    
    UncolorString = lambda s : Suppress(escapeSeq).transformString(s)
    
    try:
        _file = open('stat.txt','r+')
        text = _file.read()
        _file.close()
    except IOError:
        print ('\033[1;33mNo statistic found !\033[0m', 'No statistic found !')[sys.platform == 'win32']
        stat= {}
        text="""[DEFAULT]
words = 0
letters = 0
messages = 0
status = 0
urls = []"""
    
    stat = {}
    args['stat'] = stat
    config = ConfigParser()
    config.readfp(io.BytesIO(text))
    urls = re.compile("'((?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)',?")
    for section in config.sections():
        words, letters, messages, status, url_list = 0, 0, 0, 0, []
        if config.has_option(section, 'words'):
            words = int(config.get(section,'words'))
        if config.has_option(section, 'letters'):
            letters= int(config.get(section,'letters'))
        if config.has_option(section, 'messages'):
            messages = int(config.get(section,'messages'))
        if config.has_option(section, 'status'):
            status = int(config.get(section,'status'))
        if config.has_option(section, 'urls'):
            url_list = urls.findall(config.get(section,'urls'))
        stat.update({section:Stat(section, words, letters, messages, status, url_list)})
    
    robot = Robot(**args)
    Thread(target = robot.start).start()
    try:
        MyCmd(robot).cmdloop()
    except:
        robot.die()
    finally:
        stat = robot._stat
        for name in stat:
            if not config.has_section(name):
                try:
                    config.add_section(name)
                except:
                    continue
            _stat = stat[name].__dict__
            _name = _stat.pop('name')
            for key in _stat:
                config.set(_name, key, _stat[key])
        with open('stat.txt', 'wb') as configfile:
            config.write(configfile)

#EOF
