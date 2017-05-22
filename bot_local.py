#!/usr/bin/python
# -*- coding: utf-8 -*-

"""################################################################################
#
# File Name         : bot_local.py
# Created By        : Florian MAUFRAIS
# Contact           : florian.maufrais@gmail.com
# Creation Date     : december  22th, 2015
# Version           : 1.1.0
# Last Change       : April 11th, 2017 at 15:50
# Last Changed By   : Florian MAUFRAIS
# Purpose           : This programm use an IRC bot and cmd line interface
#                     If you find bugs or want more information please contact !
#
################################################################################"""

__version__='1.1.0'
__all__=['Robot','lancheur','MyCmd','__version__']

################################################################################
import base64, os, random, md5, sys, re, requests, ConfigParser, io, cmd
#import select

from threading import Thread
from datetime import datetime

try:
    from croniter import croniter
    import time
except ImportError:
    raise ImportError("You need libs croniter !")

try: 
    import dateutil.parser
except ImportError:
    raise ImportError("You need libs dateutil !")

try:
    import irclib,ircbot
except ImportError:
    raise ImportError("You need libs IRC !")

try:
    import optparse
    from optparse import make_option
except ImportError:
    raise ImportError("You need lib optparse !")
    
try:
    import pyparsing
    from pyparsing import *
except ImportError:
    raise ImportError("You need pyparsing lib !") 
        
def prompt() :
    import readline
    origline = readline.get_line_buffer()
    sys.stdout.write('\r'+my_cmd.prompt+origline)
    sys.stdout.flush()

class Robot(ircbot.SingleServerIRCBot):
    def __init__(self, name = 'Martoni', channel = '#Martoni', server = 'irc.worldnet.net', password = None, port = 7000, ssl = True):
        self.__name = name
        self.__channel = channel
        self.__server = server
        self.__port = port
        self.__connected = False
        self.__ssl = ssl
        self.away = False
        self.away_message = ''
        self.fonctions = False
        self.autohello = False
        self.wake_up = datetime.now()
        self.last_stop = datetime.now()
        self.admins = ['elcoc0']
        self.half_admins = []
        self.superadmins = ['Martoni','Patrik','frenchbeard','nodulaire']
        self.lastkick = ['','','','']
        self.history = []
        self.__stop = False
        self.end = False
        self.try_quit = False
        self.fonction_list = ['!md5','!help','!decodeb64','!encodeb64','!vdm','!dtc','!score']
        self.fonction_list_admin = ['!stat','!fonction','!stats','!admin','!halfadmin','!unhalfadmin','!order66','!cronvdm','!crondtc','!away','!info','!tu','!topurl']
        self.__url = re.compile('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], name, "Bot build with ircbot",password=password, ssl=ssl)
    def on_welcome(self, serv, ev):
        serv.join(self.__channel)
        self.__serv = serv
        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
            '\033[0m> \033[1;32mBot is now connect to',self.__server,'!\033[0m'
        prompt()
    def on_join(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        channel = ev.target()
        if author != self.__name:
            info = self.channels[self.__channel]
            print ('\r<\033['+PROMPT['%channel%']+'m'+channel+'\033[0m> \033[0;32m '+self.__user_mode(author)+author),'enter !\033[0m'
            if not name in stat.keys():
                stat.update({name:{item:0 for item in stats}})
                stat[author].update({'urls':[]})
                config.add_section(name)
                for item in stats:
                    config.set(name,item,0)
                config.set(name,'urls','[]')
        else:
            self.__connected = True
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32mJoin',self.__channel,'on',self.__server,'\033[0m '
        prompt()
    def on_pubmsg(self, serv, ev):
        message = ev.arguments()[0]
        author = irclib.nm_to_n(ev.source())
        channel = ev.target()
        info = self.channels[ev.target()]
        mess = message
        for name in list(set(my_cmd.pseudo) ^ set([self.__name])):
            message.replace(name,'\033['+PROMPT['%pseudo_other%']+'m'+name+'\033[0m')
        print '\r<\033['+PROMPT['%pseudo%']+'m'+self.__user_mode(author)+author+'\033[0m,\033['+PROMPT['%channel%']+'m'+channel+\
            '\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+'\033[0m> '+message
        if author in stat.keys():
            stat[author].update({'messages':stat[author]['messages']+1})
            stat[author].update({'words':stat[author]['words']+len(message.split(' '))})
            stat[author].update({'letters':stat[author]['letters']+len(message)-message.count(' ')})
        else:
            config.add_section(author)
            for item in stats:
                config.set(author,item,0)
            config.set(author,'urls','[]')
            stat.update({author:{item:0 for item in stats}})
            stat[author].update({'messages':stat[author]['messages']+1})
            stat[author].update({'words':stat[author]['words']+len(message.split(' '))})
            stat[author].update({'letters':stat[author]['letters']+len(message)-message.count(' ')})
            stat[author].update({'urls':[]})
        urls = self.__url.findall(mess)
        if urls:
            for url in urls:
                urls_user = stat[author]['urls']
                nb = [item[0] for item in urls_user].count(url) + 1
                if nb == 1:
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] == nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:pos]+[[url, 1, datetime.now().isoformat()[:-7]]]+urls_user[pos:]
                else:
                    index = [item[0] for item in urls_user].index(url)
                    temp = urls_user[index]
                    nb = temp[1] +1
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] <= nb:
                                pos = urls_user.index(item)
                                break
                    urls_user = urls_user[:index]+urls_user[index+1:]
                    temp[1] += 1
                    temp[2] = datetime.now().isoformat()[:-7]
                    urls_user = urls_user[:pos]+[temp]+urls_user[pos:]
                stat[author].update({'urls':urls_user})
                urls_user = self.all_url
                nb = [item[0] for item in urls_user].count(url) + 1
                if nb == 1:
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] == nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:pos]+[[url, 1, datetime.now().isoformat()[:-7]]]+urls_user[pos:]
                else:
                    index = [item[0] for item in urls_user].index(url)
                    temp = urls_user[index]
                    nb = temp[1] +1
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] <= nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:index]+urls_user[index+1:]
                    temp[1] += 1
                    temp[2] = datetime.now().isoformat()[:-7]
                    urls_user = urls_user[:pos]+[temp]+urls_user[pos:]
                self.all_url = urls_user
        self.fonction(serv, channel, mess, author)
        prompt()
    def on_privmsg(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        if self.channels.__contains__(self.__channel):
            info = self.channels[self.__channel]
        time = datetime.now().time().isoformat().split('.')[0][:-3]
        if not self.away:
            if author != self.__name:
                print  '\r<\033['+PROMPT['%pseudo_private%']+'m'+author+'\033[0m,\033['+PROMPT['%private%']+'mprivate\033[0m,\033['+\
                    PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+'\033[0m> '+message
            else:
                if message ==    '!stat' and author == self.__name:
                    info = self.channels[self.__channel]
                    for name in ' '.join(info.users()).replace('~','').replace('&','').split(' '):
                        if not name in stat.keys():
                            stat.update({name:{item:0 for item in stats}})
                            stat[author].update({'urls':[]})
                            if not  config.has_section(name):
                                config.add_section(name)
                            for item in stats:
                                config.set(name,item,0)
                            config.set(name,'urls','[]')
                elif message.split(' ')[0] == '!quit':
                    if len(message.split(' ')) > 1:
                        serv.disconnect(message.split(' ',1)[1])
                    else :
                        serv.disconnect()
                    sys.exit()
                elif message == '!whois connect' and self.channels.__contains__(self.__channel):
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> '+(', '.join(['%s%s' % (self.__user_mode(aut),aut) for aut in info.users()])+\
                        ' are on line !','Only you are on line !')[len(info.users()) <= 1]
                    for pseudo in info.users():
                        if not pseudo in my_cmd.pseudo:
                            my_cmd.pseudo.append(pseudo)
                elif message.split(' ')[0] == '!kickirc' and self.channels.__contains__(self.__channel) and not self.__user_mode(self.__name) in ['','%','+']:
                    for name in message.split(' ')[1:]:
                        if name in info.users() and not info.is_owner(name) and not info.is_admin(name) and not info.is_oper(name):
                            serv.kick(self.__channel,name,'No raison I\'m a bot !')
                        elif name in info.users():
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Command refused ! (target have to many right)'
                        else:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Command refused ! (name invalid)'
                elif message.split(' ')[0] == '!kickirc' and self.channels.__contains__(self.__channel):
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> Command refuse the bot is unright !\n'
        else:
            if self.away_message != '':
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Bot auto response :'+self.away_message
            else:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Bot auto response : no admin to get response !'
                serv.privmsg(author,'Bot auto response : no admin to get response !')
        self.fonction(serv, author, message, author)
        prompt()
    def on_kick(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        self.lastkick = [message,ev.arguments()[1],datetime.now().isoformat()[:-7],author]
        print ('\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
            '\033[0m> \033[1;32m'+self.__user_mode(author)+author),'kick',message,'from',channel,'!',\
            ('','('+ev.arguments()[1]+')')[len(ev.arguments()) > 1],'\033[0m'
        if message == self.__name:
            serv.join(channel)
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32mBot was kick from',channel,' and reconnect !\033[0m'
        prompt()
    def on_part(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        if message != []:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32m'+self.__user_mode(author)+author,('has left ! ('+' '.join(message)+')\033[0m')
        else:
            print ('\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32m'+self.__user_mode(author)+author),'has left !\033[0m'
        prompt()
    def on_quit(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        if message != []:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32m'+self.__user_mode(author)+author,('has left ! ('+' '.join(message)+')\033[0m')
        else:
            print ('\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32m'+self.__user_mode(author)+author),'has left !\033[0m'
        prompt()
    def on_nick(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        if author in self.admins:
            self.admins.remove(author)
            self.admins.append(channel)
        if author in self.half_admins:
            self.half_admins.remove(author)
            self.half_admins.append(channel)
        info = self.channels[self.__channel]
        print '\r<\033['+PROMPT['%channel%']+'m'+self.__channel+'\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
            '\033[0m> \033[1;32m'+self.__user_mode(author)+author,'has rename in',channel,'\033[0m'
        if not channel in stat.keys():
            stat.update({channel:{item:0 for item in stats}})
            config.add_section(channel)
            for item in stats:
                config.set(channel,item,0)
            config.set(author,'urls','[]')
        prompt()
    def on_action(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        print ('<\033['+PROMPT['%channel%']+'m'+channel+'\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
            '\033[0m> \033[1;32m*'+self.__user_mode(author)+author+' '+' '.join(message)+'*\033[0m')
        if author in stat.keys():
            stat[author].update({'messages':stat[author]['messages']+1})
            stat[author].update({'words':stat[author]['words']+len(message)})
            stat[author].update({'letters':stat[author]['letters']+len(''.join(message))})
        else:
            config.add_section(author)
            for item in stats:
                config.set(author,item,0)
            config.set(author,'urls','[]')
            stat.update({author:{item:0 for item in stats}})
            stat[author].update({'messages':stat[author]['messages']+1})
            stat[author].update({'words':stat[author]['words']+len(message)})
            stat[author].update({'letters':stat[author]['letters']+len(''.join(message))})
            stat[author].update({'urls':[]})
        prompt()
    def on_mode(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        liste_spe= 'inpstmclkSR'
        #if True in [item in liste_spe for item in message[0]]:
        #    for item in range(len(message[0])):
        #        if not item in '+-':
        #            tp = 0
        #            while not message[0][item-tp] in '+-':
        #                tp += 1
        #            serv.mode(channel,('-','+')[message[0][item-tp] == '-']+message[0][item])
        print ('\r<\033['+PROMPT['%channel%']+'m'+channel+'\033[0m> \033[1;32m'+self.__user_mode(author)+author+' change mode : '+' '.join(message)+'\033[0m')
        prompt()
    def on_currenttopic(self, serv, ev):
        arg = ev.arguments()
        mess = '\r<\033['+PROMPT['%host%']+'mHost\033[0m> Current topic on '+str(arg[0])+' : '+str(arg[1])+'\n'
        self.topic = mess
        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%private%']+'mprivate\033[0m,\033['+PROMPT['%time%']+'m'+\
            datetime.now().time().isoformat().split('.')[0]+'\033[0m> '+mess.split('>',1)[1]
        prompt()
    def on_topic(self, serv, ev):
        arg = ev.arguments()
        mess = '\r<\033['+PROMPT['%host%']+'mHost\033[0m> New topic on '+str(ev.target())+' by '+irclib.nm_to_n(ev.source())+' : '+str(arg[0])+'\n'
        self.topic = mess
        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%private%']+'mprivate\033[0m,\033['+PROMPT['%time%']+'m'+\
            datetime.now().time().isoformat().split('.')[0]+'\033[0m> '+mess.split('>',1)[1]
        prompt()
    def on_help(self, serv, dest):
        #info = self.channels[self.__channel]
        if dest in self.half_admins and not dest in self.admins+self.superadmins+[self.__name]:
            serv.privmsg(dest,'You can use following command even if they are block for normal user :')
        serv.privmsg(dest,'Accepted commands :')
        serv.privmsg(dest,'- !help : give all accepted commands')
        serv.privmsg(dest,'- !vdm [number] : give random vdm, limited to 15')
        serv.privmsg(dest,'- !dtc [number] : give random dtc, limited to 26')
        serv.privmsg(dest,'- !encodeb64 [text]')
        serv.privmsg(dest,'- !decodeb64 [text]')
        serv.privmsg(dest,'- !md5 [text]')
        serv.privmsg(dest,'- !lastkick : Give information from the last pseudo kick in the channel, it could have no information')
        serv.privmsg(dest,'- !score< pseudo>* : give Root-me and Newbie score, if it exist !')
        if dest in self.admins+self.superadmins+[self.__name]:
            serv.privmsg(dest,'Your are special, you can use previous fonctions even is they are block and use next fonctions :')
            serv.privmsg(dest,'- !fonction [on|off] : (un)active bot fonctions')
            serv.privmsg(dest,'- !order66 : Bot execute order 66 against a random user in the channel')
            serv.privmsg(dest,'- !info : bot informations (only in primsg)')
            serv.privmsg(dest,'- !stat< pseudo>* : Give stats of pseudo list, if no pseudo it give your stat')
            serv.privmsg(dest,'- (!tu|!topurl)< pseudo>* : Give top 10 of url listen ([url, number_of_hint, last_hit]), if no pseudo it\'s global top')
            serv.privmsg(dest,'- (!lp|!lastpast) [nb] : Give top nb (3 to 10) of last pastbin saved ([url, last_hit])')
            serv.privmsg(dest,'- !stats : Give all stats ! (the list could be long !)')
            serv.privmsg(dest,'- !halfadmin< pseudo>+ : Give half admin right for each pseudo in your list')
            serv.privmsg(dest,'- !halfadmins : Give half admin list')
            if dest in self.superadmins+[self.__name]:
                serv.privmsg(dest,'Your are realy special, you can use fonctions that special person can\'t :')
                serv.privmsg(dest,'- !admin< pseudo>+ : Give admin right for each pseudo in your list')
                serv.privmsg(dest,'- !admins : Give admin list')
    def get_name(self):
        return self.__name
    def get_server(self):
        return [self.__server,self.__serv]
    def get_channel(self):
        return self.__channel
    def __user_mode(self, name):
        info = self.channels[self.__channel]
        return ((((('','+')[info.is_voiced(name)],'%')[info.is_halfop(name)],'@')[info.is_oper(name)],\
            '&')[info.is_admin(name)],'~')[info.is_owner(name)]
    def info(self):
        if self.__connected:
            info = self.channels[self.__channel]
            delta = datetime.now() - self.wake_up
            ret = 'Bot name : '+self.__name+'\nConnected on channel :  '+self.__channel+'\nConnected on server : '+self.__server+'\n'+\
                ((((('','Bot is voiced !')[info.is_voiced(name)],'Bot is half oper !')[info.is_halfop(name)],\
                'Bot is oper !')[info.is_oper(name)],'Bot is admin !')[info.is_admin(name)],'Bot is owner !')[info.is_owner(name)]+'\n'+\
                'Bot is awoken for '+('',str(delta.days)+' day'+('s','')[delta.days<1]+' ')[delta.days > 0]+\
                ('',str(delta.seconds/3600)+' hour'+('s','')[delta.seconds/3600 < 1]+' ')[delta.seconds > 3600]+\
                (str(delta.seconds%60)+' seconde'+('s','')[delta.seconds%60 < 1],\
                str((delta.seconds/60)%60)+' minute'+('s','')[(delta.seconds/60)%60 < 1])[delta.seconds > 60]
        else: 
            ret = 'Bot name : '+self.__name+'\nBot is not connected !'
        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m> '+ret
        return ret
    def is_connected(self):
        return self.__connected
    def quit(self, raison=None):
        raison = (raison,'Time to quit !')[raison==None or not raison is str]
        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+\
            datetime.now().time().isoformat().split('.')[0]+'\033[0m> \033[1;33m'+raison+'\033[0m'
        self.stop()
    def fonction(self, serv, name, message, author):
        info = self.channels[self.__channel]
        if self.fonctions or author in [self.__name]+self.superadmins+self.admins+self.half_admins and False:
            if message == '!help':
                self.on_help(serv, author)
            elif message == '!lastkick':
                if self.lastkick[0] != '':
                    in_time = dateutil.parser.parse(datetime.now().isoformat()[:-7]) - dateutil.parser.parse(self.lastkick[2])
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> '+self.lastkick[0]+' is the lastkick from '+self.__channel+', he was excluded by '+self.lastkick[3]+\
                        ' for reason : '+self.lastkick[1]+'; '+((str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60)+' hour'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60 in [0,1]]+' '+\
                        (str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 == 0]+\
                        ' ',str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]]+\
                        ' ')[in_time.seconds < 3599],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                        str(in_time.seconds%60)+' seconde'+('s','')[in_time.seconds%60 in [0,1]]+' ago\033[0m'
                    serv.privmsg(name, self.lastkick[0]+' is the lastkick from '+self.__channel+', he was excluded by '+self.lastkick[3]+\
                        ' for reason : '+self.lastkick[1]+'; '+((str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60)+' hour'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60 in [0,1]]+' '+\
                        (str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 == 0]+\
                        ' ',str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]]+\
                        ' ')[in_time.seconds < 3599],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                        str(in_time.seconds%60)+' seconde'+('s','')[in_time.seconds%60 in [0,1]]+' ago')
                else:
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> \033[1;32mNo Kick saved\033[0m' 
                    serv.privmsg(name, 'No Kick saved')
            elif message.split(' ')[0] == '!encodeb64' and len(message.split(' ',1)) == 2:
                serv.privmsg(name, base64.b64encode(message.split(' ',1)[1]))
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> ',base64.b64encode(message.split(' ',1)[1])
            elif message.split(' ')[0] == '!decodeb64' and len(message.split(' ',1)) == 2:
                try:
                    serv.privmsg(name, base64.b64decode(message.split(' ',1)[1]))
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> ',base64.b64decode(message.split(' ',1)[1])
                except:
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> Can\'t decode data !\033[0m'
                    serv.privmsg(name, 'Sorry buy I can\'t decode !')
            elif message.split(' ')[0] == '!md5' and len(message.split(' ',1)) == 2:
                serv.privmsg(name, md5.new(message.split(' ',1)[1]).digest())
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> ',md5.new(message.split(' ',1)[1]).digest()
            elif message.split(' ')[0] == '!vdm':
                page=requests.get('http://www.viedemerde.fr/aleatoire')
                if page.ok:
                    p = re.compile('<div class="post article( cat-\\S+)+" id="[0-9]+">(<p class="content">)?<a href="/\\S+/[0-9]+" class="fmllink">(.*)VDM</a></p>')
                    vdm = p.findall(page.content)
                    result = []
                    lists = []
                    for item in vdm:
                        result.append(item[2].replace('&quot;','"')+'VDM')
                    if len(message.split(' ')) > 1 and message.split(' ')[1].isdigit():
                        nbr = int(message.split(' ')[1])
                    else:
                        nbr = 1
                    for item in range(min(nbr,len(result))):
                        if item > 0:
                            rdm = random.randint(0,len(result)-1)
                            while rdm in lists:
                                rdm = random.randint(0,len(result)-1)
                            lists.append(rdm)
                        else:
                            rdm = random.randint(0,len(result)-1)
                            lists = [rdm]
                        serv.privmsg(name, result[rdm])
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> ',result[rdm]
                else:
                    serv.privmsg(name, 'Impossible to contact : VDM ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')')
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> Impossible to contact : VDM ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')'
            elif message.split(' ')[0] == '!dtc':
                page=requests.get('http://danstonchat.com/random.html')
                if page.ok:
                    p = re.compile('item item[0-9]+"><p class="item-content">(.*)</p><p class="item-meta">.*</p></div>')
                    TAG_RE = re.compile(r'<[^>]+>')
                    dtc = page.content.split('<h1>Au hasard</h1>')[1].split('<div class="grid_')[0].split('<div class')[1:]
                    result = []
                    lists = []
                    for item in dtc:
                        a=p.findall(item.replace('\r',''))[0]
                        result.append(TAG_RE.sub('', a.replace('<br />','\n')).replace('&lt;','<').replace('&gt;','>').replace('&#039;',"'").replace('&quot;','"'))
                    if len(message.split(' ')) > 1 and message.split(' ')[1].isdigit():
                        nbr = int(message.split(' ')[1])
                    else:
                        nbr = 1
                    for item in range(min(nbr,len(result))):
                        if item > 0:
                            rdm = random.randint(0,len(result)-1)
                            while rdm in lists:
                                rdm = random.randint(0,len(result)-1)
                            lists.append(rdm)
                        else:
                            rdm = random.randint(0,len(result)-1)
                            lists = [rdm]
                        for element in result[rdm].split('\n'):
                            serv.privmsg(name, element)
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+'\033[0m> ',result[rdm]
                else:
                    serv.privmsg(name, 'Impossible to contact : DTC ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')')
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> Impossible to contact : DTC ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')'
            elif message.split(' ')[0] == '!score':
                if len(message.split(' ')) == 1:
                    message += ' '+author    
                for _name in message.split(' ')[1:]:
                    page=requests.get('http://www.root-me.org/?page=recherche&lang=fr&recherche='+_name)
                    if 'pagination_recherche_authors' in page.content:
                        li = page.content.split('pagination_recherche_authors')[2].split('<ul>')[1].split('</ul>')[0][1:-1].split('\n')
                        p = re.compile('<li>.*href="(.*)">(.*)</a></li>')
                        q = re.compile('<b class="tl">Challenges :</b><span class="color1 tl">([0-9]+).*Points&nbsp;<span class="gris tm">([0-9]+)/([0-9]+).*'+\
                            '<span class="color1 tl">([0-9]+)<span class="gris">/([0-9]+)</span>.*Rang :.*<span class="color1 tl">(\S+)&nbsp;')
                        for item in li:
                            try:
                                if _name.lower() in p.findall(item)[0][1].lower():
                                    page=requests.get('http://www.root-me.org'+p.findall(item)[0][0].split('?')[0]+'?inc=score&lang=fr')
                                    temp =  q.findall(page.content.split('small-12 columns')[3].split('<a class="mediabox pageajax"')[0].replace('\n',''))[0]
                                    print ('\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                        '\033[0m> \033[1;32m'+p.findall(item)[0][1]+' have '+temp[0]+' point'+('s','')[temp[0] == 0]+', he resolved '+temp[1]+' of the '+temp[2]+\
                                        ' challenge'+('s','')[temp[2] == 0]+', he\'s ranked at '+temp[3]+' out of '+temp[4]+' players ('+temp[5]+') in Root-me\033[0m')
                                    serv.privmsg(name, p.findall(item)[0][1]+' have '+temp[0]+' point'+('s','')[temp[0] == 0]+', he resolved '+temp[1]+' of the '+temp[2]+\
                                        ' challenge'+('s','')[temp[2] == 0]+', he\'s ranked at '+temp[3]+' out of '+temp[4]+' players ('+temp[5]+') in Root-me')
                            except:
                                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                    '\033[0m> \033[1;32mno such result in Root-me for',_name,'\033[0m'
                                serv.privmsg(name,'no such result in Root-me for '+_name)
                                break
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> \033[1;32mno such result in Root-me for',_name,'\033[0m'
                        serv.privmsg(name,'no such result in Root-me for '+_name)
                    page=requests.get('https://www.newbiecontest.org/index.php?page=classementdynamique&limit=0&member='+_name+'&nosmiley=0')
                    if 'Recherche de '+_name+' :' in page.content:
                        p = re.compile('<p class=".*">(.*) : ?</span> (([0-9]+/[0-9]+)</span>.*|(.*))</p>')
                        page=requests.get('https://www.newbiecontest.org/index.php?page=info_membre&amp;id='+\
                            page.content.split('Recherche de '+_name+' :')[1].split('<a href="index.php?page=info_membre&amp;id=')[1].split('"')[0])
                        value = p.findall(page.content.split('<div class="memberInfos">')[1].split('</div>')[0]+\
                            page.content.split('<h3>Challenges :</h3>')[1].split('<p>')[0])
                        val = {}
                        val.update({'name':page.content.split('<span class="nowrap">')[1].split('</span>')[0].split('line">')[-1]})
                        for item in value:
                            val.update({item[0]:(item[-2],item[-1])[item[-1]!='']})
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> \033[1;32m'+val['name']+' has '+val['Points']+' point'+('s','')[val['Points'] == 0]+', his rank is '+\
                            val['Position'].split('/')[0]+' out of '+val['Position'].split('/')[1]+' players ('+val['Titre']+') in Newbie\033[0m'
                        serv.privmsg(name, val['name']+' has '+val['Points']+' point'+('s','')[val['Points'] == 0]+', his rank is '+val['Position'].split('/')[0]+\
                            ' out of '+val['Position'].split('/')[1]+' players ('+val['Titre']+') in Newbie')
                    elif ' Affinez votre recherche' in page.content:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> \033[1;32mImpossible to complete search for '+_name+' in Newbie ('+\
                            page.content.split(' Affinez votre recherche')[0].split('<td>')[-1].replace('\n','')+')\033[0m'
                        serv.privmsg(name,'Impossible to complete search for '+_name+' in Newbie ('+\
                            page.content.split(' Affinez votre recherche')[0].split('<td>')[-1].replace('\n','')+')')
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> \033[1;32mno such result in Newbie for',_name,'\033[0m'
                        serv.privmsg(name,'no such result in Newbie for '+_name)
            elif author in [self.__name]+self.superadmins+self.admins:
                if message.split(' ')[0] == '!superadminofthedeath' and not author in self.admins:
                    serv.primsg(channel,'Do you think this commande realy exist ?')
                elif message == '!info' and self.channels.__contains__(self.__channel):
                    serv.privmsg(author,self.info())
                elif message == '!stats':
                    for _name in stat:
                            serv.privmsg(author,_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats]))
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> \033[0;32m'+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])+'\033[0m'
                elif message == '!order66':
                    cible = ' '.join(info.users()).split(' ')[random.randint(0,len(info.users())-1)]
                    serv.action(self.__channel, 'execute order 66')
                    print '\r<\033['+PROMPT['%channel%']+'m'+self.__channel+'\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> \033[1;32m*'+self.__name+' execute order 66*\033[0m'
                    info = self.channels[self.__channel]
                    if cible in info.users() and not info.is_owner(cible) and not info.is_admin(cible) and not info.is_oper(cible):
                        serv.kick(self.__channel,name,'take a blaster and open fire')
                    else:
                        serv.action(self.__channel, 'take a blaster, but con\'t open fire on '+cible)
                        print '\r<\033['+PROMPT['%channel%']+'m'+self.__channel+'\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> \033[1;32m*'+self.__name+' take a blaster, but con\'t open fire on '+cible+'*\033[0m'
                elif message == '!halfadmins':
                    if len(self.admins) != 0:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+'\033[0m> '+\
                            ', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+' half admin'+('s','')[len(self.admins)==1]
                        serv.privmsg(author, ', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+' half admin'+('s','')[len(self.admins)==1])
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+'\033[0m> There is no half admin'
                        serv.privmsg(author, 'There is no half admin')
                elif message.split(' ')[0] == '!stat':
                    if len(message.split(' ')) == 1:
                        message += ' '+author
                    for _name in message.split(' ')[1:]:
                        serv.privmsg(author,_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                            item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats]))
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+'\033[0m> '+\
                            _name+' send '+', '.join([ str(stat[_name][item])+' '+\
                            item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
                elif message.split(' ')[0] in ['!tu','!topurl']:
                    nb_url = 5
                    if len(message.split(' ')) == 1:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+'last hit the '+\
                            item[2][:-3].replace('T',' at ') for item in self.all_url[:nb_url]])
                        serv.privmsg(name, 'Global top url :')
                        time.sleep(0.1)
                        for item in self.all_url[:nb_url]:
                            time.sleep(0.1)
                            serv.privmsg(name, item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+'last hit the '\
                                +item[2][:-3].replace('T',' at '))
                    else:
                        for _name in message.split(' ')[1:]:
                            try:
                                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                    '\033[0m> '+_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+'last hit the '+\
                                    item[2][:-3].replace('T',' at ') for item in stat[_name]['urls'][:nb_url]])
                                serv.privmsg(name, _name+' top url :')
                                time.sleep(0.3)
                                for item in stat[_name]['urls'][:nb_url]:
                                    time.sleep(0.3)
                                    serv.privmsg(name, item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+\
                                        'last hit the '+item[2][:-3].replace('T',' at '))
                            except:
                                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                    '\033[0m> No stat for '+_name
                                serv.privmsg(author,'No stat for '+_name)
                elif message.split(' ')[0] in ['!lp','!lastpast']:
                    nb_past = 3
                    if len(message.split(' ')) == 2:
                        try:
                            nb_past = max(3,min(int(message.split(' ')[1]),10))
                        except:
                            nb_past = 3
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> Last pastbin :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+'last hit the '+\
                        item[2][:-3].replace('T',' at ') for item in self.all_url if re.match('(?:http[s]?|ftp)://\w+bin(?:[.]\w+)+(?:[/].*)?', item[0])][:nb_paste])
                    serv.privmsg(name, 'Last pastbin :')
                    time.sleep(0.3)
                    past_liste = [item for item in self.all_url if re.match('(?:http[s]?|ftp)://\w+bin(?:[.]\w+)+(?:[/].*)?', item[0])][:nb_paste]
                    for item in past_liste:
                        time.sleep(0.3)
                        serv.privmsg(name, item[0]+', last hit the '+item[2][:-3].replace('T',' at '))
                elif message.split(' ')[0] == '!cronvdm':
                    if message == 'cronvdm':
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Cronvdm is '+('off','on')[not cronvdm.stop]
                    elif message == 'cronvdm next':
                        test = cronvdm._iter.get_prev(datetime)
                        in_time = dateutil.parser.parse(cronvdm._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
                    elif message.split(' ')[1] in ['on','off'] and len(message.split(' ')) == 2:
                        if ('off','on')[not cronvdm.stop] == message.split(' ')[1]:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Cronvdm is already '+('off','on')[not cronvdm.stop]
                        else:
                            cronvdm.stop = (True,False)[message.split(' ')[1] == 'on']
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Cronvdm is '+('off','on')[not cronvdm.stop]
                    elif cronvdm and len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            cronvdm._iter = croniter(message.split(' ',1)[1],datetime.now())
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> New cronvdm value is :',message.split(' ',1)[1]
                        except:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Impossible option for !cronvdm'
                    elif len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            test = croniter(message.split(' ',1)[1], datetime.now())
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Cronvdm is already off'
                        except:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Impossible option for !cronvdm'
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Unkown option for !cronvdm'
                elif message.split(' ')[0] == '!crondtc':
                    if message == 'crondtc':
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> crondtc is '+('off','on')[not crondtc.stop]
                    elif message == 'crondtc next':
                        test = crondtc._iter.get_prev(datetime)
                        in_time = dateutil.parser.parse(crondtc._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
                    elif message.split(' ')[1] in ['on','off'] and len(message.split(' ')) == 2:
                        if ('off','on')[not crondtc.stop] == message.split(' ')[1]:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Crondtc is already '+('off','on')[not crondtc.stop]
                        else:
                            crondtc.stop = (True,False)[message.split(' ')[1] == 'on']
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Crondtc is '+('off','on')[not crondtc.stop]
                    elif crondtc and len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            crondtc._iter = croniter(message.split(' ',1)[1],datetime.now())
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> New crondtc value is :',message.split(' ',1)[1]
                        except:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Impossible option for !crondtc'
                    elif len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            test = croniter(message.split(' ',1)[1], datetime.now())
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> crondtc is already off'
                        except:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Impossible option for !crondtc'
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Unkown option for !crondtc'
                elif message.split(' ')[0] == '!fonction':
                    if message == '!fonction':
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Fonctions are',('off','on')[self.fonctions]
                        serv.privmsg(self.__channel, 'Fonctions are '+('off','on')[self.fonctions])
                    elif message.split(' ')[1] in ['on','off']:
                        if ('off','on')[self.fonctions] == message.split(' ')[1]:
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Fonctions are already',('off','on')[self.fonctions]
                            serv.privmsg(self.__channel, 'Fonctions are already '+('off','on')[self.fonctions])
                        else:
                            self.fonctions = (False,True)[message[1:-1].split(' ')[1] == 'on']
                            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                                '\033[0m> Fonctions are',('off','on')[self.fonctions]
                            serv.privmsg(self.__channel, 'Fonctions are '+('off','on')[self.fonctions])
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Unkown option for !fonction'
                        serv.privmsg(author,'Unkown option for !fonction')
                elif message.split(' ')[0] == '!halfadmin' and len(message.split(' ')[1:]) > 1:
                    for name in message[1:-1].split(' ')[1:]:
                        self.half_admins.append(name)
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> '+', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                            ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n'
                    if name != self.__name:
                        serv.privmsg(author,', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                            ' halfadmin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n')
                elif message.split(' ')[0] == '!unhalfadmin' and len(message.split(' ')) > 1 :
                    temp_H = []
                    for name in message.split(' ')[1:]:
                        if name in self.half_admins:
                            self.half_admins.remove(name)
                            temp._H.append(name)
                    if len(temp_H) != 0:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> '+', '.join(temp_H)+' '+('are','is')[len(temp_H)==1]+' not half admin'+('s','')[len(temp_H)==1]+' now'
                elif message.split(' ')[0] == '!admins' and not author in self.admins:
                    if len(self.admins) != 0:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> '+', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+' admin'+('s','')[len(self.admins)==1]
                        serv.privmsg(author, ', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+' admin'+('s','')[len(self.admins)==1])
                    else:
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> There is no admin'
                        serv.privmsg(author, 'There is no admin')
                elif message.split(' ')[0] == '!admin' and len(message.split(' ')[1:]) > 1 and not author in self.admins:
                    for name in message[1:-1].split(' ')[1:]:
                        self.admins.append(name)
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> '+', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                        ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n'
                    if name != self.__name:
                        serv.privmsg(author,', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                            ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n')
        elif message.split(' ')[0] == '!vdm' and not cronvdm.stop and False:
            in_time = dateutil.parser.parse(cronvdm._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
            test = cronvdm._iter.get_prev(datetime)
            serv.privmsg(name, 'You have not access to this fonction but next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]])
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> You have not access to this fonction but next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
        elif message.split(' ')[0] == '!dtc' and not crondtc.stop and False:
            in_time = dateutil.parser.parse(crondtc._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
            test = crondtc._iter.get_prev(datetime)
            serv.privmsg(name, 'You have not access to this fonction but next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]])
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> You have not access to this fonction but next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]

class lancheur(Thread):
    def __init__(self, fonction):
        if fonction in ['bot','client','cronvdm','crondtc']:
            Thread.__init__(self)
            self.fonction=fonction
            if fonction in ['cronvdm','crondtc']:
                self.stop = True
                self.end = False
        else:
            print '\003[0;32mThread aborded : Invalid fonction ! ('+fonction+')\033[0m'
    def run(self):
        if self.fonction == 'bot':
            try:
                robot.start()
            except Exception, e:
                print "You lose the game !"
            finally:
                print '\r\033[1;32mBot closed !\033[0m'
                sys.exit(0)
        elif self.fonction == 'client':
            while not robot.is_connected():
                quit = True
            cronvdm.stop = True
            crondtc.stop = True
            autore = True
            robot.get_server()[1].privmsg(robot.get_name(),'!stat')
            robot.get_server()[1].privmsg(robot.get_name(),'!whois connect')
            try:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> \033[1;32m',robot.topic+'\033[0m'
            except:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> \033[1;32mThere is no topic in this channel !\033[0m'
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32mFonctions are '+('off','on')[robot.fonctions]+'\033[0m'
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m>\033[1;32m Autohello is '+('off','on')[robot.autohello]+'\033[0m'
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> \033[1;32mAutore is '+('off','on')[autore]+'\033[0m'
            if robot.wake_up.day - robot.last_stop.day > 0:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> \033[1;32mAuto Zbra\033[0m'
                robot.get_server()[1].privmsg(robot.get_channel(), 'Zbra')
            else:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> \033[1;32mAuto Re\033[0m'
                robot.get_server()[1].privmsg(robot.get_channel(), 'Re')
            prompt()
            self.__last_error = None
            try:
                while not my_cmd.stop:
                    try:
                        my_cmd.cmdloop()
                    except Exception, e:
                        print e.__class__.__name__, e, e.message
                        if self.__last_error:
                            if [e,datetime.now().isoformat().split('.')[0]] == self.__last_error:
                                print "\033[0;31mError loop stop service !\033[0m"
                                raise Exception("Error loop stop service !")
                        self.__last_error= [e,datetime.now().isoformat().split('.')[0]]
            finally:
                print '\033[1;32mService is stopping !\033[0m'
                for name in stat.keys():
                    if not config.has_section(name):
                        config.add_section(name)
                        for item in stats:
                            config.set(name,item,0)
                    if not name in ['',None]:
                        for options in stat[name].keys():
                            config.set(name,options,stat[name][options])
                config.set('DEFAULT','time_stop',datetime.now().isoformat().split('.')[0])
                config.set('DEFAULT','all_url',str(robot.all_url))
                with open('stat.txt', 'wb') as configfile:
                    config.write(configfile)
                cronvdm.stop = True
                cronvdm.end = True
                crondtc.stop = True
                crondtc.end = True
                if not robot.is_connected():
                    robot.quit()                    
                print '\033[1;32mClient end correctly !\033[0m'
                sys.exit(0)
        elif self.fonction == 'cronvdm':
            while not self.end:
                while not self.stop:
                    _next = self._iter.get_next(datetime).isoformat()[:-1]
                    while datetime.now().isoformat()[:-8] != _next and not self.stop and not self.end:
                        time.sleep(3)
                    if not self.stop and robot.is_connected():
                        robot.get_server()[1].privmsg(robot.get_channel(),'Programmed VDM !')
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Programmed VDM !'
                        robot.fonction(robot.get_server()[1],robot.get_channel(),'!vdm',robot.get_name())
                        prompt()
                time.sleep(3)
        elif self.fonction == 'crondtc':
            while not self.end:
                while not self.stop:
                    _next = self._iter.get_next(datetime).isoformat()[:-1]
                    while datetime.now().isoformat()[:-8] != _next and not self.stop and not self.end:
                        time.sleep(3)
                    if not self.stop and robot.is_connected():
                        robot.get_server()[1].privmsg(robot.get_channel(),'Programmed DTC !')
                        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                            '\033[0m> Programmed DTC !'
                        robot.fonction(robot.get_server()[1],robot.get_channel(),'!dtc',robot.get_name())
                        prompt()
                time.sleep(3)
        else:
            print '\033[1;31mFunction unkown, programm stop\033[0m'
        
class MyCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "<\033[1;32mYou\033[0m> "
        self.persist = False
        self.pseudo = []
        self.history = {}
        self._help = {'help': None, 'quit':'if you are admin : bot quit, else you juste close client'}
        self.stop = False
        self.__url = re.compile('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    def postcmd(self, stop, line):
        if not line in self.history.values() and not line == '':
            self.history.update({len(self.history):line})
        return cmd.Cmd.postcmd(self, stop, line)
    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext)] + [a for a in self.pseudo if a.startswith(text)]
    def default(self, line):
        robot.get_server()[1].privmsg(robot.get_channel(),line)
        stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
        stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+len(line.split(' '))})
        stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+len(line)-line.count(' ')-2})
        urls = self.__url.findall(line)
        if urls:
            for url in urls:
                urls_user = stat[robot.get_name()]['urls']
                nb = [item[0] for item in urls_user].count(url) + 1
                if nb == 1:
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] == nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:pos]+[[url, 1, datetime.now().isoformat()[:-7]]]+urls_user[pos:]
                else:
                    index = [item[0] for item in urls_user].index(url)
                    temp = urls_user[index]
                    nb = temp[1] +1
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] <= nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:index]+urls_user[index+1:]
                    temp[1] += 1
                    temp[2] = datetime.now().isoformat()[:-7]
                    urls_user = urls_user[:pos]+[temp]+urls_user[pos:]
                stat[robot.get_name()].update({'urls':urls_user})
                urls_user = robot.all_url
                nb = [item[0] for item in urls_user].count(url) + 1
                if nb == 1:
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] == nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:pos]+[[url, 1, datetime.now().isoformat()[:-7]]]+urls_user[pos:]
                else:
                    index = [item[0] for item in urls_user].index(url)
                    temp = urls_user[index]
                    nb = temp[1] +1
                    pos = len(urls_user)
                    for item in urls_user:
                        if item[1] <= nb:
                            pos = urls_user.index(item)
                            break
                    urls_user = urls_user[:index]+urls_user[index+1:]
                    temp[1] += 1
                    temp[2] = datetime.now().isoformat()[:-7]
                    urls_user = urls_user[:pos]+[temp]+urls_user[pos:]
                robot.all_url = urls_user
    def emptyline(self):
        pass
    def completedefault(self, text, line , start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_msg(self, line):
        """Params : <pseudo> <message>
        Info : send <message in private to <pseudo>
        """
        robot.get_server()[1].privmsg(line.split(' ')[0],line.split(' ',1)[1])
    def complete_msg(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_quit(self, line):
        self.stop = True
        robot.quit(raison=(line,None)[len(line)==0])
        sys.exit(0)
    def complete_quit(self, text, line, start_index, end_index):
        pass
    def do_applause(self, line):
        robot.get_server()[1].action(robot.get_channel(),'applause')
        stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
        stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+1})
        stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+8})
    def complete_applause(self, *ignored):
        pass
    def do_away(self, line):
        """Params : ( <message>)?
        Info : Change away's mode of the bot
        """
        robot.away = not robot.away
        if robot.away and len(line.replace(' ', '')) != 0:
            robot.away_message = line
        else:
            robot.away_message = ''
        robot.get_server()[1].action(robot.get_channel(),('come back','is away'+(' ('+robot.away_message+')','')[len(robot.away_message)==0])[robot.away])
        print '\r<\033['+PROMPT['%host%']+'mHost,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
            '\033[0m> \033[1;32mRobot '+('get back','come away'+(' ('+robot.away_message+')','')[len(robot.away_message)==0])[robot.away]+'\033[0m'
    def complete_away(self, *ignored):
        pass
    def do_help(self, arg):
        #cmd.Cmd.do_help(self, arg)
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                if arg in self._help and self._help[arg] != None:
                    self.stdout.write("%s\n"%str(self._help[arg]))
                    return
                try:
                    doc=getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                        pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif cmd in self._help:
                        cmds_doc.append(cmd)
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help.keys(),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)
    def complete_help(self, *args):
        commands = set(self.completenames(*args))
        topics = set(a[5:] for a in self.get_names()
            if a.startswith('help_' + args[0]))
        return list((commands | topics) ^ set([a for a in self.pseudo if a.startswith(args[0])]))
    def do_infobot(self, line):
        """Info : Get information of the bot
        """
        robot.info()
    def complete_infobot(self, *ignored):
        pass
    def do_lastkick(self, line):
        """Info : Get information about the last kick save, if it' possible
        """
        robot.get_server()[1].privmsg(robot.get_channel(),'!lastkick')
        robot.fonction(robot.get_server()[1],robot.get_channel(),'!lastkick',robot.get_name())
    def complete_lastkick(self, *ignored):
        pass
    def do_connect(self, line):
        """Info : give information about who is connect in IRC
        """
        robot.get_server()[1].privmsg(robot.get_name(),'!whois connect')
    def complete_connect(self, *ignored):
        pass
    def do_robot(self, line):
        """Params : <message>
        Info : robot do <message> in IRC
        """
        robot.get_server()[1].action(robot.get_channel(),line)
        stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
        stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+len(line.split(' '))})
        stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+len(line)-line.count(' ')})
    def complete_robot(self, *ignored):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_vdm(self, line):
        """Params : ({1-15})?
        Info : Give one to 15 VDM, fonction is protect
        """
        robot.get_server()[1].privmsg(robot.get_channel(),line)
        robot.fonction(robot.get_server()[1],robot.get_channel(),line,robot.get_name())
    def complete_vdm(self, *ignored):
        pass
    def do_dtc(self, line):
        """Params : ({1-26})?
        Info : Give one to 26 DTC, fonction is protect
        """
        robot.get_server()[1].privmsg(robot.get_channel(),line)
        robot.fonction(robot.get_server()[1],robot.get_channel(),line,robot.get_name())
    def complete_dtc(self, *ignored):
        pass
    def do_cronvdm(self, line):
        """Params : [on|off|next]
        Info : Active/Unactive programmed VDM, if cronvdm active "next" give time from
            if none give status
        """
        if line == '':
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Cronvdm is '+('off','on')[not cronvdm.stop]
        elif line == 'next':
            test = cronvdm._iter.get_prev(datetime)
            in_time = dateutil.parser.parse(cronvdm._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
        elif line.split(' ')[0] in ['on','off'] and len(line.split(' ')) == 1:
            if ('off','on')[not cronvdm.stop] == line.split(' ')[0]:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Cronvdm is already '+('off','on')[not cronvdm.stop]
            else:
                cronvdm.stop = (True,False)[line.split(' ')[0] == 'on']
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Cronvdm is '+('off','on')[not cronvdm.stop]
        elif cronvdm and len(line.split(' ')) == 1 or len(line.split(' ')) == 5:
            try:
                cronvdm._iter = croniter(line.split(' ',1)[0],datetime.now())
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> New cronvdm value is :',line.split(' ',1)[0]
            except:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Impossible option for !cronvdm'
        elif len(line.split(' ')) == 1 or len(line.split(' ')) == 5:
            try:
                test = croniter(line.split(' ',1)[0], datetime.now())
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Cronvdm is already off'
            except:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Impossible option for !cronvdm'
        else:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Unkown option for !cronvdm'
    def complete_cronvdm(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off','next']
                if address.startswith(text)
            ]
        else:
            return ['on','off','next']
    def do_crondtc(self, line):
        """Params : [on|off|next]
        Info : Active/Unactive programmed DTC, if cronvdm active "next" give time from
            if none give status
        """
        if line == '':
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Crondtc is '+('off','on')[not crondtc.stop]
        elif line == 'next':
            test = crondtc._iter.get_prev(datetime)
            in_time = dateutil.parser.parse(crondtc._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
        elif line.split(' ')[0] in ['on','off'] and len(line.split(' ')) == 1:
            if ('off','on')[not crondtc.stop] == line.split(' ')[0]:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Crondtc is already '+('off','on')[not crondtc.stop]
            else:
                crondtc.stop = (True,False)[line.split(' ')[0] == 'on']
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Crondtc is '+('off','on')[not crondtc.stop]
        elif crondtc and len(line.split(' ')) == 1 or len(line.split(' ')) == 5:
            try:
                crondtc._iter = croniter(line.split(' ',1)[0],datetime.now())
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> New crondtc value is :',line.split(' ',1)[0]
            except:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Impossible option for !crondtc'
        elif len(line.split(' ')) == 1 or len(line.split(' ')) == 5:
            try:
                test = croniter(line.split(' ',1)[0], datetime.now())
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Crondtc is already off'
            except:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Impossible option for !crondtc'
        else:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Unkown option for !crondtc'
    def complete_crondtc(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off','next']
                if address.startswith(text)
            ]
        else:
            return ['on','off','next']
    def do_score(self, line):
        """Params : ( <pseudo>)*
        Info : Give Root-me and Newbie score of each pseudo, if it exist !
        """
        robot.get_server()[1].privmsg(robot.get_channel(),line)
        robot.fonction(robot.get_server()[1],robot.get_channel(),line,robot.get_name())
    def complete_score(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_autohello(self, line):
        """Params : [on|off]
        Info : Give status of autohello or change it
        """
        if line == '':
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Autohello is '+('off','on')[robot.autohello]
        elif line in ['on','off']:
            if ('off','on')[robot.autohello] == line:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Autohello is '+('off','on')[robot.autohello]
            else:
                robot.autohello = (False,True)[line == 'on']
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Autohello is '+('off','on')[robot.autohello]
        else:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Unkown option for !autohello'
    def complete_autohello(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off']
                if address.startswith(text)
            ]
        else:
            return ['on','off']
    def do_fonction(self, line):
        """Params : [on|off]
        Info : Change status of bot's fonctions
        """
        if line == '':
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Fonctions are '+('off','on')[robot.fonctions]
        elif line.split(' ')[0] in ['on','off']:
            if ('off','on')[robot.fonctions] == line.split(' ')[0]:
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Fonctions are '+('off','on')[robot.fonctions]
            else:
                robot.fonctions = (False,True)[line.split(' ')[0] == 'on']
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> Fonctions are',('off','on')[robot.fonctions]
                robot.get_server()[1].privmsg(robot.get_channel(), 'Fonctions are '+('off','on')[robot.fonctions])
        else:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Unkown option for !fonction'
    def complete_fonction(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off']
                if address.startswith(text)
            ]
        else:
            return ['on','off']
    def do_admins(self, line):
        """Info : Give admins list of the bot
        """
        if len(robot.admins) != 0:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+', '.join(robot.admins)+' '+('are','is')[len(robot.admins)==1]+\
                ' admin'+('s','')[len(robot.admins)==1]
        else:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> There is no admin'
    def complete_admins(self, text, line, start_index, end_index):
        pass
    def do_halfadmins(self, line):
        """Info : Give half admins list of the bot
        """
        if len(robot.half_admins) != 0:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+', '.join(robot.half_admins)+' '+('are','is')[len(robot.half_admins)==1]+' halfadmin'+('s','')[len(robot.half_admins)==1]
        else:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> There is no halfadmin'
    def complete_halfadmins(self, text, line, start_index, end_index):
        pass
    def do_stat(self, line):
        """Params : ( <pseudo>)*
        Info : Give stats of pseudo list, if none give yours
        """
        if len(line.split(' ')) == 0:
            line = robot.get_name()
        for _name in line.split(' '):
            if _name != '':
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                    item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
    def complete_stat(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_stats(self, line):
        """Info : Give all stats ! (the list could be long !)
        """
        for _name in stat:
            if _name != '':
                print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                    '\033[0m> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                    item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
    def complete_stats(self, *ignored):
        pass
    def do_status(self, line):
        """Info : Give stats of the channel (equal to !connect but each status is describe)
        """
        if line == '':
            info = robot.channels[robot.get_channel()]
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Information from channel : '+robot.get_channel()+\
                ('Owners connected : '+', '.join(info.owners())+'\n','')[len(info.owners()) == 0]+\
                ('Opers connected : '+', '.join(info.opers())+'\n','')[len(info.opers()) == 0]+\
                ('Admins connected : '+', '.join(info.admins())+'\n','')[len(info.admins()) == 0]+\
                ('Half opers connected : '+', '.join(info.halfops())+'\n','')[len(info.halfops()) == 0]+\
                ('Voiced connected : '+', '.join(info.voiced())+'\n','')[len(info.voiced()) == 0]+\
                ('Users connected : '+', '.join(info.users()),'')[len(info.users()) == 0]
        else:
            for _channel in line.split(' '):
                try:
                    info = robot.channels[_channel]
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> Information from channel : '+_channel+\
                        ('Owners connected : '+', '.join(info.owners())+'\n','')[len(info.owners()) == 0]+\
                        ('Opers connected : '+', '.join(info.opers())+'\n','')[len(info.opers()) == 0]+\
                        ('Admins connected : '+', '.join(info.admins())+'\n','')[len(info.admins()) == 0]+\
                        ('Half opers connected'+', '.join(info.halfops())+'\n','')[len(info.halfops()) == 0]+\
                        ('Voiced connected'+', '.join(info.voiced())+'\n','')[len(info.voiced()) == 0]+\
                        ('Users connected'+', '.join(info.users()),'')[len(info.users()) == 0]
                except:
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> No Info from channel : '+_channel
    def complete_status(self, *ignored):
        pass
    def do_slap(self, line):
        """Params : <pseudo>
        Info : Give a slap to the pseudo you give
        """
        for name in line.split(' '):
            robot.get_server()[1].action(robot.get_channel(),'slaps '+name+' around a bit with a large trout')
            print '\r<\033['+PROMPT['%channel%']+'m'+robot.get_channel()+'\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> *'+robot.get_name()+' slaps '+name+' around a bit with a large trout*'
    def complete_slap(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_admin(self, line):
        """Params : ( <pseudo>)+
        Info : Give admin status for each pseudo
        """
        for name in line.split(' '):
            if name != '':
                robot.admins.append(name)
        if line.replace(' ','') != '':
            robot.get_server()[1].privmsg(robot.get_channel(),'!admin '+line)
            robot.get_server()[1].privmsg(robot.get_channel(),', '.join(line.split(' '))+' '+('are','is')[len(line.split(' '))==1]+\
                ' admin'+('s','')[len(line.split(' '))==1]+' now')
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+', '.join(line.split(' '))+' '+('are','is')[len(line.split(' '))==1]+' admin'+('s','')[len(line.split(' '))==1]+' now'
    def complete_admin(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_halfadmin(self, line):
        """Params : ( <pseudo>)+
        Info : Give half admin status for each pseudo
        """
        for name in line.split(' '):
            if name != '':
                robot.half_admins.append(name)
        if line.replace(' ','') != '':
            robot.get_server()[1].privmsg(robot.get_channel(),'!admin '+line)
            robot.get_server()[1].privmsg(robot.get_channel(),', '.join(line.split(' '))+' '+('are','is')[len(line.split(' '))==1]+\
                ' half admin'+('s','')[len(line.split(' '))==1]+' now')
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+', '.join(line.split(' '))+' '+('are','is')[len(line.split(' '))==1]+' half admin'+('s','')[len(line.split(' '))==1]+' now'
    def complete_halfadmin(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_unadmin(self, line):
        """Params : ( <pseudo>)+
        Info : Take admin and half admin status for each pseudo
        """
        temp_A = []
        temp_H = []
        for name in line.split(' '):
            if name in robot.admins:
                robot.admins.remove(name)
                temp_A.append(name)
            if name in robot.half_admins:
                robot.half_admins.remove(name)
                temp_H.append(name)
        if len(temp_A) != 0:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+', '.join(temp_A)+' '+('are','is')[len(temp_A)==1]+' not admin'+('s','')[len(temp_A)==1]+' now'
        if len(temp_H) != 0:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+', '.join(temp_H)+' '+('are','is')[len(temp_H)==1]+' not half admin'+('s','')[len(temp_H)==1]+' now'
    def complete_unadmin(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_topic(self, line):
        """
        topic
        Info : Get the current topic
        """
        try:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> '+robot.topic
        except:
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> There is no topic in this channel !'
    def complete_topic(self, *ignored):
        pass
    def do_topurl(self, line):
        """Params : < pseudo>*
        Info : Give top 5 of url, if no pseudo it's global top
        """
        nb_url = 5
        robot.get_server()[1].privmsg(robot.get_channel(),'!topurl '+line)
        if len(line.replace(' ','')) == 0:
            robot.get_server()[1].privmsg(robot.get_channel(), 'Global top url :')
            for item in robot.all_url[:nb_url]:
                robot.get_server()[1].privmsg(robot.get_channel(), item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+'last hit the '\
                    +item[2][:-3].replace('T',' at '))
            print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                '\033[0m> Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+\
                'last hit the '+item[2][:-3].replace('T',' at ') for item in robot.all_url[:nb_url]])
        else:
            for _name in line.split(' '):
                try:
                    robot.get_server()[1].privmsg(robot.get_channel(), _name+' top url :')
                    for item in stat[_name]['urls'][:nb_url]:
                        robot.get_server()[1].privmsg(robot.get_channel(), item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+\
                            'last hit the '+item[2][:-3].replace('T',' at '))
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> '+_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+\
                        'last hit the '+item[2][:-3].replace('T',' at ') for item in stat[_name]['urls'][:nb_url]])
                except:
                    robot.get_server()[1].privmsg(robot.get_channel(),'No stat for '+_name)
                    print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
                        '\033[0m> No stat for '+_name
    def complete_topurl(self, line):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_lastpast(self, line):
        nb_past = 3
        if len(line.split(' ')) == 1:
            try:
                nb_past = max(3,min(int(line),10))
            except:
                nb_past = 3
        print '\r<\033['+PROMPT['%host%']+'mHost\033[0m,\033['+PROMPT['%time%']+'m'+datetime.now().time().isoformat().split('.')[0]+\
            '\033[0m> Last pastbin :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times, ','')[item[1] == 1]+'last hit the '+\
            item[2][:-3].replace('T',' at ') for item in robot.all_url if re.match('(?:http[s]?|ftp)://\w+bin(?:[.]\w+)+(?:[/].*)?', item[0])][:nb_paste])
        robot.get_server()[1].privmsg(robot.get_channel(), 'Last pastbin :')
        time.sleep(0.3)
        past_liste = [item for item in robot.all_url if re.match('(?:http[s]?|ftp)://\w+bin(?:[.]\w+)+(?:[/].*)?', item[0])][:nb_paste]
        for item in past_liste:
            time.sleep(0.3)
            robot.get_server()[1].privmsg(robot.get_channel(), item[0]+', last hit the '+item[2][:-3].replace('T',' at '))
    def complete_lastpast(self, *ignored):
        pass
    def do_change(self, line):
        """Params : <channel>
        Info : change the channel of the bot to the given one
        """
        robot.get_server()[1].disconnect('leave')
        robot.get_server()[1].join(line)        
    def complete_change(self, *ignored):
        pass
    def do_history(self, line):
        """        Params : [<line>]
        Info : Give list of issued commands, line give if possible the line in the history else all commands
        """
        if not line:
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history])
        elif (line.isdigit() or (line[1:].isdigit() and line[0] in '+-')) and abs(int(line)) <= len(self.history) and line != '0':
            print '-----------------['+(str(int(line)),str(len(self.history)+int(line)+1))[int(line) < 0]+']\n'+\
                self.history[(int(line)-1,len(self.history)+int(line))[int(line) < 0]]
        elif line[0] == '/':
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history if self.history[item].endswith(line[1:])])
        elif line[-1] == '/':
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history if line in self.history[item].startswith(line[:-1])])
        else:
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history if line in self.history[item]])
    def complete_history(self, *args):
        pass

def main():
    try:
        if __name__ == "__main__":
            print """"You main direct run has : python bot_local.py [options]"""
        # Threads 
        thread_1 = lancheur("bot")
        thread_2 = lancheur("client")
        
        # Lanch !
        thread_1.start()
        thread_2.start()
        #cronvdm.start()
        #crondtc.start()
        
        # Waitting for end !
        #thread_1.join()
        thread_2.join()
    except:
        print 'End program !'
        sys.exit(0)

if set([argv in ['setup.py', 'install'] for argv in sys.argv]) != set([True]):
    ESC = Literal('\x1b')
    integer = Word(nums)
    escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer,';')) + oneOf(list(alphas)))
    
    UncolorString = lambda s : Suppress(escapeSeq).transformString(s)
    robot=Robot()
    try:
        _file = open('stat.txt','r+')
        text = _file.read()
        _file.close()
        if '\n[]\n' in text:
            text = text.replace('[]', '').replace('\n\n\n','\n')
            with open('stat.txt', 'w') as outfile:
                for item in text.split('\n'):
                    outfile.write(item+'\n')
        stat= {}
        stats = ['words','letters','messages']
        config = ConfigParser.ConfigParser()
        config.readfp(io.BytesIO(text))
        def num(s):
            try:
                return int(s)
            except ValueError:
                return s
        urls = re.compile("(?:[[]('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', [0-9]+, "+\
            "'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}')[]])")
        for section in config.sections():
            stat.update({section:{}})
            for value in stats:
                stat[section].update({value:int(config.get(section,value))})
            stat[section].update({'urls':[[num(item) for item in element.replace("'",'').split(', ')] for element in urls.findall(config.get(section,'urls'))]})
        print '\033[1;32mStats have been found !\033[0m'
    except IOError:
        print '\033[1;33mNo stats found !\033[0m'
        stat= {}
        text="""[DEFAULT]
        words = 0
        letters = 0
        messages = 0
        urls = []
        all_url = []"""
        config = ConfigParser.ConfigParser()
        config.readfp(io.BytesIO(text))
    cronvdm = lancheur('cronvdm')
    cronvdm._iter = croniter('0 * * * *', datetime.now())
    crondtc = lancheur('crondtc')
    crondtc._iter = croniter('0 * * * *', datetime.now())
    my_cmd = MyCmd()
    PROMPT = {'%private%': '0;31', '%host%': '0;31', '%pseudo%': '0;32', '%channel%': '0;34', '%pseudo_private%': '0;32', '%time%': '0;32','%pseudo_other%':'0;33'}

if __name__ == "__main__":
    __name__ = "__lanched__"
    if '-h' in sys.argv or '--help' in sys.argv:
        print '''usage : python '''+os.path.basename(__file__)+''' [OPTIONS]
        -n : Use to change default bot's Name
        -p : Use a Password, not by default
        -c : Use to change default bot's Channel 
        -s : Use to change default bot's Server
        --ssl [True|False] : Use to activate or not ssl
        --port <server_port> : Int require to change server port
        --prompt : Change color and format of tags in prompt
            example : "\\033[0;34m%host%\\033[0m"
                %host% in red
                %time% in green
                %channel% in blue
                %private% in red
                %pseudo% in green
                %pseudo_private% in green
                %pseudo_other% in yellow'''
        sys.exit(0)
    args = list(set([sys.argv.count(item) for item in sys.argv if item in ['-n','-s','-c','-p','--prompt','--ssl','--port']]))
    if not (args == [1] or args == [] ):
        print '\033[0;33mError during ARGUMENTS processing : InvalidFormat, Duplicate options !\033[0m'
        sys.exit(0)
    name = ''
    if '-n' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-n') > 0:
        name = sys.argv[sys.argv.index('-n')+1]
    server = ''
    if '-s' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-s') > 0:
        server =  sys.argv[sys.argv.index('-s')+1]
    channel = ''
    if '-c' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-c') > 0:
        channel = sys.argv[sys.argv.index('-c')+1]
    password = ''
    if '-p' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-p') > 0:
        password = sys.argv[sys.argv.index('-p')+1]
    if '--prompt' in sys.argv and (len(sys.argv)-1)-sys.argv.index('--prompt') > 0:
        add = re.findall('\\033[[]((?:(?:[0-9]|2[1-3]|[3-49][0-7])?;)*(?:[0-9]|2[1-3]|[3-49][0-7])?)m(%(?:host|time|channel|private|pseudo(?:|_private|_other))%)\\033[[]0?m',\
            sys.argv[sys.argv.index('--prompt')+1])
        if add != []:
            PROMPT = {item[1]:item[0] for item in [('1;31', '%host%'), ('1;32', '%time%'), ('1;34', '%channel%'),\
                ('0;31', '%private%'), ('1;32', '%pseudo%'), ('1;32', '%pseudo_private%'), ('1;33','%pseudo_other%')]+add}
        else:
            print '\033[0;33mError during PROMPT processing : InvalidFormat !\033[0m'
            print '\t'+sys.argv[sys.argv.index('--prompt')+1]
            sys.exit(0)
    else:
        PROMPT = {'%private%': '0;31', '%host%': '0;31', '%pseudo%': '0;32', '%channel%': '0;34', '%pseudo_private%': '0;32', '%time%': '0;32','%pseudo_other%':'0;33'}
    ssl = ''
    if '--ssl' in sys.argv and (len(sys.argv)-1)-sys.argv.index('--ssl') > 0:
        if sys.argv[sys.argv.index('--ssl')+1] in ['True','False']:
            ssl = (True,False)[sys.argv[sys.argv.index('--ssl')+1] == 'False']
        else:
            print '\033[0;33mError during SSL processing : InvalidFormat !\033[0m'
            print '\t'+sys.argv[sys.argv.index('--ssl')+1]
            sys.exit(0)
    server_port = ''
    if '--port' in sys.argv and (len(sys.argv)-1)-sys.argv.index('--port') > 0:
        if sys.argv[sys.argv.index('--port')+1].isdigit():
            server_port = int(sys.argv[sys.argv.index('--port')+1])
        else:
            print '\033[0;33mError during PORT processing : InvalidFormat !\033[0m'
            print '\t'+sys.argv[sys.argv.index('--port')+1]
    #import itertools
    #def auto_craft():
    #    #It could help a lot if you would build with more options
    #    l = ['name','channel','server','password','ssl','server_port']
    #    a = [list(itertools.combinations(l,i)) for i in range(1,len(l)+1)]
    #    b = []
    #    for c in a:
    #        b+= c
    #    a = b[::-1]
    #    print '    if '+" != '' and ".join(a[0])+" != '':"
    #    print '        robot = Robot('+','.join(a[0])+')'
    #    print "        print ('\\033[1;33mrobot get",
    #    if len(a[0]) > 1:
    #        for b,c in zip(a[0][:-2],a[0][:-2]):
    #            print b+" ('+"+c+"+'),",
    #        print a[0][-2]+" ('+"+a[0][-2]+"+') and "+a[0][-1]+" ('+"+a[0][-1]+"+')!\\033[0m')"
    #    else :
    #        print "a "+a[0][0]+" ('+"+a[0][0]+"+')"
    #    for item in a[1:]:
    #        print '    elif '+" != '' and ".join(item)+" != '':"
    #        print '        robot = Robot('+','.join(item)+')'
    #        print "        print ('\\033[1;33mrobot get",
    #        if len(item) > 1:
    #            for b,c in zip(item[:-2],item[:-2]):
    #                print b+" ('+"+c+"+'),",
    #            print item[-2]+" ('+"+item[-2]+"+') and "+item[-1]+" ('+"+item[-1]+"+')!\\033[0m')"
    #        else :
    #            print "a "+item[0]+" ('+"+item[0]+"+')\\033[0m')"
    #    print """    else:
    #        robot = Robot()
    #        print '\\033[1;33mrobot has default value !\\033[0m'"""
    if name != '' and channel != '' and server != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(name,channel,server,password,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and server != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(channel,server,password,ssl,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and server != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(name,server,password,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(name,channel,password,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and server != '' and ssl != '' and server_port != '':
        robot = Robot(name,channel,server,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and server != '' and password != '' and server_port != '':
        robot = Robot(name,channel,server,password,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and server != '' and password != '' and ssl != '':
        robot = Robot(name,channel,server,password,ssl)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif server != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(server,password,ssl,server_port)
        print ('\033[1;33mrobot get server ('+server+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(channel,password,ssl,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and server != '' and ssl != '' and server_port != '':
        robot = Robot(channel,server,ssl,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and server != '' and password != '' and server_port != '':
        robot = Robot(channel,server,password,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and server != '' and password != '' and ssl != '':
        robot = Robot(channel,server,password,ssl)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and password != '' and ssl != '' and server_port != '':
        robot = Robot(name,password,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and server != '' and ssl != '' and server_port != '':
        robot = Robot(name,server,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and server != '' and password != '' and server_port != '':
        robot = Robot(name,server,password,server_port)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and server != '' and password != '' and ssl != '':
        robot = Robot(name,server,password,ssl)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and channel != '' and ssl != '' and server_port != '':
        robot = Robot(name,channel,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and password != '' and server_port != '':
        robot = Robot(name,channel,password,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and password != '' and ssl != '':
        robot = Robot(name,channel,password,ssl)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and channel != '' and server != '' and server_port != '':
        robot = Robot(name,channel,server,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and server != '' and ssl != '':
        robot = Robot(name,channel,server,ssl)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and channel != '' and server != '' and password != '':
        robot = Robot(name,channel,server,password)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+'), server ('+server+') and password ('+password+')!\033[0m')
    elif password != '' and ssl != '' and server_port != '':
        robot = Robot(password,ssl,server_port)
        print ('\033[1;33mrobot get password ('+password+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif server != '' and ssl != '' and server_port != '':
        robot = Robot(server,ssl,server_port)
        print ('\033[1;33mrobot get server ('+server+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif server != '' and password != '' and server_port != '':
        robot = Robot(server,password,server_port)
        print ('\033[1;33mrobot get server ('+server+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif server != '' and password != '' and ssl != '':
        robot = Robot(server,password,ssl)
        print ('\033[1;33mrobot get server ('+server+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif channel != '' and ssl != '' and server_port != '':
        robot = Robot(channel,ssl,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and password != '' and server_port != '':
        robot = Robot(channel,password,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and password != '' and ssl != '':
        robot = Robot(channel,password,ssl)
        print ('\033[1;33mrobot get channel ('+channel+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif channel != '' and server != '' and server_port != '':
        robot = Robot(channel,server,server_port)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and server != '' and ssl != '':
        robot = Robot(channel,server,ssl)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+') and ssl ('+ssl+')!\033[0m')
    elif channel != '' and server != '' and password != '':
        robot = Robot(channel,server,password)
        print ('\033[1;33mrobot get channel ('+channel+'), server ('+server+') and password ('+password+')!\033[0m')
    elif name != '' and ssl != '' and server_port != '':
        robot = Robot(name,ssl,server_port)
        print ('\033[1;33mrobot get name ('+name+'), ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and password != '' and server_port != '':
        robot = Robot(name,password,server_port)
        print ('\033[1;33mrobot get name ('+name+'), password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and password != '' and ssl != '':
        robot = Robot(name,password,ssl)
        print ('\033[1;33mrobot get name ('+name+'), password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and server != '' and server_port != '':
        robot = Robot(name,server,server_port)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and server != '' and ssl != '':
        robot = Robot(name,server,ssl)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and server != '' and password != '':
        robot = Robot(name,server,password)
        print ('\033[1;33mrobot get name ('+name+'), server ('+server+') and password ('+password+')!\033[0m')
    elif name != '' and channel != '' and server_port != '':
        robot = Robot(name,channel,server_port)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and channel != '' and ssl != '':
        robot = Robot(name,channel,ssl)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and channel != '' and password != '':
        robot = Robot(name,channel,password)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+') and password ('+password+')!\033[0m')
    elif name != '' and channel != '' and server != '':
        robot = Robot(name,channel,server)
        print ('\033[1;33mrobot get name ('+name+'), channel ('+channel+') and server ('+server+')!\033[0m')
    elif ssl != '' and server_port != '':
        robot = Robot(ssl,server_port)
        print ('\033[1;33mrobot get ssl ('+ssl+') and server_port ('+server_port+')!\033[0m')
    elif password != '' and server_port != '':
        robot = Robot(password,server_port)
        print ('\033[1;33mrobot get password ('+password+') and server_port ('+server_port+')!\033[0m')
    elif password != '' and ssl != '':
        robot = Robot(password,ssl)
        print ('\033[1;33mrobot get password ('+password+') and ssl ('+ssl+')!\033[0m')
    elif server != '' and server_port != '':
        robot = Robot(server,server_port)
        print ('\033[1;33mrobot get server ('+server+') and server_port ('+server_port+')!\033[0m')
    elif server != '' and ssl != '':
        robot = Robot(server,ssl)
        print ('\033[1;33mrobot get server ('+server+') and ssl ('+ssl+')!\033[0m')
    elif server != '' and password != '':
        robot = Robot(server,password)
        print ('\033[1;33mrobot get server ('+server+') and password ('+password+')!\033[0m')
    elif channel != '' and server_port != '':
        robot = Robot(channel,server_port)
        print ('\033[1;33mrobot get channel ('+channel+') and server_port ('+server_port+')!\033[0m')
    elif channel != '' and ssl != '':
        robot = Robot(channel,ssl)
        print ('\033[1;33mrobot get channel ('+channel+') and ssl ('+ssl+')!\033[0m')
    elif channel != '' and password != '':
        robot = Robot(channel,password)
        print ('\033[1;33mrobot get channel ('+channel+') and password ('+password+')!\033[0m')
    elif channel != '' and server != '':
        robot = Robot(channel,server)
        print ('\033[1;33mrobot get channel ('+channel+') and server ('+server+')!\033[0m')
    elif name != '' and server_port != '':
        robot = Robot(name,server_port)
        print ('\033[1;33mrobot get name ('+name+') and server_port ('+server_port+')!\033[0m')
    elif name != '' and ssl != '':
        robot = Robot(name,ssl)
        print ('\033[1;33mrobot get name ('+name+') and ssl ('+ssl+')!\033[0m')
    elif name != '' and password != '':
        robot = Robot(name,password)
        print ('\033[1;33mrobot get name ('+name+') and password ('+password+')!\033[0m')
    elif name != '' and server != '':
        robot = Robot(name,server)
        print ('\033[1;33mrobot get name ('+name+') and server ('+server+')!\033[0m')
    elif name != '' and channel != '':
        robot = Robot(name,channel)
        print ('\033[1;33mrobot get name ('+name+') and channel ('+channel+')!\033[0m')
    elif server_port != '':
        robot = Robot(server_port)
        print ('\033[1;33mrobot get a server_port ('+server_port+')!\033[0m')
    elif ssl != '':
        robot = Robot(ssl)
        print ('\033[1;33mrobot get a ssl ('+ssl+')!\033[0m')
    elif password != '':
        robot = Robot(password)
        print ('\033[1;33mrobot get a password ('+'*'*len(password)+')!\033[0m')
    elif server != '':
        robot = Robot(server)
        print ('\033[1;33mrobot get a server ('+server+')!\033[0m')
    elif channel != '':
        robot = Robot(channel)
        print ('\033[1;33mrobot get a channel ('+channel+')!\033[0m')
    elif name != '':
        robot = Robot(name)
        print ('\033[1;33mrobot get a name ('+name+')!\033[0m')
    else:
        robot = Robot()
        print '\033[1;33mrobot has default value !\033[0m'
    if config.defaults().has_key('time_stop'):
        robot.last_stop = dateutil.parser.parse(config.defaults()['time_stop'])
        print 'Last stop :', str(robot.last_stop)
    if config.defaults().has_key('all_url'):
        robot.all_url = [[num(item) for item in element.replace("'",'').split(', ')] for element in urls.findall(config.get('DEFAULT','all_url'))]
    else:
        config.set('DEFAULT','all_url','[]')
        robot.all_url = []
    main()
#EOF
