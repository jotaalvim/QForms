#!/usr/bin/python3
from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import sys, os, yaml, json, jjcli, waitress, hashlib, shelve
from datetime import datetime


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

#yaml path
fconf = c.args[0]

UPLOAD_FOLDER = fconf.split(sep='/')[-1][:-5] + '_uploads/'
#create the upload directory
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

conf = yaml.load( open(fconf).read(), Loader=yaml.FullLoader)

app = Flask(__name__)

#ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif' }
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#if '-n' in c.opt:
#    run_with_ngrok(app)

@app.route('/quest',methods = ['GET','POST'])
def quest():
    if request.method == 'GET':
        return list2form (conf)

    if request.method == 'POST':
        form2file(conf, request.form, request.files)
        upload_file(request.files)
        return mostra_request (conf, request.form, request.files)


def list2form(l:list)->str:
    title,*l2 = l
    h = f"<h1>{title}</h1>\n<form method='post' enctype='multipart/form-data'> <ul>"
    fim = "<input type=submit value='done'/> </ul></form>"

    for dic in l2:
        id = dic['id']            # name
        t  = dic.get('t','str')   # types
        op = dic.get('o')         # options
        d  = dic.get('h','')      # description, helper
        r  = dic.get('req',False) # required
        req = 'required' if r else ''
        # text box
        if t == 'str':
            h += f"<li> {id}: <input type='text' name='{id}' {req} /> </li> <p>{d}</p>\n"
        # selects one of diferent buttons 
        if t == 'radio': 
            h += f'<li>{id}: <br/>'
            for elem in op:
                h += f"<input type='radio' name='{id}' value='{elem}' {req} >  {elem}</input> <br/>"
            h += f'</li>  <p>{d}</p>\n'
        # checkbox buttons
        if t == 'check':
            h += f'<li>{id}: <br/>'
            for elem in op:
                h += f"<input type='checkbox' name='{id}' value='{elem}'>  {elem}</input> <br/>"
            h += f'</li> <p>{d}</p>\n'
       # submit files
        if t == 'file':
            h += f"<input type='file' name ='{id}'>\n"

    return h + fim


def upload_file(d:dict):
    # d is a multidict(request.files)
    for key in d: 
        if d[key]: #d[key] != "" houve submissao de ficheiro
            f = d[key] #name
            c = f.read()
            
            oldname = f.filename

            l = oldname.split(sep='.')
            if l: # l!=[]
                ext = '.'+l[-1]
            else:
                ext = ''
            
            # calculating the file md5 
            newname = hashlib.md5(c).hexdigest()

            idnt = key
            #adding extension and identification
            finalname = idnt + newname + ext
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], finalname)) 
            
            #f.save(os.path.join(app.config['UPLOAD_FOLDER'], newname)) 


#takes a form and a list os dicts(from yaml) and stores it in json, csv files
def form2file(l:list,rfo:dict,rfi)->str:
    #rfo → request.forms
    #rfi → request.files
    fdict = forms2dict(l,rfo,rfi)
    fcsv  = forms2csv(l,rfo,rfi)
 
    title,*l2 = l
    #path to yaml: fconf
 
    #extracting the file name and path from fconf (first argument)
    lp = fconf.split(sep='/') #list with the path
    if len(lp) > 1:
        name = lp[-1][:-5] # from: 'path/path/name.yaml' returns: 'name'
        path = '/'.join(lp[:-1])+'/' #path without the file
    else:
        name = lp [0][:-5]
        path = ''
    
    lId = listId(l) # list of dentifiers 
    # saving to csv
    if '-c' in c.opt:
        f = open(path+name+'.csv','a')
        if not os.path.exists(path+name+'.csv'):
            f.write(f'{title}\n')
            f.write(','.join(lId)+'\n')
        f.write(fcsv+'\n')
        f.close()
    # saving to json
    if '-j' in c.opt:
        f = open(path+name+'.json','a')
        if not os.path.exists(path+name+'.json'):
            f.write(f'{{"title":"{title}"}}')
        f.write(json.dumps(fdict)+'\n')
        f.close()

    s = shelve.open("teste")
    chave = "nome teste"#FIXME
    s[chave] = fdict
    s.close()


#"recieved" html for the POST method
def mostra_request(yc:list,rfo:dict,rfi:dict)->str:
    #yc  → yaml conf
    #rfo → request.forms
    #rfi → request.files
    title,*l = yc
    h   = f'<h1> Received : {title} </h1> <h4> {date()}</h4><ul>'
    fim = '</ul>'

    for dic in l:
        id = dic['id'] # name
        t  = dic.get('t','str') # types
        if t == 'check':
            h += f'<li> {id}: '
            h += str.join(', ',rfo.getlist(id))
            h += '</li>'
        if t == 'file':
            lf = rfi.getlist(id)
            fn = []
            for f in lf:
                fn.append(f.filename)
            h += f'<li> {id}: '
            h += str.join(', ',fn)
            h += '</li>\n'
            
        else:
            h += f"<li> {id}: {rfo.get(id,'ignored')} </li>\n"
    return h + fim

#forms(multidict) to coma separated values
def forms2csv(yc:list,rfo:dict,rfi:dict)->str:
    # l yaml conf
    #rfo → request.forms
    #rfi → request.files
    title,*l = yc
    lId = listId(yc) # list of identifiers
    acc = []
    for dic in l:
        lo = []
        id = dic['id']
        if dic['t'] == 'file':
            f = rfi[id]
            lo = [UPLOAD_FOLDER + f.filename]
        else:
            lo = rfo.getlist(id)

        acc.append(csv(', '.join(lo)))

    acc.append(date())
    acc.append(request.remote_addr)
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

#convert a form (multidict) to a normal dict
def forms2dict(yc:list,rfo:dict,rfi:dict)->dict:
    #yc  → yaml configuration
    #rfo → request.forms
    #rfi → request.files
    title,*l = yc
    acc = {}
    for dic in l:
        lo = []
        id = dic['id']
        if dic['t'] == 'file':
            f = rfi[id]
            lo += UPLOAD_FOLDER + f.filename
            lo = ''.join(lo)
        else:
            lo = rfo.getlist(id)
        if len(lo) == 1:
            acc[id] = lo[0]
        else:
            acc[id] = lo

        acc['date'] = date()  
        acc['ip'] = request.remote_addr
    return acc

#returns a list of identifiers from the yaml config
def listId(l:list)->list: 
    title,*l2 = l
    lacc = [] 
    for dic in l2:
        lacc.append(dic['id'])
    return lacc

#get the date and time
def date()->str:
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

if __name__ == '__main__':
    if "-d" in c.opt:
        waitress.serve(app, host=c.opt["-d"], port=8080)
    else:
        waitress.serve(app, host="localhost", port=8080)
    #app.run()

# yaml.load ↓
#['Torneio de xadrez viii edição Braga', {'id': 'nome', 't': 'str', 'h': 'descriçao nome completo', 'req': True}, {'id': 'sexo', 't': 'radio', 'o': ['masculino', 'feminino'], 'h': 'atençao abcdefghijklmnopqrstuvwxy', 'req': True}, {'id': 'checkbox', 't': 'check', 'o': ['vaca', 'gato', 'crocodilo', 'bicho pau']}]

# request form 
#ImmutableMultiDict([('nome', 'joao afonsoa alvim oliveida dias de almeida'), ('sexo', 'masculino'), ('checkbox', 'vaca'), ('checkbox', 'gato'), ('checkbox', 'crocodilo'), ('checkbox', 'bicho pau')])

#json dumps
#{"nome": "joao afonsoa alvim oliveida dias de almeida", "sexo": "masculino", "checkbox": "vaca"}
