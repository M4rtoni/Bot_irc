#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, select, sys, base64, md5, getpass, readline, re, cmd, time, os

from threading import Thread
from datetime import datetime

try:
    from croniter import croniter
except:
    raise ImportError('You need croniter lib')
try:
    from pyparsing import *
except ImportError:
        raise ImportError('You need pyparsing lib') 

###
# Change for your lib for encryption (more secure)
###
class Encryption:
	def __init__(self, key):
		self.key = key
	def encode(self, string, key):
		return string
	def decode(self, string,key):
		return string

encryption = Encryption('your key')

def prompt() :
    import readline
    origline = readline.get_line_buffer()
    sys.stdout.write(my_cmd.prompt+origline)
    sys.stdout.flush()

ESC = Literal('\x1b')
integer = Word(nums)
escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer,';')) + 
                oneOf(list(alphas)))

UncolorString = lambda s : Suppress(escapeSeq).transformString(s)
    
def main():
    if True:
    try:
        # Threads 
        thread_1 = lancheur("cmd")
        thread_2 = lancheur("client")
        
        # Lanch !
        thread_1.start()
        thread_2.start()
        
        # Waitting for end !
        thread_1.join()
        thread_2.join()
    except:
    	print 'End program !'
    
    
class lancheur(Thread):
    def __init__(self, fonction):
        if fonction in ['cmd','client']:
            Thread.__init__(self)
            self.fonction=fonction
    def run(self):
        if self.fonction == 'client':
            try:
                while 1:
                    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
                    for sock in read_sockets:
                        if sock == s:
                            data = sock.recv(4096)
                            if not data :
                                    s.close()
                                    sys.exit()
                            else :
                                mess = encryption.decode(data,key)
                                now = datetime.now().time().isoformat().split('.')[0]
                                if mess[-1] == '\n':
                                    if mess[2:].split('>',1)[0] == 'Host':
                                        if mess[:-1].endswith('on line !'):
                                            for item in mess.split(' ')[1:-4]:
                                                temp = item.replace('&','').replace('~','').replace('+','').replace('@','').replace(',','')
                                                if not temp in my_cmd.pseudo:
                                                    my_cmd.pseudo.append(temp)
                                        mess = '\r<\033[1;31mHost\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+'>'+mess[7:].replace(pseudo,'\033[1;32m'+pseudo+'\033[0m')
                                        if len(mess.split('\n')) > 2 and '"!help"' in mess:
                                            p = re.compile('\t- "!([a-zA-Z0-9]+) *(.*)" : (.*)\n(\t{2}.*\n)?')
                                            temp = p.findall(mess)
                                            for item in temp:
                                                _cmd = item[0]
                                                _param = item[1]
                                                _text = item[2]
                                                if item[3] != '':
                                                    _text += '\n'+item[3][:-1]
                                                my_cmd._help.update({_cmd:(('','\tParams : '+_param+'\n')[_param != '']+'\tInfo : '+_text)})
                                            mess = ''
                                    elif not '<' in mess :
                                        mess = '\r'+('','<\033[1;32m'+now+'\033[0m> ')[_time]+'\033[1;32m'+mess[1:]+'\033[0m'
                                    elif mess[2] == '#':
                                        if mess[:-1].endswith('enter !'):
                                            if not mess.split(' ')[1:-3][0] in my_cmd.pseudo:
                                                my_cmd.pseudo.append(mess.split(' ')[1:-3][0])
                                        elif mess.split(' ')[2:5] == ['has','left','!']:
                                            if mess.split(' ')[1] in my_cmd.pseudo:
                                                my_cmd.pseudo.remove(mess.split(' ')[1])
                                        elif mess.split(' ')[2:5] == ['has','rename','in']:
                                            if mess.split(' ')[1] in my_cmd.pseudo:
                                                my_cmd.pseudo[my_cmd.pseudo.index(mess.split(' ')[1])] = mess.split(' ')[5]
                                        mess = '\r<\033[1;34m'+mess[2:].split('>')[0]+'\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+\
                                            '>\033[1;32m'+mess.split('>')[1]+'\033[0m'
                                    elif len(mess[2:].split('>')[0].split(',')) == 2 and mess[2:].split('>')[0].split(',')[1] == 'private':
                                        mess = '\r<\033[1;32m'+mess[2:].split(',')[0]+\
                                            '\033[0m,\033[1;31m'+mess[2:].split('>')[0].split(',')[1]+\
                                            '\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+'>'+\
                                            mess[len(mess[2:].split('>')[0])+3:].replace(pseudo,'\033[1;32m'+pseudo+'\033[0m')
                                        for name in list(set(my_cmd.pseudo) ^ set([pseudo])):
                                            mess = mess.split('>',1)[0]+'>'+mess.split('>',1)[1].replace(name,'\033[1;33m'+name+'\033[0m')
                                    elif len(mess[2:].split('>')[0].split(',')) == 2:
                                        mess = '\r<\033[1;32m'+mess[2:].split(',')[0]+\
                                            '\033[0m,\033[1;34m'+mess[2:].split('>')[0].split(',')[1]+\
                                            '\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+'>'+\
                                            mess[len(mess[2:].split('>')[0])+3:].replace(pseudo,'\033[1;32m'+pseudo+'\033[0m')
                                        for name in list(set(my_cmd.pseudo) ^ set([pseudo])):
                                            mess = mess.split('>',1)[0]+'>'+mess.split('>',1)[1].replace(name,'\033[1;33m'+name+'\033[0m')
                                    if mess != '':
                                        import readline
                                        origline = readline.get_line_buffer()
                                        if len(UncolorString(my_cmd.prompt+origline)) >= len(UncolorString(mess)):
                                            sys.stdout.write('\r'+' '*min(len(UncolorString(my_cmd.prompt+origline)),int(os.popen('stty size', 'r').read().split()[1])))
                                        sys.stdout.write(mess)
                                        prompt()
                                else:
                                    sys.stdout.flush()
                                    if mess.split(';')[0] == '\r<Host> Password required : ' and auto:
                                        try:
                                            _file = open('admins.txt')
                                            txt = _file.read()
                                            _file.close()
                                            txt = txt.split('\n')
                                            for item in txt:
                                                if item.split(';')[0] == pseudo:
                                                    msg = item.split(';')[1]
                                            print '\r<\033[1;31mHost\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+'> Password required'
                                            print '<\033[1;32mHost\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+'> \033[1;32mAuto response !\033[0m'
                                        except:
                                            print '\r<\033[1;31mHost\033[0m'+('',',\033[1;32m'+now+'\033[0m')[_time]+'>'+mess[7:].split(';')[0],
                                            msg = getpass.getpass()
                                            sys.stdout.flush()
                                    else :
                                        if mess[2:].split('>',1)[0] == 'Host':
                                            print '\r<\033[1;31mHost\033[0m'+('',',time')[_time]+'>'+mess[7:].split(';')[0],
                                            msg = getpass.getpass()
                                            sys.stdout.flush()
                                        else:
                                            if time:
                                                print '<\033[1;32m'+now+'\033[0m> '
                                            msg = getpass.getpass(mess.split(';')[0])
                                            sys.stdout.flush()
            finally:
                s.close()
                print '\r\033[1;32mEnd program\033[0m'
                my_cmd.quit()
        elif self.fonction == 'cmd':
            my_cmd.cmdloop()

class MyCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "<\033[1;32mYou\033[0m> "
        self.persist = False
        self.pseudo = []
        self.history = {}
        self._help = {'help': None, 'quit':'if you are admin : bot quit, else you juste close client'}
        self.stop = False
    def postcmd(self, stop, line):
        if not line in self.history.values() and not line == '':
            self.history.update({len(self.history):line})
        return cmd.Cmd.postcmd(self, stop, line)
    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext)] + [a for a in self.pseudo if a.startswith(text)]
    def default(self, line):
        self.send(line+'\n')
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
        self.send('!msg '+line+'\n')
    def complete_msg(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_quit(self, line):
        msg = '!quitclient\n'
        if isinstance(line,str):
            self.send('!quit\n')
        self.stop = True
        sys.exit()
    def complete_quit(self, text, line, start_index, end_index):
        pass
    def do_leave(self, line):
        msg = '!quitclient\n'
        self.stop = True
        self.send('!leave\n')
        sys.exit()
    def complete_leave(self, text, line, start_index, end_index):
        pass
    def do_away(self, line):
        self.send('!away\n')
    def complete_away(self, text, line, start_index, end_index):
        pass
    def do_help(self, arg):
        #cmd.Cmd.do_help(self, arg)
        if len(self._help) == 2:
            self.send('!help\n')
            while len(self._help) == 2:
                time.sleep(0.5)
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
        self.send('!infobot\n')
    def complete_infobot(self, text, line, start_index, end_index):
        pass
    def do_lastkick(self, line):
        self.send('!lastkick\n')
    def complete_lastkick(self, text, line, start_index, end_index):
        pass
    def do_connect(self, line):
        self.send('!connect\n')
    def complete_connect(self, text, line, start_index, end_index):
        pass
    def do_robot(self, line):
        self.send('!robot '+line+'\n')
    def complete_robot(self, text, line, start_index, end_index):
        pass
    def do_vdm(self, line):
        self.send('!vdm '+line+'\n')
    def complete_vdm(self, text, line, start_index, end_index):
        pass
    def do_dtc(self, line):
        self.send('!dtc '+line+'\n')
    def complete_dtc(self, text, line, start_index, end_index):
        pass
    def do_cronvdm(self, line):
        if line == '':
            self.send('!cronvdm\n')
        else:
            self.send('!cronvdm '+line+'\n')
    def complete_cronvdm(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off','next']
                 if address.startswith(text)
            ]
        else:
            return ['on','off','next']
    def do_crondtc(self, line):
        if line == '':
            self.send('!crondtc\n')
        else:
            self.send('!crondtc '+line+'\n')
    def complete_crondtc(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off','next']
                 if address.startswith(text)
            ]
        else:
            return ['on','off','next']
    def do_score(self, line):
        if line == '':
            self.send('!score\n')
        else:
            self.send('!score '+line+'\n')
    def complete_score(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                 if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_autoaway(self, line):
        if line == '':
            self.send('!autoaway\n')
        else:
            self.send('!autoaway '+line+'\n')
    def complete_autoaway(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off']
                 if address.startswith(text)
            ]
        else:
            return ['on','off']
    def do_autohello(self, line):
        if line == '':
            self.send('!autohello\n')
        else:
            self.send('!autohello '+line+'\n')
    def complete_autohello(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off']
                 if address.startswith(text)
            ]
        else:
            return ['on','off']
    def do_autore(self, line):
        if line == '':
            self.send('!autore\n')
        else:
            self.send('!autore '+line+'\n')
    def complete_autore(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off']
                 if address.startswith(text)
            ]
        else:
            return ['on','off']
    def do_fonction(self, line):
        if line == '':
            self.send('!fonction\n')
        else:
            self.send('!fonction '+line+'\n')
    def complete_fonction(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in ['on','off']
                 if address.startswith(text)
            ]
        else:
            return ['on','off']
    def do_admins(self, line):
        self.send('!admins\n')
    def complete_admins(self, text, line, start_index, end_index):
        pass
    def do_halfadmins(self, line):
        self.send('!halfadmins\n')
    def complete_halfadmins(self, text, line, start_index, end_index):
        pass
    def do_stat(self, line):
        if line == '':
            self.send('!stat\n')
        else:
            self.send('!stat '+line+'\n')
    def complete_stat(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                 if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_stats(self, line):
        self.send('!stats\n')
    def complete_stats(self, text, line, start_index, end_index):
        pass
    def do_status(self, line):
        self.send('!status\n')
    def complete_status(self, text, line, start_index, end_index):
        pass
    def do_slap(self, line):
        self.send('!slap '+line+'\n')
    def complete_slap(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                 if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_admin(self, line):
        self.send('!admin '+line+'\n')
    def complete_admin(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                 if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_halfadmin(self, line):
        self.send('!halfadmin '+line+'\n')
    def complete_halfadmin(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                 if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_unadmin(self, line):
        self.send('!unadmin '+line+'\n')
    def complete_unadmin(self, text, line, start_index, end_index):
        if text:
            return [
                address for address in self.pseudo
                 if address.startswith(text)
            ]
        else:
            return self.pseudo
    def do_history(self, line):
        """		Params : [<line>]
        Info : Give list of issued commands, line give if possible the line in the history else all commands
        """
        if not line:
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history])
        elif (line.isdigit() or (line[1:].isdigit() and line[0] in '+-')) and abs(int(line)) <= len(self.history) and line != '0':
            print '-----------------['+(str(int(line)),str(len(self.history)+int(line)+1))[int(line) < 0]+']\n'+self.history[(int(line)-1,len(self.history)+int(line))[int(line) < 0]]
        elif line[0] == '/':
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history if self.history[item].endswith(line[1:])])
        elif line[-1] == '/':
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history if line in self.history[item].startswith(line[:-1])])
        else:
            print '\n'.join(['-----------------['+str(item+1)+']\n'+self.history[item] for item in self.history if line in self.history[item]])
    def complete_history(self, *args):
        pass
    def do_test(self, line):
        print self.pseudo
        print self._help
        print dir()
        print {item:globals()[item] for item in globals() if item in ['socket', 'select', 'sys', 'base64',\
            'md5', 'getpass', 'readline', 're', 'cmd', 'time', 'Thread', ''] or item.startswith('thread')}
    def do_silent(self, line):
        self.send('!msg '+pseudo+' !'+line)
    def do_persist(self, line):
        if line == 'off':
            self.persist = False
            self.prompt = "<\033[1;32mYou\033[0m> "
        else:
            self.persist = line
            self.prompt = "<\033[1;32mYou\033[0m,\033[1;33m"+line+"\033[0m> "
    def send(self,line):
        s.send(encryption.decode((line,str(self.persist)+' '+line)[self.persist != False], key))
    def quit(self):
        sys.exit()

if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print '\033[1;33mUse condition : python <programme.py> '+\
            '<Hote(@IP)> <port> <pseudo> [-a|-auto] [-t|-time]\033[0m'
        sys.exit()
    host = sys.argv[1]
    port = int(sys.argv[2])
    pseudo = sys.argv[3]
    data = False
    msg = ''
    if len(sys.argv) > 4:
        auto = '-a' in sys.argv or '-auto' in sys.argv
        _time = '-t' in sys.argv or '-time' in sys.argv
    else:
        auto = False
        _time = False
    if len(pseudo) > 20:
        raise ValueError('Pseudo to long !')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try :
        _file = open('key.txt')
        line = _file.read()
        _file.close()
        key = line.split('\n')[0]
    except:
        raise IOError('\033[1;31mBot stop no key available !\033[0m')
    try :
		s.connect((host, port))
    except :
    	print '\033[1;31mImpossible to connect\033[0m'
    	sys.exit()
    try:
        print '\033[1;32mConnecte\033[0m'
        s.send(encryption.encode(pseudo,key))
    except:
        s.close()
        if msg != 'quitclient\n' and not data:
            print '\r\033[1;31mEnd program\033[0m'
        else:
            print '\r\033[1;32mEnd program\033[0m'
        sys.exit()
    socket_list = [sys.stdin, s]
    my_cmd = MyCmd()
    main()

