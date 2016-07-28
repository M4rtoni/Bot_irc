#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, select, base64, os, random, md5, sys, re, requests, ConfigParser, io

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

###
# Add your lib for encryption (more secure)
###

class Robot(ircbot.SingleServerIRCBot):
    def __init__(self, name = 'Bot', channel = '#Channel', server = 'irc.wroldnet.net', password = None, port = 7000, ssl =True):
        self.__name = name
        self.__channel = channel
        self.__server = server
        self.__port = port
        self.__connected = False
        self.away = False
        self.away_message = ''
        self.fonctions = False
        self.autohello = False
        self.wake_up = datetime.now()
        self.last_stop = datetime.now()
        self.admins = []
        self.half_admins = []
        self.superadmins = []
        self.lastkick = ['','','','']
        self.history = []
        self.end = False
        self.try_quit = False
        self.fonction_list = ['!md5','!help','!decodeb64','!encodeb64','!vdm','!dtc','!score']
        self.fonction_list_admin = ['!stat','!fonction','!stats','!admin','!halfadmin','!unhalfadmin','!order66','!cronvdm','!crondtc','!away','!info','!tu','!topurl']
        self.__url = re.compile('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], name, "Bot build with ircbot",password=password, ssl=ssl)
    def on_welcome(self, serv, ev):
        serv.join(self.__channel)
        self.__serv = serv
        print '\033[1;32mBot is now connect to',self.__server,'!\033[0m'
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, '\rBot is now connect to '+self.__server+' !\n')

    def on_join(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        channel = ev.target()
        if author != self.__name:
            info = self.channels[self.__channel]
            print ('\033[1;32m<'+channel+'> '+self.__user_mode(author)+author),'est entré !\033[0m'
            if len(pseudo_list) != 0:
                broadcast_data(server_socket, '\r<'+channel+'> '+self.__user_mode(author)+author+' enter !\n')
            if not name in stat.keys():
                stat.update({name:{item:0 for item in stats}})
                stat[author].update({'urls':[]})
                config.add_section(name)
                for item in stats:
                    config.set(name,item,0)
                config.set(name,'urls','[]')
        else:
            self.__connected = True
            print '\033[1;32mJoin',self.__channel,'on',self.__server,'\033[0m'
            if len(pseudo_list) != 0:
                broadcast_data(server_socket, '\rJoin '+self.__channel+' on '+self.__server+' !\n')
    def on_pubmsg(self, serv, ev):
        message = ev.arguments()[0]
        author = irclib.nm_to_n(ev.source())
        channel = ev.target()
        info = self.channels[ev.target()]
        print self.__user_mode(author)+author, ':', channel, ':', message, [':'+str(ev.arguments()[1:]),''][len(ev.arguments()) == 1]
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
        urls = self.__url.findall(message)
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
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, '\r<'+self.__user_mode(author)+author+','+channel+'> '+message+'\n')
        self.fonction(serv, channel, message, author)
    def on_privmsg(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        if self.channels.__contains__(self.__channel):
            info = self.channels[self.__channel]
        time = datetime.now().time().isoformat().split('.')[0][:-3]
        if message != '!quit' and author != self.__name:
            print author, ': private :', message, [':'+str(ev.arguments()[1:]),''][len(ev.arguments()) == 1]
        if len(pseudo_list) != 0:
            if author in self.superadmins+self.admins and author != self.__name:
                broadcast_data(server_socket, '\r<'+author+',private> '+message+'\n')
            elif author == self.__name:
                if message.split(' ')[0] == '!quit':
                    if len(message.split(' ')) > 1:
                        serv.disconnect(message.split(' ',1)[1])
                    else :
                        serv.disconnect()
                    sys.exit()
                elif message == '!whois connect' and self.channels.__contains__(self.__channel):
                    print '<Host> '+(', '.join(['%s%s' % (self.__user_mode(aut),aut) for aut in info.users()])+\
                        ' are on line !','Only you are on line !')[len(info.users()) <= 1]
                    broadcast_data(server_socket, '\r<Host> '+(', '.join(['%s%s' % (self.__user_mode(aut),aut)\
                        for aut in info.users()])+' are on line !\n','Only you are on line !\n')[len(info.users()) <= 1])
                elif message.split(' ')[0] == '!kickirc' and self.channels.__contains__(self.__channel) and not self.__user_mode(self.__name) in ['','%','+']:
                    for name in message.split(' ')[1:]:
                        if name in info.users() and not info.is_owner(name) and not info.is_admin(name):
                            serv.kick(self.__channel,name,'No raison I\'m a bot !')
                        else:
                            broadcast_data(server_socket, '\r<Host> Command refuse for '+name+' !\n')
                elif message.split(' ')[0] == '!kickirc' and self.channels.__contains__(self.__channel):
                    broadcast_data(server_socket, '\r<Host> Command refuse the bot is unright !\n')
            elif self.away:
                serv.privmsg(author,'Sorry, I\'m away for now'+(' ('+self.away_message+')','')[len(self.away_message)==0])
                broadcast_data(server_socket, '\r<'+author+',private> '+message+'\n')
            else:
                broadcast_data(server_socket, '\r<'+author+',private> '+message+'\n')
            self.fonction(serv, author, message, author)
        else:
            if author in self.superadmins+[self.__name]+self.admins:
                if message ==	'!stat' and author == self.__name:
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
                elif message.split(' ')[0] in self.fonction_list+self.fonction_list_admin:
                    self.fonction(serv, author, message, author)
                elif author != self.__name:
                    print '\033[1;33mCommand not understood by the bot !\033[0m',('('+message+')')
                    serv.privmsg(author,'Yes master, but I don\'t understand what you tell me !')
            else:
                print 'Bot auto response : no admin to get response !'
                serv.privmsg(author,'Sorry, I\'m bot and your are not my admin ! I can\'t do anything for you')
    def on_kick(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        self.lastkick = [message,ev.arguments()[1],datetime.now().isoformat()[:-7],author]
        print ('\033[1;32m'+self.__user_mode(author)+author),'kick',message,'from',channel,'!',\
            ('','('+ev.arguments()[1]+')')[len(ev.arguments()) > 1],'\033[0m'
        if message == self.__name:
            serv.join(channel)
            broadcast_data(server_socket, '\rBot has been kicked from '+channel+' and reconnect !\n')
            print '\033[1;32mBot has been kicked from',channel,' and reconnect !\033[0m'
            if len(pseudo_list) == 0:
                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') Bot has been kicked from '+channel+' and reconnect !\n')
        elif len(pseudo_list) != 0:
            broadcast_data(server_socket, '\r'+self.__user_mode(author)+author+' kick '+self.__user_mode(message)+message+' from '+channel+('',' ('+ev.arguments()[1]+')')[len(ev.arguments()) > 1]+' !\n')
    def on_part(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        if message != []:
            print '\033[1;32m'+self.__user_mode(author)+author,('has left ! ('+' '.join(message)+')\033[0m')
            if len(pseudo_list) == 0:
                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') '+self.__user_mode(author)+author+' has left ! ('+' '.join(message)+')\n')
            broadcast_data(server_socket, '\r'+self.__user_mode(author)+author+' has left ! ('+' '.join(message)+')\n')
        else:
            print ('\033[1;32m'+self.__user_mode(author)+author),'has left !\033[0m'
            if len(pseudo_list) != 0:
                broadcast_data(server_socket, '\r'+self.__user_mode(author)+author+' has left !\n')
            else:
                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') '+self.__user_mode(author)+author+' has left !\n')
    def on_quit(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        if message != []:
            print '\033[1;32m'+self.__user_mode(author)+author,('has left ! ('+' '.join(message)+')\033[0m')
            if len(pseudo_list) == 0:
                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') '+self.__user_mode(author)+author+' has left ! ('+' '.join(message)+')\n')
            broadcast_data(server_socket, '\r'+self.__user_mode(author)+author+' has left ! ('+' '.join(message)+')\n')
        else:
            print ('\033[1;32m'+self.__user_mode(author)+author),'has left !\033[0m'
            if len(pseudo_list) != 0:
                broadcast_data(server_socket, '\r'+self.__user_mode(author)+author+' has left !\n')
            else:
                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') '+self.__user_mode(author)+author+' has left !\n')
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
        print '\033[1;32m<'+self.__channel+'> '+self.__user_mode(author)+author,'has rename in',channel,'\033[0m'
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, '\r<'+self.__channel+'> '+self.__user_mode(author)+author+' has rename in '+channel+'\n')
        if not channel in stat.keys():
            stat.update({channel:{item:0 for item in stats}})
            config.add_section(channel)
            for item in stats:
                config.set(channel,item,0)
            config.set(author,'urls','[]')
    def on_action(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        print ('<'+channel+'> : *'+self.__user_mode(author)+author+' '+' '.join(message)+'*')
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
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, '\r<'+channel+'> *'+self.__user_mode(author)+author+' '+' '.join(message)+'*\n')
        else:
            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+channel+'> *'+self.__user_mode(author)+author+' '+' '.join(message)+'*\n')
    def on_mode(self, serv, ev):
        channel = ev.target()
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()
        info = self.channels[ev.target()]
        liste_spe= 'inpstmclkSR'
        if True in [item in liste_spe for item in message[0]] and False:
            for item in range(len(message[0])):
                if not item in '+-':
                    tp = 0
                    while not message[0][item-tp] in '+-':
                        tp += 1
                    serv.mode(channel,('-','+')[message[0][item-tp] == '-']+message[0][item])
        print ('\033[1;33m<'+channel+'> '+self.__user_mode(author)+author+' change mode : '+' '.join(message)+'\033[0m')
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, '\r<'+channel+'> '+self.__user_mode(author)+author+' change mode : '+' '.join(message)+'\n')
    def on_currenttopic(self, serv, ev):
        arg = ev.arguments()
        mess = '\r<Host> Current topic on '+str(arg[0])+' : '+str(arg[1])+'\n'
        self.topic = mess
        print mess
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, mess)
    def on_topic(self, serv, ev):
        arg = ev.arguments()
        mess = '\r<Host> New topic on '+str(ev.target())+' by '+irclib.nm_to_n(ev.source())+' : '+str(arg[0])+'\n'
        self.topic = mess
        print mess
        if len(pseudo_list) != 0:
            broadcast_data(server_socket, mess)
    def on_help(self, serv, dest):
        #info = self.channels[self.__canal]
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
    def get_canal(self):
        return self.__canal
    def __user_mode(self, name):
        info = self.channels[self.__canal]
        return ((((('','+')[info.is_voiced(name)],'%')[info.is_halfop(name)],'@')[info.is_oper(name)],\
            '&')[info.is_admin(name)],'~')[info.is_owner(name)]
    def info(self):
        if self.__connected:
            info = self.channels[self.__canal]
            delta = datetime.now() - self.wake_up
            ret = 'Bot name : '+self.__name+'\nConnected on channel :  '+self.__canal+'\nConnected on server : '+self.__server+'\n'+\
                ((((('','Bot is voiced !')[info.is_voiced(name)],'Bot is half oper !')[info.is_halfop(name)],\
                'Bot is oper !')[info.is_oper(name)],'Bot is admin !')[info.is_admin(name)],'Bot is owner !')[info.is_owner(name)]+'\n'+\
                'Bot is awoken for '+('',str(delta.days)+' day'+('s','')[delta.days<1]+' ')[delta.days > 0]+\
                ('',str(delta.seconds/3600)+' hour'+('s','')[delta.seconds/3600 < 1]+' ')[delta.seconds > 3600]+\
                (str(delta.seconds%60)+' seconde'+('s','')[delta.seconds%60 < 1],\
                str((delta.seconds/60)%60)+' minute'+('s','')[(delta.seconds/60)%60 < 1])[delta.seconds > 60]
        else: 
            ret = 'Bot name : '+self.__name+'\nBot is not connected !'
        print ret
        return ret
    def is_connected(self):
        return self.__connected
    def fonction(self, serv, name, message, author):
        info = self.channels[self.__canal]
        if self.fonctions or author in [self.__name]+self.superadmins+self.admins+self.half_admins:
            if message == '!help':
                self.on_help(serv, author)
            elif message == '!lastkick':
                if self.lastkick[0] != '':
                    in_time = dateutil.parser.parse(datetime.now().isoformat()[:-7]) - dateutil.parser.parse(self.lastkick[2])
                    print '<Host> '+self.lastkick[0]+' is the lastkick from '+self.__canal+', he was excluded by '+self.lastkick[3]+\
                        ' for reason : '+self.lastkick[1]+'; '+((str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60)+' hour'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60 in [0,1]]+' '+\
                        (str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 == 0]+\
                        ' ',str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]]+\
                        ' ')[in_time.seconds < 3599],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                        str(in_time.seconds%60)+' seconde'+('s','')[in_time.seconds%60 in [0,1]]+' ago'
                    serv.privmsg(name, self.lastkick[0]+' is the lastkick from '+self.__canal+', he was excluded by '+self.lastkick[3]+\
                        ' for reason : '+self.lastkick[1]+'; '+((str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60)+' hour'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60 in [0,1]]+' '+\
                        (str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 == 0]+\
                        ' ',str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                        ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]]+\
                        ' ')[in_time.seconds < 3599],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                        str(in_time.seconds%60)+' seconde'+('s','')[in_time.seconds%60 in [0,1]]+' ago')
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket, '\r<Host> '+self.lastkick[0]+' is the lastkick from '+self.__canal+', he was excluded by '+self.lastkick[3]+\
                            ' for reason : '+self.lastkick[1]+'; '+((str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60)+' hour'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60 in [0,1]]+' '+\
                            (str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 == 0]+\
                            ' ',str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]]+\
                            ' ')[in_time.seconds < 3599],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(in_time.seconds%60)+' seconde'+('s','')[in_time.seconds%60 in [0,1]]+' ago\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+self.lastkick[0]+' is the lastkick from '+self.__canal+', he was excluded by '+self.lastkick[3]+\
                            ' for reason : '+self.lastkick[1]+'; '+((str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60)+' hour'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]/60 in [0,1]]+' '+\
                            (str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 == 0]+\
                            ' ',str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60)+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0]%60 in [0,1]]+\
                            ' ')[in_time.seconds < 3599],'')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(in_time.seconds%60)+' seconde'+('s','')[in_time.seconds%60 in [0,1]]+' ago\n')
                else:
                    print '<Host> No Kick saved' 
                    serv.privmsg(name, 'No Kick saved')
                    broadcast_data(server_socket, '\r<Host> No Kick saved\n')
            elif message.split(' ')[0] == '!encodeb64' and len(message.split(' ',1)) == 2:
                serv.privmsg(name, base64.b64encode(message.split(' ',1)[1]))
                print '<Host> Result :',base64.b64encode(message.split(' ',1)[1])
                if len(pseudo_list) != 0:
                    broadcast_data(server_socket, '\r<Host> '+base64.b64encode(message.split(' ',1)[1])+'\n')
                else:
                    self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+base64.b64encode(message.split(' ',1)[1])+'\n')
            elif message.split(' ')[0] == '!decodeb64' and len(message.split(' ',1)) == 2:
                try:
                    serv.privmsg(name, base64.b64decode(message.split(' ',1)[1]))
                    print '<Host> Result :',base64.b64decode(message.split(' ',1)[1])
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket, '\r<Host> '+base64.b64decode(message.split(' ',1)[1])+'\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+base64.b64decode(message.split(' ',1)[1])+'\n')
                except:
                    print '\033[1;3Can\'t decode data !\033[0m'
                    serv.privmsg(name, 'Sorry buy I can\'t decode !')
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket, '\r<Host> Sorry buy I can\'t decode it !\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Sorry buy I can\'t décode it !\n')
            elif message.split(' ')[0] == '!md5' and len(message.split(' ',1)) == 2:
                serv.privmsg(name, md5.new(message.split(' ',1)[1]).digest())
                print '<Host> Result :',md5.new(message.split(' ',1)[1]).digest()
                if len(pseudo_list) != 0:
                    broadcast_data(server_socket, '\r<Host> '+md5.new(message.split(' ',1)[1]).digest()+'\n')
                else:
                    self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+md5.new(message.split(' ',1)[1]).digest()+'\n')
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
                        print '<Host> Result :',result[rdm]
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<Host> '+result[rdm]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+result[rdm]+'\n')
                else:
                    serv.privmsg(name, 'Impossible to contact : VDM ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')')
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket, '\r<Host> Impossible to contact : VDM ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Impossible to contact : VDM ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')\n')
                    print '<Host> Impossible to contact : VDM ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')'
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
                        print '<Host> Result :',result[rdm]
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<Host> '+result[rdm]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+result[rdm]+'\n')
                else:
                    serv.privmsg(name, 'Impossible to contact : DTC ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')')
                    if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<Host> Impossible to contact : DTC ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Impossible to contact : DTC ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')\n')
                    print '<Host> Impossible to contact : DTC ('+page.content.split('<html><body><h1>')[1].split('</h1>')[0]+')'
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
                                    print ('<Host> '+p.findall(item)[0][1]+' have '+temp[0]+' point'+('s','')[temp[0] == 0]+', he resolved '+temp[1]+' of the '+temp[2]+\
                                        ' challenge'+('s','')[temp[2] == 0]+', he\'s ranked at '+temp[3]+' out of '+temp[4]+' players ('+temp[5]+') in Root-me')
                                    serv.privmsg(name, p.findall(item)[0][1]+' have '+temp[0]+' point'+('s','')[temp[0] == 0]+', he resolved '+temp[1]+' of the '+temp[2]+\
                                        ' challenge'+('s','')[temp[2] == 0]+', he\'s ranked at '+temp[3]+' out of '+temp[4]+' players ('+temp[5]+') in Root-me')
                                    if len(pseudo_list) != 0:
                                        broadcast_data(server_socket, '\r<'+name+'> '+p.findall(item)[0][1]+' have '+temp[0]+' point'+('s','')[temp[0] == 0]+', he resolved '+\
                                            temp[1]+' of the '+temp[2]+' challenge'+('s','')[temp[2] == 0]+', he\'s ranked at '+temp[3]+' out of '+temp[4]+' players ('+temp[5]+') in Root-me'+'\n')
                                    else:
                                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+name+'> '+p.findall(item)[0][1]+' have '+temp[0]+' point'+('s','')[temp[0] == 0]+', he resolved '+\
                                            temp[1]+' of the '+temp[2]+' challenge'+('s','')[temp[2] == 0]+', he\'s ranked at '+temp[3]+' out of '+temp[4]+' players ('+temp[5]+') in Root-me'+'\n')
                                    
                            except:
                                print 'no such result in Root-me for',_name
                                serv.privmsg(name,'no such result in Root-me for '+_name)
                                if len(pseudo_list) != 0:
                                    broadcast_data(server_socket, '\r<'+name+'> no such result in Root-me for '+_name+'\n')
                                else:
                                    self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+name+'> no such result in Root-me for '+_name+'\n')
                                break
                    else:
                        print 'no such result in Root-me for',_name
                        serv.privmsg(name,'no such result in Root-me for '+_name)
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<'+name+'> no such result in Root-me for '+_name+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+name+'> no such result in Root-me for '+_name+'\n')
                    page=requests.get('https://www.newbiecontest.org/index.php?page=classementdynamique&limit=0&member='+_name+'&nosmiley=0')
                    if 'Recherche de '+_name+' :' in page.content:
                        p = re.compile('<p class=".*">(.*) : ?</span> (([0-9]+/[0-9]+)</span>.*|(.*))</p>')
                        page=requests.get('https://www.newbiecontest.org/index.php?page=info_membre&amp;id='+page.content.split('Recherche de '+_name+' :')[1].split('<a href="index.php?page=info_membre&amp;id=')[1].split('"')[0])
                        value = p.findall(page.content.split('<div class="memberInfos">')[1].split('</div>')[0]+\
                            page.content.split('<h3>Challenges :</h3>')[1].split('<p>')[0])
                        val = {}
                        val.update({'name':page.content.split('<span class="nowrap">')[1].split('</span>')[0].split('line">')[-1]})
                        for item in value:
                            val.update({item[0]:(item[-2],item[-1])[item[-1]!='']})
                        print '<Host> '+val['name']+' has '+val['Points']+' point'+('s','')[val['Points'] == 0]+', his rank is '+val['Position'].split('/')[0]+' out of '+val['Position'].split('/')[1]+' players ('+val['Titre']+') in Newbie'
                        serv.privmsg(name, val['name']+' has '+val['Points']+' point'+('s','')[val['Points'] == 0]+', his rank is '+val['Position'].split('/')[0]+' out of '+val['Position'].split('/')[1]+' players ('+val['Titre']+') in Newbie')
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<'+name+'> '+val['name']+' has '+val['Points']+' point'+('s','')[val['Points'] == 0]+', his rank is '+val['Position'].split('/')[0]+' out of '+val['Position'].split('/')[1]+' players ('+val['Titre']+') in Newbie\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+name+'> '+val['name']+' has '+val['Points']+' point'+('s','')[val['Points'] == 0]+', his rank is '+val['Position'].split('/')[0]+' out of '+val['Position'].split('/')[1]+' players ('+val['Titre']+') in Newbie\n')
                    elif ' Affinez votre recherche' in page.content:
                        print '<Host> Impossible to complete search for '+_name+' in Newbie ('+page.content.split(' Affinez votre recherche')[0].split('<td>')[-1].replace('\n','')+')'
                        serv.privmsg(name,'Impossible to complete search for '+_name+' in Newbie ('+page.content.split(' Affinez votre recherche')[0].split('<td>')[-1].replace('\n','')+')')
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<'+name+'> Impossible to complete search for '+_name+' in Newbie ('+page.content.split(' Affinez votre recherche')[0].split('<td>')[-1].replace('\n','')+')\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+name+'> Impossible to complete search for '+_name+' in Newbie ('+page.content.split(' Affinez votre recherche')[0].split('<td>')[-1].replace('\n','')+')\n')
                    else:
                        print '<Host> no such result in Newbie for',_name
                        serv.privmsg(name,'no such result in Newbie for '+_name)
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<'+name+'> no such result in Newbie for '+_name+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+name+'> no such result in Newbie for '+_name+'\n')
            if author in [self.__name]+self.superadmins+self.admins:
                if message.split(' ')[0] == '!superadminofthedeath' and not author in self.admins:
                    serv.primsg(canal,'Do you think this commande realy exist ?')
                elif message == '!info' and self.channels.__contains__(self.__canal):
                    serv.privmsg(author,self.info())
                elif message == '!stats':
                    for _name in stat:
                            serv.privmsg(author,_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats]))
                            print '<Host> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
                elif message == '!order66':
                    cible = ' '.join(info.users()).split(' ')[random.randint(0,len(info.users())-1)]
                    serv.action(self.__canal, 'execute order 66')
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket, '\r<'+self.__canal+'> *'+self.__name+' execute order 66*\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <'+self.__canal+'> *'+self.__name+' execute order 66*\n')
                    print '<'+self.__canal+'> *'+self.__name+' execute order 66*'
                    info = self.channels[self.__canal]
                    if cible in info.users() and not info.is_owner(cible) and not info.is_admin(cible) and not info.is_oper(cible):
                        serv.kick(self.__canal,name,'take a blaster and open fire')

                    else:
                        serv.action(self.__canal, 'take a blaster, but con\'t open fire on '+cible)
                        broadcast_data(server_socket, '\r<'+self.__canal+'> *'+self.__name+' take a blaster, but can\'t open fire on '+cible+'*\n')
                        print '<'+self.__canal+'> *'+self.__name+' take a blaster, but con\'t open fire on '+cible+'*'
                elif message == '!halfadmins':
                    if len(self.admins) != 0:
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<Host> '+', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+\
                                ' half admin'+('s','')[len(self.admins)==1]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> '+', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+\
                                ' half admin'+('s','')[len(self.admins)==1]+'\n')
                        print '<Host> '+', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+\
                            ' half admin'+('s','')[len(self.admins)==1]
                        serv.privmsg(author, ', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+' half admin'+('s','')[len(self.admins)==1])
                    else:
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<Host> There is no half admin\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> There is no half admin\n')
                        print '<Host> There is no half admin'
                        serv.privmsg(author, 'There is no half admin')
                elif message.split(' ')[0] == '!stat':
                    if len(message.split(' ')) == 1:
                        message += ' '+author
                    for _name in message.split(' ')[1:]:
                        serv.privmsg(author,_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                            item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats]))
                        print '<Host> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                            item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
                elif message.split(' ')[0] in ['!tu','!topurl']:
                    if len(message.split(' ')) == 1:
                        serv.privmsg(name,'Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+' at '+item[2][:-3].replace('T',' ') for item in self.all_url[:10]]))
                        print '<Host> Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+' at '+item[2][:-3].replace('T',' ') for item in self.all_url[:10]])
                        broadcast_data(server_socket,'\r<Host> Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                            ' at '+item[2][:-3].replace('T',' ') for item in self.all_url[:10]])+'\n')
                    else:
                        for _name in message.split(' ')[1:]:
                            try:
                                serv.privmsg(name,_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                                    ' at '+item[2][:-3].replace('T',' ') for item in stat[_name]['urls'][:10]]))
                                print '<Host> '+_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+' at '+item[2][:-3].replace('T',' ') for item in stat[_name]['urls'][:10]])
                                broadcast_data(server_socket,'\r<Host> '+_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                                    ' at '+item[2][:-3].replace('T',' ') for item in stat[_name]['urls'][:10]])+'\n')
                            except:
                                print 'Error, procces abort !'
                                broadcast_data(server_socket,'\r<Host> Process abort !\n')
                elif message.split(' ')[0] == '!cronvdm':
                    if message == 'cronvdm':
                        broadcast_data(server_socket,'\r<Host> Cronvdm is '+('off','on')[not cronvdm.stop]+'\n')
                        print '<Host> Cronvdm is '+('off','on')[not cronvdm.stop]
                    elif message == 'cronvdm next':
                        test = cronvdm._iter.get_prev(datetime)
                        in_time = dateutil.parser.parse(cronvdm._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<Host> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
                        print '<Host> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
                    elif message.split(' ')[1] in ['on','off'] and len(message.split(' ')) == 2:
                        if ('off','on')[not cronvdm.stop] == message.split(' ')[1]:
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Cronvdm is already '+('off','on')[not cronvdm.stop]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Cronvdm is already '+('off','on')[not cronvdm.stop]+'\n')
                            print '<Host> Cronvdm is already '+('off','on')[not cronvdm.stop]
                        else:
                            cronvdm.stop = (True,False)[message.split(' ')[1] == 'on']
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Cronvdm is '+('off','on')[not cronvdm.stop]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Cronvdm is '+('off','on')[not cronvdm.stop]+'\n')
                            print '<Host> Cronvdm is '+('off','on')[not cronvdm.stop]
                    elif cronvdm and len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            cronvdm._iter = croniter(message.split(' ',1)[1],datetime.now())
                            print '<Host> New cronvdm value is :',message.split(' ',1)[1]
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> New cronvdm value is :'+message.split(' ',1)[1]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> New cronvdm value is :'+message.split(' ',1)[1]+'\n')
                        except:
                            print 'Impossible option for !cronvdm'
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket, '\r<Host> Unkown option for !cronvdm\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !cronvdm\n')
                    elif len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            test = croniter(message.split(' ',1)[1], datetime.now())
                            print 'Cronvdm is already off'
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket, '\r<Host> Cronvdm is already off\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Cronvdm is already off\n')
                        except:
                            print 'Impossible option for !cronvdm'
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket, '\r<Host> Unkown option for !cronvdm\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !cronvdm\n')
                            
                    else:
                        print 'Unkown option for !cronvdm'
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<Host> Unkown option for !cronvdm\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !cronvdm\n')
                elif message.split(' ')[0] == '!crondtc':
                    if message == 'crondtc':
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<Host> crondtc is '+('off','on')[not crondtc.stop]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> crondtc is '+('off','on')[not crondtc.stop]+'\n')
                        print '<Host> crondtc is '+('off','on')[not crondtc.stop]
                    elif message == 'crondtc next':
                        test = crondtc._iter.get_prev(datetime)
                        in_time = dateutil.parser.parse(crondtc._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket, '\r<Host> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
                        print '<Host> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
                    elif message.split(' ')[1] in ['on','off'] and len(message.split(' ')) == 2:
                        if ('off','on')[not crondtc.stop] == message.split(' ')[1]:
                            broadcast_data(server_socket,'\r<Host> Crondtc is already '+('off','on')[not crondtc.stop]+'\n')
                            print '<Host> Crondtc is already '+('off','on')[not crondtc.stop]
                        else:
                            crondtc.stop = (True,False)[message.split(' ')[1] == 'on']
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Crondtc is '+('off','on')[not crondtc.stop]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Crondtc is '+('off','on')[not crondtc.stop]+'\n')
                            print '<Host> Crondtc is '+('off','on')[not crondtc.stop]
                    elif crondtc and len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            crondtc._iter = croniter(message.split(' ',1)[1],datetime.now())
                            print '<Host> New crondtc value is :',message.split(' ',1)[1]
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> New crondtc value is :'+message.split(' ',1)[1]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> New crondtc value is :'+message.split(' ',1)[1]+'\n')
                        except:
                            print 'Impossible option for !crondtc'
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Unkown option for !crondtc\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !crondtc\n')
                    elif len(message.split(' ')) == 2 or len(message.split(' ')) == 6:
                        try:
                            test = croniter(message.split(' ',1)[1], datetime.now())
                            print 'crondtc is already off'
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> crondtc is already off\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> crondtc is already off\n')
                        except:
                            print 'Impossible option for !crondtc'
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Unkown option for !crondtc\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !crondtc\n')
                    else:
                        print 'Unkown option for !crondtc'
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<Host> Unkown option for !crondtc\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !crondtc\n')
                elif message.split(' ')[0] == '!fonction':
                    if message == '!fonction':
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<Host> Fonctions are '+('off','on')[self.fonctions]+'\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Fonctions are '+('off','on')[self.fonctions]+'\n')
                        print '<Host> Fonctions are',('off','on')[self.fonctions]
                        serv.privmsg(self.__canal, 'Fonctions are '+('off','on')[self.fonctions])
                    elif message.split(' ')[1] in ['on','off']:
                        if ('off','on')[self.fonctions] == message.split(' ')[1]:
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Fonctions are already '+('off','on')[self.fonctions]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Fonctions are already '+('off','on')[self.fonctions]+'\n')
                            print '<Host> Fonctions are already',('off','on')[self.fonctions]
                            serv.privmsg(self.__canal, 'Fonctions are already '+('off','on')[self.fonctions])
                        else:
                            self.fonctions = (False,True)[message[1:-1].split(' ')[1] == 'on']
                            if len(pseudo_list) != 0:
                                broadcast_data(server_socket,'\r<Host> Fonctions are '+('off','on')[self.fonctions]+'\n')
                            else:
                                self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Fonctions are '+('off','on')[self.fonctions]+'\n')
                            print '<Host> Fonctions are',('off','on')[self.fonctions]
                            serv.privmsg(self.__canal, 'Fonctions are '+('off','on')[self.fonctions])
                    else:
                        print 'Unkown option for !fonction'
                        serv.privmsg(author,'Unkown option for !fonction')
                        if len(pseudo_list) != 0:
                            broadcast_data(server_socket,'\r<Host> Unkown option for !fonction\n')
                        else:
                            self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> Unkown option for !fonction\n')
                elif message.split(' ')[0] == '!away' and not author in self.admins:
                    self.away = not self.away
                    if self.away and len(message.split(' ')[0]) > 1:
                        self.away_message = message.split(' ',1)[1]
                    else:
                        self.away_message = ''
                    print '\033[1;32mself '+('get back','come away')[self.away]+' (by '+author+')'+(' ('+self.away_message+')','')[len(self.away_message)==0]+'\033[0m'
                    serv.privmsg(author, 'Yes master, I '+('get back','come away')[self.away]+(' for reason : '+self.away_message,'')[len(self.away_message)==0])
                    serv.privmsg(self.__canal, 'self '+('get back','come away')[self.away]+(' for reason : '+self.away_message,'')[len(self.away_message)==0])
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket,'\r<Host> self '+('get back','come away')[self.away]+' (by '+author+(' for reason : '+self.away_message,'')[len(self.away_message)==0]+')\n')
                    else:
                        self.history.append('\r('+datetime.now().isoformat()[:-7].replace('T',' ')+') <Host> self '+('get back','come away')[self.away]+' (by '+author+(' for reason : '+self.away_message,'')[len(self.away_message)==0]+')\n')
                elif message.split(' ')[0] == '!halfadmin' and len(message.split(' ')[1:]) > 1:
                    for name in message[1:-1].split(' ')[1:]:
                        self.half_admins.append(name)
                    if len(pseudo_list) != 0:
                        broadcast_data(server_socket,'\r<Host> '+', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                            ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n')
                    if name != self.__name:
                        serv.privmsg(author,', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                            ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n')
                elif message.split(' ')[0] == '!unhalfadmin' and len(message.split(' ')) > 1 :
                    temp_H = []
                    for name in message.split(' ')[1:]:
                        if name in self.half_admins:
                            self.half_admins.remove(name)
                            temp._H.appen(name)
                    if len(temp_H) != 0:
                        broadcast_data(server_socket,'\r<Host> '+', '.join(temp_H)+' '+('are','is')[len(temp_H)==1]+\
                            ' not half admin'+('s','')[len(temp_H)==1]+' now\n')
                        print '<Host> '+', '.join(temp_H)+' '+('are','is')[len(temp_H)==1]+\
                            ' not half admin'+('s','')[len(temp_H)==1]+' now'
                elif message.split(' ')[0] == '!admins' and	not author in self.admins:
                    if len(self.admins) != 0:
                        broadcast_data(server_socket,'\r<Host> '+', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+\
                            ' admin'+('s','')[len(self.admins)==1]+'\n')
                        print '<Host> '+', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+\
                            ' admin'+('s','')[len(self.admins)==1]
                        serv.privmsg(author, ', '.join(self.admins)+' '+('are','is')[len(self.admins)==1]+' admin'+('s','')[len(self.admins)==1])
                    else:
                        broadcast_data(server_socket,'\r<Host> There is no admin\n')
                        print '<Host> There is no admin'
                        serv.privmsg(author, 'There is no admin')
                elif message.split(' ')[0] == '!admin' and len(message.split(' ')[1:]) > 1 and not author in self.admins:
                    for name in message[1:-1].split(' ')[1:]:
                        self.admins.append(name)
                    broadcast_data(server_socket,'\r<Host> '+', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                        ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n')
                    if name != self.__name:
                        serv.privmsg(author,', '.join(message[1:-1].split(' ')[1:])+' '+('are','is')[len(message[1:-1].split(' ')[1:])==1]+\
                            ' admin'+('s','')[len(message[1:-1].split(' ')[1:])==1]+' now\n')
        elif message.split(' ')[0] == '!vdm' and not cronvdm.stop:
            in_time = dateutil.parser.parse(cronvdm._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
            test = cronvdm._iter.get_prev(datetime)
            serv.privmsg(name, 'You have not access to this fonction but next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]])
            print 'You have not access to this fonction but next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
            broadcast_data(server_socket, '\r<Host> You have not access to this fonction but next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
        elif message.split(' ')[0] == '!dtc' and not crondtc.stop:
            in_time = dateutil.parser.parse(crondtc._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
            test = crondtc._iter.get_prev(datetime)
            serv.privmsg(name, 'You have not access to this fonction but next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]])
            print 'You have not access to this fonction but next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
            broadcast_data(server_socket, '\r<Host> You have not access to this fonction but next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')

class lancheur(Thread):
    def __init__(self, fonction):
        if fonction in ['bot','serveur','cronvdm','crondtc']:
            Thread.__init__(self)
            self.fonction=fonction
            if fonction in ['cronvdm','crondtc']:
                self.stop = True
                self.end = False
    def run(self):
        if self.fonction == 'bot':
            robot.start()
        elif self.fonction == 'serveur':
            self.__url = re.compile('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            while not robot.is_connected():
                autoaway = False
            quit = True
            cronvdm.stop = True
            crondtc.stop = True
            autore = True
            robot.get_server()[1].privmsg(robot.get_name(),'!stat')
            try:
                while quit:
                    read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
                    for sock in read_sockets:
                        try:
                            if sock == server_socket:
                                sockfd, addr = server_socket.accept()
                                CONNECTION_LIST.append(sockfd)
                                pseudo_list.append([sockfd,[],0])
                                print ("Client (%s, %s) \033[1;32mconnected at "% addr)+\
                                    datetime.now().time().isoformat().split('.')[0]+"\033[0m"
                                if addr[0] in black_list_ip:
                                    black_list_try[black_list_ip.index(addr[0])] += 1
                                    print '\033[1;33mThe black listed adress\033[1;31m',addr[0],'\033[1;33mhas been detected and refuse to connect !\nit actually at\033[1;31m',\
                                        black_list_try[black_list_ip.index(addr[0])],'\033[1;33mtry and fail !\033[0m'
                                    sock.close()
                                    CONNECTION_LIST.remove(sock)
                                    pseudo_list.remove([sockfd,[],0])
                            else:
                                data = sock.recv(RECV_BUFFER)
                                if data:
                                    for socket in pseudo_list:
                                        if socket[0] == sock and socket[2] == 0:
											name = encryption.decode(data,key)
                                            if name in admin_list:
                                                socket[1] = name
                                                socket.append(2)
                                                socket.append(random.randint(100000,1000000))
                                                mess = encryption.encode('\r<Host> Password required : ;'+str(socket[4]),key)
                                                socket[0].send(mess)
                                                print ('Client ('+socket[1]+', %s, %s)') %addr,'\033[1;32mtry login as admin\033[0m'
                                            else:
                                                print 'Client (%s, %s)' %addr,'host \033[1;32mtry to connected but is not admin\033[0m'
                                                found = False
                                                for item in try_list:
                                                    if item[0] == addr[0]:
                                                        item[1] += 1
                                                        found = True
                                                        if item[1] == 5:
                                                            black_list_ip.append(addr[0])
                                                            print '\033[1;31mThe IP address',addr[0],'is now black listed !\033[0m'
                                                            black_list_try.append(5)
                                                if not found:
                                                    try_list.append([addr[0],1])
                                                sock.close()
                                                CONNECTION_LIST.remove(sock)
                                                pseudo_list.remove(socket)
                                            if name in pseudo_list:
                                                print "Client (%s, %s)" %addr,"remove, \033[1;32mpseudo already use\033[0m"
                                                mess = encryption.encode('\r<Host> Your pseudo is already use, change and reconnect\n',key)
                                                sock.send(mess)
                                                sock.close()
                                                CONNECTION_LIST.remove(sock)
                                            socket[2] += 1
                                        elif socket[0] == sock and socket[2] == 1:
                                            reply = encryption.decode(data,key)[:-1]
                                            answer = md5.new(admin_pwd[admin_list.index(socket[1])]+str(socket[4])).digest()
                                            if len(socket) < 6:
                                                if reply == answer:
                                                    socket[2] += 1
                                                    socket[3] = 3
                                                    mess = encryption.encode("\r<Host> Password accept, Welcome "+socket[1]+"\n",key)
                                                    socket[0].send(mess)
                                                    print '\033[1;33mAdmin \033[0m:\033[1;32m', socket[1], 'connected succesfully at '+\
                                                        datetime.now().time().isoformat().split('.')[0]+' !\033[0m'
                                                    broadcast_data(sock, "\r<Host>Client "+socket[1]+\
                                                        " is online, as admin\n")
                                                    if len(pseudo_list) == 1 and robot.away:
                                                        mess = encryption.encode('\r<Host> Robot is actually away send commande : "!away" to erase this mode\n',key)
                                                        socket[0].send(mess)
                                                    robot.get_server()[1].privmsg(robot.get_name(),'!whois connect')
                                                    time.sleep(0.7)
                                                    try:
                                                        mess = encryption.encode(robot.topic,key)
                                                    except:
                                                        mess = encryption.encode('\r<Host> There is no topic in this channel !\n',key)
                                                    socket[0].send(mess)
                                                    time.sleep(0.7)
                                                    mess = encryption.encode('\r<Host> Fonctions are '+('off','on')[robot.fonctions]+'\n',key)
                                                    socket[0].send(mess)
                                                    time.sleep(0.7)
                                                    mess = encryption.encode('\r<Host> Autoaway is '+('off','on')[autoaway]+'\n',key)
                                                    socket[0].send(mess)
                                                    time.sleep(0.7)
                                                    mess = encryption.encode('\r<Host> Autohello is '+('off','on')[robot.autohello]+'\n',key)
                                                    socket[0].send(mess)
                                                    time.sleep(0.7)
                                                    mess = encryption.encode('\r<Host> Autore is '+('off','on')[autore]+'\n',key)
                                                    socket[0].send(mess)
                                                    if robot.wake_up.day - robot.last_stop.day > 0 and len(pseudo_list) == 1:
                                                        print '<Host> Auto Zbra'
                                                        robot.get_server()[1].privmsg(robot.get_canal(), 'Zbra')
                                                        mess = encryption.encode('\r<Host> Auto Zbra\n',key)
                                                        socket[0].send(mess)
                                                    elif len(pseudo_list) == 1 and autore:
                                                        print 'Auto Re'
                                                        robot.get_server()[1].privmsg(robot.get_canal(), 'Re')
                                                        mess = encryption.encode('\r<Host> Auto Re\n',key)
                                                        socket[0].send(mess)
                                                elif socket[3] != 0:
                                                    socket[3] -= 1
                                                    socket[3] -= 1
                                                    socket[3] -= 1
                                                    socket[4] = random.randint(100000,1000000)
                                                    mess = encryption.encode("\r<Host> Password refused : ;"+str(socket[4]),key)
                                                    socket[0].send(mess)
                                                else:
                                                    mess = encryption.encode("\r<Host> Connection end, bad password\n",key)
                                                    socket[0].send(mess)
                                                    print "Client (",socket[1],"%s, %s )" %addr,\
                                                        "\033[1;33mtry to connected has admin and fail at "+\
                                                        datetime.now().time().isoformat().split('.')[0]+"!\033[0m"
                                                    sock.close()
                                                    CONNECTION_LIST.remove(sock)
                                                    pseudo_list.remove(socket)
                                            else:
                                                if reply == answer:
                                                    socket[2] = socket[5][0] + 1
                                                    mess = encryption.encode("\r<Host> Command accept !\n",key)
                                                    socket[0].send(mess)
                                                    if len(socket[5]) == 1:
                                                        if robot.is_connected():
                                                            robot.get_server()[1].privmsg(robot.get_name(),'!quit')
                                                        quit = False
                                                    elif len(socket[5]) == 2:
                                                        admin_pwd[admin_list.index(item)] = socket[5][0]
                                                        print "Client (",socket[1],"%s, %s )" %addr,\
                                                            "change is password to : ",\
                                                            admin_pwd[admin_list.index(item)],',',
                                                        try:
                                                            if not os.path.isfile('./admin.txt'):
                                                                raise ValueError('file not exist !')
                                                            _file = open('admins.txt','w+')
                                                            for item in admin_list:
                                                                _file.write(item+';'+admin_pwd\
                                                                    [admin_list.index(item)]+'\n')
                                                                _file.close()
                                                                print 'file change done !'
                                                        except:
                                                            print 'file error !'
                                                            msg = encryption.encode('\r<Host> Error in process, '+\
                                                                'password change until server\'s'+\
                                                                ' reboot !\n',key)
                                                            socket[0].send(msg)
                                                    socket[3] = 3
                                                    socket.remove(socket[-1])
                                                elif socket[3] != 0:
                                                    socket[3] -= 1
                                                    socket[4] = random.randint(100000,1000000)
                                                    mess = encryption.encode("\r<Host> Password refused : ;"+str(socket[4]),key)
                                                    socket[0].send(mess)
                                                else:
                                                    mess = encryption.encode("\r<Host> Command refused : bad password\n",key)
                                                    socket[0].send(mess)
                                                    print "Client (",socket[1],"%s, %s )" %addr,\
                                                        "try to used admin command and fail !"
                                                    socket[2] = socket[5][0] + 1
                                                    socket[3] = 3
                                                    socket.remove(socket[-1])
                                        elif socket[0] == sock:
                                            if data != 'client hello':
                                                mess = encryption.decode(data,key)
                                                print '(serveur)',socket[1],':',mess[:-1]
                                            else:
                                                mess = ''
                                                socket[2] -= 1
                                            if mess == '':
                                                pass
                                            elif mess[0] != '!':
                                                broadcast_data(sock, '\r<' + socket[1] +'> '+mess)
                                                robot.get_server()[1].privmsg(robot.get_canal(),mess)
                                                stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
                                                stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+len(mess[:-1].split(' '))})
                                                stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+len(mess)-mess[:-1].count(' ')-2})
                                                urls = self.__url.findall(mess)
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
                                            else:
                                                if mess[1:-1] == 'quit':
                                                    socket[4] = random.randint(100000,1000000)
                                                    msg = encryption.encode(\
                                                        '\r<Host> Password required : ;'+\
                                                        str(socket[4]),key)
                                                    socket.append([socket[2]])
                                                    socket[2] = 0
                                                    socket[3] = 2
                                                    socket[0].send(msg)
                                                elif mess[1:-1] == 'leave':
                                                    broadcast_data(sock, "\r<Host> Client "+socket[1]+" is offline\n")
                                                    print '\033[1;33mClient (',socket[1],', %s, %s) is offline (leave) !\033[0m' % addr
                                                    pseudo_list.remove(socket)
                                                    sock.close()
                                                    CONNECTION_LIST.remove(sock)
                                                    if len(pseudo_list) == 0:
                                                        robot.last_stop = datetime.now()
                                                        if not robot.away and autoaway:
                                                            robot.away == True
                                                            robot.get_server()[1].action(robot.get_canal(),'is away')
                                                            print '\033[1;32mRobot come away\033[0m'
                                                elif mess[1:-1] == 'help':
                                                    mess = encryption.encode(\
                                                        '\r<Host> As admin you have permit command :\n'+\
                                                        '\t- "!help" : give you all commands\n'+\
                                                        '\t- "!kick( <pseudo>)+" : kick all name you list\n'+\
                                                        '\t- "!password <password>" : change your password accont (only serv)\n'+\
                                                        '\t- "!whois( <pseudo>)+" : give information about name in the list\n'+\
                                                        '\t- "!connect" : give information about who is connect in IRC\n'+\
                                                        '\t- "!infobot" : Get information of the bot\n'+\
                                                        '\t- "!topic" : Get the current topic \n'+\
                                                        '\t- "!lastkick" : Get information about the last kick save, if it\' possible\n'+\
                                                        '\t- "!slap <pseudo>" : Give a slap to the pseudo you give\n'+\
                                                        '\t- "!vdm ({1-15})?" : Give one to 15 VDM, fonction is protect\n'+\
                                                        '\t- "!cronvdm [on|off|next]" : Active/Unactive programmed VDM, if cronvdm active "next" give time from\n'+\
                                                        '\t\tif none give status\n'+\
                                                        '\t- "!dtc ({1-26})?" : Give one to 26 DTC, fonction is protect\n'+\
                                                        '\t- "!crondtc [on|off|next]" : Active/Unactive programmed DTC, if cronvdm active "next" give time from\n'+\
                                                        '\t\tif none give status\n'+\
                                                        '\t- "!score( <pseudo>)+" : Give Root-me and Newbie score of each pseudo, if it exist !\n'+\
                                                        '\t- "!away( <message>)?" : Change away\'s mode of the bot\n'+\
                                                        '\t- "!autoaway [on|off]" : Give status of autoaway or change it\n'+\
                                                        '\t- "!autohello [on|off]" : Give status of autohello or change it\n'+\
                                                        '\t- "!autore [on|off]" : Give status of autore or change it\n'+\
                                                        '\t- "!admin( <pseudo>)+" : Give admin status for each pseudo\n'+\
                                                        '\t- "!halfadmin( <pseudo>)+" : Give half admin status for each pseudo\n'+\
                                                        '\t- "!unadmin( <pseudo>)+" : Take admin and half admin status for each pseudo\n'+\
                                                        '\t- "!admins" : Give admins list of the bot\n'+\
                                                        '\t- "!halfadmins" : Give half admins list of the bot\n'+\
                                                        '\t- "!fonction [on|off]" : Change status of bot\'s fonctions\n'+\
                                                        '\t- "!msg <pseudo> <message>" : send <message in private to <pseudo>\n'+\
                                                        '\t- "!robot <message>" : robot do <message> in IRC\n'+\
                                                        '\t- "!change <canal>" : change the canal of the bot to the given one\n'+\
                                                        '\t- "!topurl< pseudo>*" : Give top 10 of url, if no pseudo it\'s global top\n'+\
                                                        '\t- "!stat( <pseudo>)*" : Give stats of pseudo list, if none give yours\n'+\
                                                        '\t- "!stats" : Give all stats ! (the list could be long !)\n'+\
                                                        '\t- "!status" : Give stats of the canal (equal to !connect but each status is describe)\n'+\
                                                        '\t- /!\\ "!quit" : as admin use quit close the serveur /!\\\n',key)
                                                    socket[0].send(mess)
                                                    robot.get_server()[1].privmsg(robot.get_name(),'!help')
                                                elif mess[1:-1] == 'infobot':
                                                    msg = encryption.encode('\r<Host> '+robot.info()+'\n',key)
                                                    socket[0].send(msg)
                                                elif mess[1:-1] == 'lastkick':
                                                    robot.get_server()[1].privmsg(robot.get_canal(),mess[:-1])
                                                    robot.fonction(robot.get_server()[1],robot.get_canal(),mess[:-1],robot.get_name())
                                                elif mess[1:-1] == 'applause':
                                                    broadcast_data(sock, '\r<'+socket[1]+'> *'+robot.get_name()+' *\n')
                                                    robot.get_server()[1].action(robot.get_canal(),'applause')
                                                    stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
                                                    stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+1})
                                                    stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+8})
                                                elif mess[1:-1] == 'topic':
                                                    print '<Host> '+robot.topic
                                                    broadcast_data(server_socket,'\r<Host> '+robot.topic+'\n')
                                                elif mess[1:-1].split(' ')[0] == 'away':
                                                    robot.away = not robot.away
                                                    if robot.away and len(mess[1:-1].split(' ')[0]) > 1:
                                                        robot.away_message = mess[1:-1].split(' ',1)[1]
                                                    else:
                                                        robot.away_message = ''
                                                    broadcast_data(server_socket,'\r<Host> Robot '+('get back','come away'+(' ('+robot.away_message+')','')[len(robot.away_message)==0])[robot.away]+'\n')
                                                    robot.get_server()[1].action(robot.get_canal(),('come back','is away'+(' ('+robot.away_message+')','')[len(robot.away_message)==0])[robot.away])
                                                    print '\033[1;32mRobot '+('get back','come away'+(' ('+robot.away_message+')','')[len(robot.away_message)==0]+'\033[0m')[robot.away]
                                                elif mess[1:-1].split(' ')[0] == 'kick':
                                                    for name in mess[1:-1].split(' ')[1:]:
                                                        for item in pseudo_list:
                                                            if name == item[1]:
                                                                broadcast_data(server_socket,\
                                                                    "\rClient "+item[1]+\
                                                                    " has been kick by "+\
                                                                    socket[1]+"\n")
                                                                print "Client (",item[1],\
                                                                    ", %s, %s)" %addr,\
                                                                    "is offline : \033[1;31mkick by",\
                                                                    (socket[1]+'\033[0m')
                                                                pseudo_list.remove(item)
                                                                CONNECTION_LIST.remove(item[0])
                                                                item[0].close()
                                                elif mess[1:-1].split(' ')[0] == 'kickirc' and len(mess[1:-1].split(' ')) > 1:
                                                    robot.get_server()[1].privmsg(robot.get_name(),mess[:-1])
                                                elif mess[1:-1].split(' ')[0] == 'password' and len(mess[1:-1].split(' ')) == 2:
                                                    for item in admin_list:
                                                        if item == socket[1]:
                                                            if mess[1:-1].split(' ')[1] !=\
                                                                admin_pwd[admin_list.index(socket[1])]:
                                                                socket[4] = random.randint(100000,1000000)
                                                                msg = encryption.encode('\r<Host> Password required : ;'+\
                                                                    str(socket[4]),key)
                                                                socket.append([socket[2],\
                                                                    mess[1:-1].split(' ')[1]])
                                                                socket[2] = 0
                                                                socket[3] = 2
                                                                socket[0].send(msg)
                                                            else:
                                                                msg = encryption.encode(\
                                                                    '\r<Host> Command refused, '+\
                                                                    'can\'t change to current '+\
                                                                    'password !\n',key)
                                                                print "Client (",item,", %s, %s)" %addr,\
                                                                    "try to change password,",\
                                                                    "fail because current",\
                                                                    "password !"
                                                                socket[0].send(msg)
                                                elif mess[1:-1].split(' ')[0] == 'connect':
                                                    robot.get_server()[1].privmsg(robot.get_name(),'!whois connect')
                                                elif mess[1:-1].split(' ')[0] == 'whois':
                                                    for name in mess[1:-1].split(' ')[1:]:
                                                        for item in pseudo_list:
                                                            if name == item[1]:
                                                                msg = encryption.encode('\r<Host> '+name+\
                                                                    ", IP : %s %s," %addr+' have send '+\
                                                                    str(item[2]-(1,2)[name in admin_list])+' messge(s)\n',key)
                                                                socket[0].send(msg)
                                                elif mess[1:-1].split(' ')[0] == 'msg' and len(mess[1:-1].split(' ')) > 2 :
                                                    broadcast_data(sock, "\r" + '<' + socket[1] +','+\
                                                        mess[1:-1].split(' ')[1]+'> '+mess[1:-1].split(' ',2)[2])
                                                    robot.get_server()[1].privmsg(mess[1:-1].split(' ')[1],mess[1:-1].split(' ',2)[2])
                                                    print mess[1:-1].split(' ')[1],': private :',mess[1:-1].split(' ',2)[2]
                                                elif mess[1:-1].split(' ')[0] == 'robot':
                                                    broadcast_data(sock, '\r<'+socket[1]+'> *'+robot.get_name()+' '+\
                                                        mess[1:-1].split(' ',1)[1]+'*\n')
                                                    robot.get_server()[1].action(robot.get_canal(),mess[1:-1].split(' ',1)[1])
                                                    stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
                                                    stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+len(mess[:-1].split(' '))-1})
                                                    stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+len(mess)-mess[:-1].count(' ')-9})
                                                elif mess[1:-1].split(' ')[0] == 'change' and len(mess[1:-1].split(' ')) == 2 and \
                                                    '#' in mess[1:-1].split(' ')[1]:
                                                    robot.get_server()[1].disconnect('leave')
                                                    robot.get_server()[1].join(mess[1:-1].split(' ')[1])
                                                elif mess[1:-1].split(' ')[0] == 'vdm':
                                                    robot.get_server()[1].privmsg(robot.get_canal(),mess[:-1])
                                                    robot.fonction(robot.get_server()[1],robot.get_canal(),mess[:-1],robot.get_name())
                                                elif mess[1:-1].split(' ')[0] == 'dtc':
                                                    robot.get_server()[1].privmsg(robot.get_canal(),mess[:-1])
                                                    robot.fonction(robot.get_server()[1],robot.get_canal(),mess[:-1],robot.get_name())
                                                elif mess[1:-1].split(' ')[0] == 'cronvdm':
                                                    if mess[1:-1] == 'cronvdm':
                                                        broadcast_data(server_socket,'\r<Host> Cronvdm is '+('off','on')[not cronvdm.stop]+'\n')
                                                        print '<Host> Cronvdm is '+('off','on')[not cronvdm.stop]
                                                    elif mess[1:-1] == 'cronvdm next':
                                                        test = cronvdm._iter.get_prev(datetime)
                                                        in_time = dateutil.parser.parse(cronvdm._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
                                                        broadcast_data(server_socket, '\r<Host> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                                                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                                                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
                                                        print '<Host> Next auto vdm is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                                                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                                                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
                                                    elif mess[1:-1].split(' ')[1] in ['on','off'] and len(mess[1:-1].split(' ')) == 2:
                                                        if ('off','on')[not cronvdm.stop] == mess[1:-1].split(' ')[1]:
                                                            broadcast_data(server_socket,'\r<Host> Cronvdm is already '+('off','on')[not cronvdm.stop]+'\n')
                                                            print '<Host> Cronvdm is already '+('off','on')[not cronvdm.stop]
                                                        else:
                                                            cronvdm.stop = (True,False)[mess[1:-1].split(' ')[1] == 'on']
                                                            broadcast_data(server_socket,'\r<Host> Cronvdm is '+('off','on')[not cronvdm.stop]+'\n')
                                                            print '<Host> Cronvdm is '+('off','on')[not cronvdm.stop]
                                                    elif cronvdm and len(mess[1:-1].split(' ')) == 2 or len(mess[1:-1].split(' ')) == 6:
                                                        try:
                                                            cronvdm._iter = croniter(mess[1:-1].split(' ',1)[1],datetime.now())
                                                            print '<Host> New cronvdm value is :',mess[1:-1].split(' ',1)[1]
                                                            broadcast_data(server_socket,'\r<Host> New cronvdm value is :'+mess[1:-1].split(' ',1)[1]+'\n')
                                                        except:
                                                            print 'Impossible option for !cronvdm'
                                                            socket[0].send(encryption.encode('\r<Host> Unkown option for !cronvdm\n',key))
                                                    elif len(mess[1:-1].split(' ')) == 2 or len(mess[1:-1].split(' ')) == 6:
                                                        try:
                                                            test = croniter(mess[1:-1].split(' ',1)[1], datetime.now())
                                                            print 'Cronvdm is already off'
                                                            socket[0].send(encryption.encode('\r<Host> Cronvdm is already off\n',key))
                                                        except:
                                                            print 'Impossible option for !cronvdm'
                                                            socket[0].send(encryption.encode('\r<Host> Unkown option for !cronvdm\n',key))
                                                    else:
                                                        print 'Unkown option for !cronvdm'
                                                        socket[0].send(encryption.encode('\r<Host> Unkown option for !cronvdm\n',key))
                                                elif mess[1:-1].split(' ')[0] == 'crondtc':
                                                    if mess[1:-1] == 'crondtc':
                                                        broadcast_data(server_socket,'\r<Host> crondtc is '+('off','on')[not crondtc.stop]+'\n')
                                                        print '<Host> crondtc is '+('off','on')[not crondtc.stop]
                                                    elif mess[1:-1] == 'crondtc next':
                                                        test = crondtc._iter.get_prev(datetime)
                                                        in_time = dateutil.parser.parse(crondtc._iter.get_next(datetime).isoformat()) - dateutil.parser.parse(datetime.now().isoformat().split('.')[0])
                                                        broadcast_data(server_socket, '\r<Host> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                                                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                                                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]+'\n')
                                                        print '<Host> Next auto dtc is in '+(str(divmod(in_time.days * 86400 + in_time.seconds, 60)[0])+' minute'+\
                                                            ('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] in [0,1]]+' ','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[0] == 0]+\
                                                            str(divmod(in_time.days * 86400 + in_time.seconds, 60)[1])+' seconde'+('s','')[divmod(in_time.days * 86400 + in_time.seconds, 60)[1] in [0,1]]
                                                    elif mess[1:-1].split(' ')[1] in ['on','off'] and len(mess[1:-1].split(' ')) == 2:
                                                        if ('off','on')[not crondtc.stop] == mess[1:-1].split(' ')[1]:
                                                            broadcast_data(server_socket,'\r<Host> Crondtc is already '+('off','on')[not crondtc.stop]+'\n')
                                                            print '<Host> Crondtc is already '+('off','on')[not crondtc.stop]
                                                        else:
                                                            crondtc.stop = (True,False)[mess[1:-1].split(' ')[1] == 'on']
                                                            broadcast_data(server_socket,'\r<Host> Crondtc is '+('off','on')[not crondtc.stop]+'\n')
                                                            print '<Host> Crondtc is '+('off','on')[not crondtc.stop]
                                                    elif crondtc and len(mess[1:-1].split(' ')) == 2 or len(mess[1:-1].split(' ')) == 6:
                                                        try:
                                                            crondtc._iter = croniter(mess[1:-1].split(' ',1)[1],datetime.now())
                                                            print '<Host> New crondtc value is :',mess[1:-1].split(' ',1)[1]
                                                            broadcast_data(server_socket,'\r<Host> New crondtc value is :'+mess[1:-1].split(' ',1)[1]+'\n')
                                                        except:
                                                            print 'Impossible option for !crondtc'
                                                            socket[0].send(encryption.encode('\r<Host> Unkown option for !crondtc\n',key))
                                                    elif len(mess[1:-1].split(' ')) == 2 or len(mess[1:-1].split(' ')) == 6:
                                                        try:
                                                            test = croniter(mess[1:-1].split(' ',1)[1], datetime.now())
                                                            print 'crondtc is already off'
                                                            socket[0].send(encryption.encode('\r<Host> crondtc is already off\n',key))
                                                        except:
                                                            print 'Impossible option for !crondtc'
                                                            socket[0].send(encryption.encode('\r<Host> Unkown option for !crondtc\n',key))
                                                    else:
                                                        print 'Unkown option for !crondtc'
                                                        socket[0].send(encryption.encode('\r<Host> Unkown option for !crondtc\n',key))
                                                elif mess[1:-1].split(' ')[0] == 'score':
                                                    robot.get_server()[1].privmsg(robot.get_canal(),mess[:-1])
                                                    robot.fonction(robot.get_server()[1],robot.get_canal(),mess[:-1],robot.get_name())		
                                                elif mess[1:-1].split(' ')[0] == 'autoaway':
                                                    if mess[1:-1] == 'autoaway':
                                                        broadcast_data(server_socket,'\r<Host> Autoaway is '+('off','on')[autoaway]+'\n')
                                                        print '<Host> Autoaway is '+('off','on')[autoaway]
                                                    elif mess[1:-1].split(' ')[1] in ['on','off'] and len(mess[1:-1].split(' ')) == 2:
                                                        if ('off','on')[autoaway] == mess[1:-1].split(' ')[1]:
                                                            broadcast_data(server_socket,'\r<Host> Autoway is already '+('off','on')[autoaway]+'\n')
                                                            print '<Host> Autoaway is '+('off','on')[autoaway]
                                                        else:
                                                            autoaway = (False,True)[mess[1:-1].split(' ')[1] == 'on']
                                                            broadcast_data(server_socket,'\r<Host> Autoaway is now : '+('off','on')[autoaway]+'\n')
                                                            print '<Host> Autoaway is '+('off','on')[autoaway]
                                                    else:
                                                        print 'Unkown option for !autoaway'
                                                        socket[0].send(encryption.encode('\r<Host> Unkown option for !autoaway\n',key))
                                                elif mess[1:-1].split(' ')[0] == 'autohello':
                                                    if mess[1:-1] == 'autohello':
                                                        broadcast_data(server_socket,'\r<Host> Autohello is '+('off','on')[robot.autohello]+'\n')
                                                        print '<Host> Autohello is '+('off','on')[robot.autohello]
                                                    elif mess[1:-1].split(' ')[1] in ['on','off']:
                                                        if ('off','on')[robot.autohello] == mess[1:-1].split(' ')[1]:
                                                            broadcast_data(server_socket,'\r<Host> Autohello is already '+('off','on')[robot.autohello]+'\n')
                                                            print '<Host> Autohello is '+('off','on')[robot.autohello]
                                                        else:
                                                            robot.autohello = (False,True)[mess[1:-1].split(' ')[1] == 'on']
                                                            broadcast_data(server_socket,'\r<Host> Autohello is now : '+('off','on')[robot.autohello]+'\n')
                                                            print '<Host> Autohello is '+('off','on')[robot.autohello]
                                                    else:
                                                        print 'Unkown option for !autohello'
                                                        socket[0].send(encryption.encode('\r<Host> Unkown option for !autohello\n',key))
                                                elif mess[1:-1].split(' ')[0] == 'autore':
                                                    if mess[1:-1] == 'autore':
                                                        broadcast_data(server_socket,'\r<Host> Autore is '+('off','on')[autore]+'\n')
                                                        print '<Host> Autore is '+('off','on')[autore]
                                                    elif mess[1:-1].split(' ')[1] in ['on','off']:
                                                        if ('off','on')[autore] == mess[1:-1].split(' ')[1]:
                                                            broadcast_data(server_socket,'\r<Host> Autore is already '+('off','on')[autore]+'\n')
                                                            print '<Host> Autore is '+('off','on')[autore]
                                                        else:
                                                            autore = (False,True)[mess[1:-1].split(' ')[1] == 'on']
                                                            broadcast_data(server_socket,'\r<Host> Autore is now : '+('off','on')[autore]+'\n')
                                                            print '<Host> Autore is '+('off','on')[autore]
                                                    else:
                                                        print 'Unkown option for !autore'
                                                        socket[0].send(encryption.encode('\r<Host> Unkown option for !autore\n',key))
                                                elif mess[1:-1].split(' ')[0] == 'fonction':
                                                    if mess[1:-1] == 'fonction':
                                                        broadcast_data(server_socket,'\r<Host> Fonctions are '+('off','on')[robot.fonctions]+'\n')
                                                        print '<Host> Fonctions are '+('off','on')[robot.fonctions]
                                                    elif mess[1:-1].split(' ')[1] in ['on','off']:
                                                        if ('off','on')[robot.fonctions] == mess[1:-1].split(' ')[1]:
                                                            broadcast_data(server_socket,'\r<Host> Fonctions are already '+('off','on')[robot.fonctions]+'\n')
                                                            print '<Host> Fonctions are '+('off','on')[robot.fonctions]
                                                        else:
                                                            robot.fonctions = (False,True)[mess[1:-1].split(' ')[1] == 'on']
                                                            broadcast_data(server_socket,'\r<Host> Fonctions are '+('off','on')[robot.fonctions]+'\n')
                                                            print '<Host> Fonctions are',('off','on')[robot.fonctions]
                                                            robot.get_server()[1].privmsg(robot.get_canal(), 'Fonctions are '+('off','on')[robot.fonctions])
                                                    else:
                                                        print 'Unkown option for !fonction'
                                                        socket[0].send(encryption.encode('\r<Host> Unkown option for !fonction\n',key))
                                                elif mess[1:-1].split(' ')[0] == 'admins':
                                                    if len(robot.admins) != 0:
                                                        broadcast_data(server_socket,'\r<Host> '+', '.join(robot.admins)+' '+('are','is')[len(robot.admins)==1]+\
                                                            ' admin'+('s','')[len(robot.admins)==1]+'\n')
                                                        print '<Host> '+', '.join(robot.admins)+' '+('are','is')[len(robot.admins)==1]+\
                                                            ' admin'+('s','')[len(robot.admins)==1]
                                                    else:
                                                        broadcast_data(server_socket,'\r<Host> There is no admin\n')
                                                        print '<Host> There is no admin'
                                                elif mess[1:-1].split(' ')[0] == 'halfadmins':
                                                    if len(robot.half_admins) != 0:
                                                        broadcast_data(server_socket,'\r<Host> '+', '.join(robot.half_admins)+' '+('are','is')[len(robot.half_admins)==1]+\
                                                            ' half admin'+('s','')[len(robot.half_admins)==1]+'\n')
                                                        print '<Host> '+', '.join(robot.half_admins)+' '+('are','is')[len(robot.half_admins)==1]+\
                                                            ' half admin'+('s','')[len(robot.half_admins)==1]
                                                    else:
                                                        broadcast_data(server_socket,'\r<Host> There is no half admin\n')
                                                        print '<Host> There is no half admin'
                                                elif mess[1:-1].split(' ')[0] == 'topurl':
                                                    if len(mess[1:-1].split(' ')) == 1:
                                                        print '<Host> Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                                                            ' at '+item[2][:-3].replace('T',' ') for item in robot.all_url[:10]])
                                                        broadcast_data(server_socket,'\r<Host> Global top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                                                            ' at '+item[2][:-3].replace('T',' ') for item in robot.all_url[:10]])+'\n')
                                                    else:
                                                        for _name in mess[1:-1].split(' ')[1:]:
                                                            try:
                                                                print '<Host> '+_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                                                                    ' at '+item[2][:-3].replace('T',' ') for item in stat[_name]['urls'][:10]])
                                                                broadcast_data(server_socket,'\r<Host> '+_name+' top url :\n'+'\n'.join([ item[0]+', '+(str(item[1])+' times ','')[item[1] == 1]+\
                                                                    ' at '+item[2][:-3].replace('T',' ') for item in stat[_name]['urls'][:10]])+'\n')
                                                            except:
                                                                print 'Error process abord !'
                                                                broadcast_data(server_socket,'\r<Host> Process abort !\n')
                                                elif mess[1:-1].split(' ')[0] == 'stat':
                                                    if len(mess[1:-1].split(' ')) == 1:
                                                        mess = mess[:-1]+' '+robot.get_name()+'\n'
                                                    for _name in mess[1:-1].split(' ')[1:]:	
                                                        time.sleep(0.7)
                                                        broadcast_data(server_socket,'\r<Host> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                                            item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])+'\n')
                                                        print '<Host> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                                            item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
                                                elif mess[1:-1].split(' ')[0] == 'stats':
                                                    for _name in stat:
                                                        if _name != '':
                                                            time.sleep(0.7)
                                                            broadcast_data(server_socket,'\r<Host> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                                                item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])+'\n')
                                                            print '<Host> '+_name+' send '+', '.join([ str(stat[_name][item])+' '+\
                                                                item[:-1]+('s','')[stat[_name][item]==1] for item in stat[_name] if item in stats])
                                                elif mess[1:-1].split(' ')[0] == 'status' :
                                                    if mess[1:-1] == 'status':
                                                        info = robot.channels[robot.get_canal()]
                                                        broadcast_data(server_socket, '\r<Host> '+\
                                                            ('Owners connected : '+', '.join(info.owners())+'\n','')[len(info.owners()) == 0]+\
                                                            ('Admins connected : '+', '.join(info.admins())+'\n','')[len(info.admins()) == 0]+\
                                                            ('Opers connected : '+', '.join(info.opers())+'\n','')[len(info.opers()) == 0]+\
                                                            ('Half opers connected : '+', '.join(info.halfops())+'\n','')[len(info.halfops()) == 0]+\
                                                            ('Voiced connected : '+', '.join(info.voiced())+'\n','')[len(info.voiced()) == 0]+\
                                                            ('Users connected : '+', '.join(info.users())+'\n','')[len(info.users()) == 0])
                                                        print '<Host> Information from canal : '+robot.get_canal()+\
                                                            ('Owners connected : '+', '.join(info.owners())+'\n','')[len(info.owners()) == 0]+\
                                                            ('Opers connected : '+', '.join(info.opers())+'\n','')[len(info.opers()) == 0]+\
                                                            ('Admins connected : '+', '.join(info.admins())+'\n','')[len(info.admins()) == 0]+\
                                                            ('Half opers connected : '+', '.join(info.halfops())+'\n','')[len(info.halfops()) == 0]+\
                                                            ('Voiced connected : '+', '.join(info.voiced())+'\n','')[len(info.voiced()) == 0]+\
                                                            ('Users connected : '+', '.join(info.users()),'')[len(info.users()) == 0]
                                                    else:
                                                        for _canal in mess[1:-1].split(' ')[1:]:
                                                            try:
                                                                info = robot.channels[_canal]
                                                                broadcast_data(server_socket, '\r<Host> Info from canal : '+_canal+\
                                                                    ('Owners connected : '+', '.join(info.owners())+'\n','')[len(info.owners()) == 0]+\
                                                                    ('Admins connected : '+', '.join(info.admins())+'\n','')[len(info.admins()) == 0]+\
                                                                    ('Opers connected : '+', '.join(info.opers())+'\n','')[len(info.opers()) == 0]+\
                                                                    ('Half opers connected'+', '.join(info.halfops())+'\n','')[len(info.halfops()) == 0]+\
                                                                    ('Voiced connected'+', '.join(info.voiced())+'\n','')[len(info.voiced()) == 0]+\
                                                                    ('Users connected'+', '.join(info.users())+'\n','')[len(info.users()) == 0])
                                                                print '<Host> Information from canal : '+_canal+\
                                                                    ('Owners connected : '+', '.join(info.owners())+'\n','')[len(info.owners()) == 0]+\
                                                                    ('Opers connected : '+', '.join(info.opers())+'\n','')[len(info.opers()) == 0]+\
                                                                    ('Admins connected : '+', '.join(info.admins())+'\n','')[len(info.admins()) == 0]+\
                                                                    ('Half opers connected'+', '.join(info.halfops())+'\n','')[len(info.halfops()) == 0]+\
                                                                    ('Voiced connected'+', '.join(info.voiced())+'\n','')[len(info.voiced()) == 0]+\
                                                                    ('Users connected'+', '.join(info.users()),'')[len(info.users()) == 0]
                                                            except:
                                                                broadcast_data(server_socket, '\r<Host> No Info from channel : '+_canal+'\n')
                                                elif mess[1:-1].split(' ')[0] == 'slap' :
                                                    for name in mess[1:-1].split(' ')[1:]:
                                                        robot.get_server()[1].action(robot.get_canal(),'slaps '+name+' around a bit with a large trout')
                                                        broadcast_data(server_socket, '\r<'+robot.get_canal()+'> *'+robot.get_name()+' slaps '+name+' around a bit with a large trout*\n')
                                                        print '<'+robot.get_canal()+'> *'+robot.get_name()+'slaps '+name+' around a bit with a large trout*'
                                                elif mess[1:-1].split(' ')[0] == 'admin' and len(mess[1:-1].split(' ')) > 1 :
                                                    for name in mess[1:-1].split(' ')[1:]:
                                                        if name != '':
                                                            robot.admins.append(name)
                                                    broadcast_data(server_socket,'\r<Host> '+', '.join(mess[1:-1].split(' ')[1:])+' '+('are','is')[len(mess[1:-1].split(' ')[1:])==1]+\
                                                        ' admin'+('s','')[len(mess[1:-1].split(' ')[1:])==1]+' now\n')
                                                    print '<Host> '+', '.join(mess[1:-1].split(' ')[1:])+' '+('are','is')[len(mess[1:-1].split(' ')[1:])==1]+\
                                                        ' admin'+('s','')[len(mess[1:-1].split(' ')[1:])==1]+' now'
                                                elif mess[1:-1].split(' ')[0] == 'halfadmin' and len(mess[1:-1].split(' ')) > 1 :
                                                    for name in mess[1:-1].split(' ')[1:]:
                                                        if name != '':
                                                            robot.half_admins.append(name)
                                                    broadcast_data(server_socket,'\r<Host> '+', '.join(mess[1:-1].split(' ')[1:])+' '+('are','is')[len(mess[1:-1].split(' ')[1:])==1]+\
                                                        ' half admin'+('s','')[len(mess[1:-1].split(' ')[1:])==1]+' now\n')
                                                    print '<Host> '+', '.join(mess[1:-1].split(' ')[1:])+' '+('are','is')[len(mess[1:-1].split(' ')[1:])==1]+\
                                                        ' half admin'+('s','')[len(mess[1:-1].split(' ')[1:])==1]+' now'
                                                elif mess[1:-1].split(' ')[0] == 'unadmin' and len(mess[1:-1].split(' ')) > 1 :
                                                    temp_A = []
                                                    temp_H = []
                                                    for name in mess[1:-1].split(' ')[1:]:
                                                        if name in robot.admins:
                                                            robot.admins.remove(name)
                                                            temp_A.append(name)
                                                        if name in robot.half_admins:
                                                            robot.half_admins.remove(name)
                                                            temp_H.append(name)
                                                    if len(temp_A) != 0:
                                                        broadcast_data(server_socket,'\r<Host> '+', '.join(temp_A)+' '+('are','is')[len(temp_A)==1]+\
                                                            ' not admin'+('s','')[len(temp_A)==1]+' now\n')
                                                        print '<Host> '+', '.join(temp_A)+' '+('are','is')[len(temp_A)==1]+\
                                                            ' not admin'+('s','')[len(temp_A)==1]+' now'
                                                    if len(temp_H) != 0:
                                                        broadcast_data(server_socket,'\r<Host> '+', '.join(temp_H)+' '+('are','is')[len(temp_H)==1]+\
                                                            ' not half admin'+('s','')[len(temp_H)==1]+' now\n')
                                                        print '<Host> '+', '.join(temp_H)+' '+('are','is')[len(temp_H)==1]+\
                                                            ' not half admin'+('s','')[len(temp_H)==1]+' now'
                                                else:
                                                    broadcast_data(sock, '\r<' + socket[1] +'> '+mess)
                                                    robot.get_server()[1].privmsg(robot.get_canal(),mess[:-1])
                                                    stat[robot.get_name()].update({'messages':stat[robot.get_name()]['messages']+1})
                                                    stat[robot.get_name()].update({'words':stat[robot.get_name()]['words']+len(mess[:-1].split(' '))})
                                                    stat[robot.get_name()].update({'letters':stat[robot.get_name()]['letters']+len(mess)-mess[:-1].count(' ')-1})
                                            socket[2] += 1
                                else:
                                    for item in pseudo_list:
                                        if sock == item[0]:
                                            broadcast_data(sock, "\rClient "+item[1]+" is offline\n")
                                            print '\033[1;33mClient (',item[1],', %s, %s) is offline (client close) !\033[0m' % addr
                                            pseudo_list.remove(item)
                                            sock.close()
                                            CONNECTION_LIST.remove(sock)
                                    if len(pseudo_list) == 0:
                                        robot.last_stop = datetime.now()
                                        if not robot.away and autoaway:
                                            robot.away == True
                                            robot.get_server()[1].action(robot.get_canal(),' is away')
                                            print '\033[1;32mRobot come away\033[0m'
                        except KeyboardInterrupt:
                            for item in pseudo_list:
                                if sock == item[0] and item[1] in admin_list:
                                    raise KeyboardInterrupt('admin close serveur')
                        except Exception, e:
                            print e.__class__.__name__, e, e.message
                            if not [sockfd,[],0] in pseudo_list:
                                for item in pseudo_list:
                                    if sock == item[0]:
                                        broadcast_data(sock, "\r<Host> Client "+item[1]+" is offline\n")
                                        print '\033[1;33mClient (',item[1],', %s, %s) is offline (forced to quit) !\033[0m' % addr
                                        pseudo_list.remove(item)
                                        sock.close()
                                        CONNECTION_LIST.remove(sock)
                                if len(pseudo_list) == 0:
                                    robot.last_stop = datetime.now()
                                    if not robot.away and autoaway:
                                        robot.away == True
                                        robot.get_server()[1].action(robot.get_canal(),'is away')
                                        print '\033[1;32mRobot come away\033[0m'
                            else:
                                print '\033[1;33mClient (',item[1],', %s, %s) close (forced to quit during establishment) !\033[0m' % addr
                                pseudo_list.remove([sockfd,[],0])
                                sock.close()
                                CONNECTION_LIST.remove(sock)
            except KeyboardInterrupt:
                broadcast_data(server_socket, '\r<Host> Server end\n')
                print '\033[1;31mAdmin close serveur\033[0m'
            finally:
                server_socket.close()
                print '\033[1;32mService end correctly !\033[0m'
                if black_list_ip != []:
                    try:
                        _file = open('black.list.txt','w+')
                        _file.write('\n'.join(['%s;%s' %(ip, black_list_try[black_list_ip.index(ip)]) for ip in black_list_ip]))
                        _file.close()
                    except:
                        print '\033[1;31mError in writting black list !\033[0m'
                        if os.path.isfile('./black.list.txt'):
                            os.system('rm -f black.list.txt')
                for name in stat.keys():
                    if not config.has_section(name):
                        config.add_section(name)
                        for item in stats:
                            config.set(name,item,0)
                    if not name in ['',None]:
                        for options in stat[name].keys():
                            config.set(name,options,stat[name][options])
                        print name,':',{item:stat[name][item] for item in stat[name] if item in stats}
                config.set('DEFAULT','time_stop',datetime.now().isoformat().split('.')[0])
                config.set('DEFAULT','all_url',str(robot.all_url))
                with open('stat.txt', 'wb') as configfile:
                    config.write(configfile)
                cronvdm.stop = True
                cronvdm.end = True
                crondtc.stop = True
                crondtc.end = True
                sys.exit()
        elif self.fonction == 'cronvdm':
            while not self.end:
                while not self.stop:
                    _next = self._iter.get_next(datetime).isoformat()[:-1]
                    while datetime.now().isoformat()[:-8] != _next and not self.stop and not self.end:
                        time.sleep(3)
                    if not self.stop and robot.is_connected():
                        robot.get_server()[1].privmsg(robot.get_canal(),'Programmed VDM !')
                        broadcast_data(server_socket,'\r<Host> Programmed VDM !\n')
                        print '<Host> Programmed VDM !'
                        robot.fonction(robot.get_server()[1],robot.get_canal(),'!vdm',robot.get_name())
                time.sleep(3)
        elif self.fonction == 'crondtc':
            while not self.end:
                while not self.stop:
                    _next = self._iter.get_next(datetime).isoformat()[:-1]
                    while datetime.now().isoformat()[:-8] != _next and not self.stop and not self.end:
                        time.sleep(3)
                    if not self.stop and robot.is_connected():
                        robot.get_server()[1].privmsg(robot.get_canal(),'Programmed DTC !')
                        broadcast_data(server_socket,'\r<Host> Programmed DTC !\n')
                        print '<Host> Programmed DTC !'
                        robot.fonction(robot.get_server()[1],robot.get_canal(),'!dtc',robot.get_name())
                time.sleep(3)
        else:
            print '\033[1;31mFunction unkown, programm stop\033[0m'

def broadcast_data(sock, message):
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            for item in pseudo_list:
                if item[0] == socket and item[1] in admin_list:
                    if item[3] == 3:
                        socket.send(encryption.encode(message,key))
                elif item[0] == socket:
                    socket.send(encryption.encode(message,key))

def main():
    try:
        # Threads 
        thread_1 = lancheur("bot")
        thread_2 = lancheur("serveur")
        
        # Lanch !
        thread_1.start()
        thread_2.start()
        cronvdm.start()
        crondtc.start()
        
        # Waitting for end !
        thread_1.join()
        thread_2.join()
    except:
        print 'End program !'

if __name__ == "__main__":
    CONNECTION_LIST = []
    pseudo_list = []
    black_list_ip = []
    black_list_try = []
    try_list = []
    found = False
    admin_list = ['admin']
    admin_pwd = ['admin']
    try:
        _file = open('admins.txt','r+')
        line = _file.read()
        _file.close()
        line = line.split('\n')
        for item in line:
            if ';' in item:
                admin_list.append(item.split(';')[0])
                admin_pwd.append(item.split(';')[1])
        admin_list.remove(admin_list[0])
        admin_pwd.remove(admin_pwd[0])
        print '\033[1;32mAn admin list is now available !\033[0m'
    except:
        print '\033[1;33mDefault admin is available !\033[0m'
        admin_list = ['admin']
        admin_pwd = ['admin']
    try:
        _file = open('key.txt','r+')
        line = _file.read()
        _file.close()
        key = line.split('\n')[0]
        print '\033[1;32mA specific key is available !\033[0m'
    except:
        raise IOError('\033[1;31mBot stop no key available !\033[0m')
    try:
        _file = open('black.list.txt','r+')
        line = _file.read()
        _file.close()
        line = line.split('\n')
        for item in line:
            if ';' in item:
                black_list_ip.append(item.split(';')[0])
                black_list_try.append(item.split(';')[1])
                try:
                    temp = socket.inet_aton(item.split(';')[0])
                except:
                    black_list_ip.remove(item.split(';')[0])
                    black_list_try.remove(item.split(';')[1])
        print '\033[1;32mA black list has been found !\033[0m'
    except:
        print '\033[1;33mNo black list found !\033[0m'
        black_list_ip = []
        black_list_try = []
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
        urls = re.compile("(?:[[]('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', [0-9]+, '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}')[]])")
        for section in config.sections():
            stat.update({section:{}})
            for value in stats:
                stat[section].update({value:int(config.get(section,value))})
            stat[section].update({'urls':[[num(item) for item in element.replace("'",'').split(', ')] for element in urls.findall(config.get(section,'urls'))]})
        print '\033[1;32mStats have been found !\033[0m'
    except IOError:
        print '\033[1;33mNo stats found !\033[0m'
        stat= {}
    cronvdm = lancheur('cronvdm')
    cronvdm._iter = croniter('0 * * * *', datetime.now())
    crondtc = lancheur('crondtc')
    crondtc._iter = croniter('0 * * * *', datetime.now())
    RECV_BUFFER = 4096 
    PORT = 5000 
    binary = Binary.Binary()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connect = False
    while not connect:
        try:
            server_socket.bind(("", PORT))
        except Exception, e:
            if e.__class__.__name__ == 'error' and str(e) == '[Errno 98] Address already in use':
                PORT += 1
            else:
                raise e
        connect = True
    server_socket.listen(10)
    CONNECTION_LIST.append(server_socket)
    print '\033[1;32mChat server started on port', str(PORT),'\033[0m'
    name = ''
    if '-n' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-n') > 0:
        name = sys.argv[sys.argv.index('-n')+1]
    server = ''
    if '-s' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-s') > 0:
        server =  sys.argv[sys.argv.index('-s')+1]
    canal = ''
    if '-c' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-c') > 0:
        canal = sys.argv[sys.argv.index('-c')+1]
    password = ''
    if '-p' in sys.argv and (len(sys.argv)-1)-sys.argv.index('-p') > 0:
        password = sys.argv[sys.argv.index('-p')+1]
    if name != '' and canal != '' and server != '' and password != '':
        robot = LeRobot(name,canal,server,password)
        print ('\033[1;33mrobot get name ('+name+'), canal ('+canal+') and server ('+server+') and password ('+password+')!\033[0m')
    elif name != '' and canal != '' and server != '':
        robot = LeRobot(name,canal,server)
        print ('\033[1;33mrobot get name ('+name+'), canal ('+canal+') and server ('+server+')!\033[0m')
    elif name != '' and canal != '' and password != '':
        robot = LeRobot(name,canal,password=password)
        print '\033[1;33mrobot get name ('+name+') and canal ('+canal+') and password ('+password+')!\033[0m'
    elif name != '' and canal != '':
        robot = LeRobot(name,canal)
        print '\033[1;33mrobot get name ('+name+') and canal ('+canal+')!\033[0m'
    elif canal != '' and server != '' and password != '':
        robot = LeRobot(canal=canal,server=server,password=password)
        print '\033[1;33mrobot get canal ('+canal+') and server ('+server+') and password ('+password+')!\033[0m'
    elif canal != '' and server != '':
        robot = LeRobot(canal=canal,server=server)
        print '\033[1;33mrobot get canal ('+canal+') and server ('+server+')!\033[0m'
    elif name != '' and server != '' and password != '':
        robot = LeRobot(name=name,server=server,password=password)
        print '\033[1;33mrobot get name ('+name+') and serveur ('+server+') and password ('+password+')!\033[0m'
    elif name != '' and server != '':
        robot = LeRobot(name=name,server=server)
        print '\033[1;33mrobot get name ('+name+') and serveur ('+server+')!\033[0m'
    elif name != '' and password != '':
        robot = LeRobot(name=name,password=password)
        print '\033[1;33mrobot get name ('+name+') and password ('+password+')!\033[0m'
    elif canal != '' and password != '':
        robot = LeRobot(canal=canal,password=password)
        print '\033[1;33mrobot get canal ('+canal+') and password ('+password+')!\033[0m'
    elif server != '' and password != '':
        robot = LeRobot(server=server,password=password)
        print '\033[1;33mrobot get server ('+server+') and password ('+password+')!\033[0m'
    elif name != '':
        robot = LeRobot(name=name)
        print '\033[1;33mrobot get a name ('+name+')!\033[0m'
    elif canal != '':
        robot = LeRobot(canal=canal)
        print '\033[1;33mrobot get a canal ('+canal+')!\033[0m'
    elif server != '':
        robot = LeRobot(server=server)
        print '\033[1;33mrobot get a server ('+server+')!\033[0m'
    elif password != '':
        robot = LeRobot(password=password)
        print '\033[1;33mrobot get a password ('+password+')!\033[0m'
    else:
        robot = LeRobot()
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
