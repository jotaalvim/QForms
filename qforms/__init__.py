"""
Qforms: google-forms like local form generator tool
"""
#!/usr/bin/python3

from flask import Flask, render_template, request
#from flask_ngrok import run_with_ngrok
import sys, os, yaml, json, jjcli, waitress
app = Flask(__name__)
conf={}
__version__ = "0.3"
c = None

def main():
    global c,conf
    c = jjcli.clfilter(opt="d:cjh")

    if '-h' in c.opt:
        print(
        """Usage: qforms [options] config.yaml   
        Options: 
            -j : export to <title>.json
            -c : export to <title>.csv
            -d <domain> : server host = domain (def: localhost) 
            -h : this help
        """)
        sys.exit(0)

    fconf = c.args[0]
    conf = yaml.safe_load( open(fconf).read() )

    if "-d" in c.opt:
        waitress.serve(app, host=c.opt["-d"], port=8080)
    else:
        waitress.serve(app, host="localhost", port=8080)
    #app.run()





#if '-n' in c.opt:
#    run_with_ngrok(app)



@app.route('/quest',methods = ['GET','POST'])
def quest():
    if request.method == 'GET':
        return list2form (conf)

    if request.method == 'POST':
        form2file(conf, request.form)
        return mostra_request (conf, request.form)


def list2form(l:list)->str:
    title,*l2 = l
    h = f"<h1>{title}</h1>\n<form method='post'> <ul>"
    fim = "<input type=submit value='done'/> </ul></form>"

    for dic in l2:
        id = dic['id'] # name
        t  = dic.get('t','str') # types
        op = dic.get('o') # options
        d  = dic.get('h','') # description, helper
        r  = dic.get('req',False) # required
        req = 'required' if r else ''

        if t == 'str':
            h += f"<li> {id}: <input type='text' name='{id}' {req} /> </li> <p>{d}</p>\n"
        if t == 'radio': # selects on of diferent buttons 
            h += f'<li>{id}: <br/>'
            for elem in op:
                h += f"<input type='radio' name='{id}' value='{elem}' {req} >  {elem}</input> <br/>"
            h += f'</li>  <p>{d}</p>\n'
        if t == 'check':# checkbox buttons
            h += f'<li>{id}: <br/>'
            for elem in op:
                h += f"<input type='checkbox' name='{id}' value='{elem}' >  {elem}</input> <br/>"
            h += f'</li> <p>{d}</p>\n'
    return h + fim

    
#takes a form and a list os dicts(from yaml) and stores it in json, csv files
def form2file(l:list,d:list)->str:
    fdict = forms2dict(d)
    fcsv  = forms2csv(l,d)

    title,*l2 = l
    #path to yamell: fconf
    #extracting the file name and path from fconf (first argument)
    lp = fconf.split(sep='/') #list with the path
    if len(lp) > 1:
        name = lp[-1][:-5] # from: 'path/path/name.yaml' returns: 'name'
        path = '/'.join(lp[:-1])+'/' #path without the file
    else:
        name = lp [0][:-5]
        path = ''
    
    lId = listId(l) # list of dentifiers 

    # exporting to csv
    if '-c' in c.opt:
        f = open(path+name+'.csv','a')
        if not os.path.exists(path+name+'.csv'):
            f.write(f'{title}\n')
            f.write(','.join(lId)+'\n')
        f.write(fcsv+'\n')
        f.close()
    #exporting to json
    if '-j' in c.opt:
        f = open(path+name+'.json','a')
        if not os.path.exists(path+name+'.json'):
            f.write(f'{{"title":"{title}"}}')
        f.write(json.dumps(fdict)+'\n')
        f.close()


#making the "recieved" html for the POST method
def mostra_request(l:list,d:list)->str:
    title,*l2 = l
    h   = f'<h1> Received : {title} </h1> <ul>'
    fim = '</ul>'

    for dic in l2:
        id = dic['id'] # name
        t  = dic.get('t','str') # types
        if t == 'check':
            h += f'<li> {id}: '
            h += str.join(', ',d.getlist(id))
            h += '</li>'
        else:
            h += f"<li> {id}: {d[id]} </li>\n"
    return h + fim

#forms to coma separated values
def forms2csv(l:list,d:dict)->str:
    title,*l2 = l
    lId = listId(l) # list of identifiers
    acc = []
    for id in lId:
        lo = d.getlist(id)
        if not lo: #lo == []
            acc.append('')
        if len(lo) == 1: #one argument
            acc.append(csv(lo[0]))
        if len(lo) > 1: # multiple answers
            acc.append(csv(', '.join(lo)))
    return ','.join(acc)

#string to csv
def csv (word:str)->str:
    wordaux = ''
    if '"' in word:
        for l in word:
            if l == '"':
                wordaux += '"'+ '"'
            else:
                wordaux += l
    if wordaux: # wordaux != null
        wordcsv = wordaux
    else:
        wordcsv = word
    if ',' in wordcsv or '"' in wordcsv:
        wordcsv = '"'+wordcsv+'"'
    return wordcsv

#convert a form to a dict
def forms2dict(l:list)->dict:
    acc = {}
    for id in l:
        lo = l.getlist(id)
        if len(lo) == 1:
            acc[id] = lo[0]
        else:
            acc[id] = lo
    return acc
    
def listId(l:list)->list:
    title,*l2 = l
    lacc = [] # list of identifiers
    for dic in l2:
        lacc.append(dic['id'])
    return lacc



# yaml.load ↓
#['Torneio de xadrez viii edição Braga', {'id': 'nome', 't': 'str', 'h': 'descriçao nome completo', 'req': True}, {'id': 'sexo', 't': 'radio', 'o': ['masculino', 'feminino'], 'h': 'atençao abcdefghijklmnopqrstuvwxy', 'req': True}, {'id': 'checkbox', 't': 'check', 'o': ['vaca', 'gato', 'crocodilo', 'bicho pau']}]
# form request
#ImmutableMultiDict([('nome', 'joao afonsoa alvim oliveida dias de almeida'), ('sexo', 'masculino'), ('checkbox', 'vaca'), ('checkbox', 'gato'), ('checkbox', 'crocodilo'), ('checkbox', 'bicho pau')])
#json dumps
#{"nome": "joao afonsoa alvim oliveida dias de almeida", "sexo": "masculino", "checkbox": "vaca"}
