"""
Qforms: google-forms like local form generator tool
"""

from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import sys, os, yaml, json, jjcli, waitress
import hashlib, shelve, datetime

__version__ = "0.4"
app = Flask(__name__)

conf={}
c = None
fconf = None


def main():
    """Personal form generator 

    Usage: qforms [options] config.yaml
    Options: 
        -j : export to <title>.json
        -c : export to <title>.csv
        -d <domain> : server host = domain (def: localhost) 
        -h : this help
        -s : FIXME
    """

    global c,conf, fconf
    c = jjcli.clfilter(opt="sd:cjh",doc=main.__doc__)

    if '-s' in c.opt :
        print(
        """
        FIXME
        """)

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
    #conf = yaml.load( open(fconf).read(), Loader=yaml.FullLoader)

    UPLOAD_FOLDER = getPath(fconf)

    #create the upload directory
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    #subdirectory to submitted files
    subd = os.path.join(UPLOAD_FOLDER, getName(fconf)+"_submitted_files")
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    if not os.path.exists(subd):
        os.mkdir(subd)

    #ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif' }
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['KEY'] = None
    app.config['TITLE'] = None


    if "-d" in c.opt:
        print(f'[host] {c.opt["-d"]}:8080/quest')
        waitress.serve(app, host=c.opt["-d"], port=8080)
    else:
        print(f'[host] localhost:8080/quest')
        waitress.serve(app, host="localhost", port=8080)
    #app.run()

    if '-n' in c.opt:
        run_with_ngrok(app)


@app.route('/login',methods = ['GET','POST'])
def login():
    #FIXME
    if request.method == 'GET':
        return key2form(conf)
    if request.method == 'POST':
        return "asd"
    #fazer uma autenticação


@app.route('/quest',methods = ['GET','POST'])
def quest():
    if request.method == 'GET':
        page = list2form(conf)
        return page

    #test_form = {"nome!": "joao afonsoa alvim oliveida dias de almeida", "sexo": "masculino", "animais preferidos":
         #       ["gato","vaca"], "cor preferida":"vermelho"}
        #return list2formFilled(conf, test_form)

    if request.method == 'POST':
        form2file(conf, request.form, request.files)
        print("CHEGO AQUI")
        upload_file(request.files)
        return mostra_request(conf, request.form, 
                request.files)


def getName(filename:str)->str:
    head,tail = os.path.split(filename)
    return tail.replace('.yaml','')


def getPath(filename:str)->str:
    "return the uploads directory path"
    head,tail = os.path.split(filename)
    file_name = tail.replace('.yaml','')
    dirname = file_name + '_uploads'
    return os.path.join( head , dirname ) 



def key2form(yc:list)->str:
    key = getkey(yc)
    #FIXME
    return 

def list2form(l:list)->str:
    title,*l2 = l
    h = '<!DOCTYPE html>\n'
    
    
    h += """<head> 
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

.checkbox-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            max-width: 100%;
            justify-content: center;
        }

        .checkbox-container input[type='checkbox'] {
            margin-right: 1px; /* Adds space between the checkbox and the text */
        }

        .checkbox-container div {
            flex: 0 1 100px; /* Adjusts the width of each checkbox block */
            margin: 1px;
        }

</style>
            </head>"""


    h += f"<h1>{title}</h1>\n"

    h += "<form method='post' enctype='multipart/form-data'> <ul>"

    fim = "<input type=submit value='done'/> </ul></form>"

    for dic in l2:
        id = dic['id'] # name
        t  = dic.get('t','str') # types
        op = dic.get('o') # options
        d  = dic.get('h','') # description, helper
        r  = dic.get('req',False) # required
        req = 'required' if r else ''
        redstar = '<span style="color: red;">*</span>' if r else ''

        if t == 'str':
            h += f"<li> {id} {redstar}: <input type='text' name='{id}' {req} /> </li> <p>{d}</p>\n"
        if t == 'radio': # selects on of diferent buttons 
            h += f'<li>{id} {redstar}: <br/>'
            h += f'<p>{d}</p>'
            h += '<div class="checkbox-container">'
            for elem in op:
                h += f"<div><input type='radio' name='{id}' value='{elem}' > {elem}</input> </div><br/>\n"
            h += '</div>'
            h += f'</li> \n'

        if t == 'check':# checkbox buttons
            h += f'<li>{id}{redstar}: <br/>'
            h += f'<p>{d}</p>\n'

            h += '<div class="checkbox-container">'
            for elem in op:
                h += f"<div><input type='checkbox' name='{id}' value='{elem}' >  {elem} </input></div> <br/> \n"
            h += '</div></li> '
        # submit files
        if t == 'file':
            h += f'<li>{id}{redstar}: <br/>'
            h += f'</li> <p>{d}</p>\n'
            h += f"<input type='file' name ='{id}' multiple {req} > \n"
    return h + fim

    
def form2file(yc:list,rfo:dict,rfi:dict)->str:
    'takes a form and a list os dicts(from yaml) and stores it in json, csv files'
    global fconf
    #fconf path to yaml

    #rfo → request.forms
    #rfi → request.files
    
    fdict = forms2dict(yc,rfo,rfi)

    title,*l = yc

    name = getName(fconf)
    path = app.config['UPLOAD_FOLDER']

    lId = listId(yc) # list of dentifiers 

    # saving to csv
    if '-c' in c.opt:
        fcsv  = forms2csv (yc,rfo,rfi)
        pathcsv = os.path.join(path, name+'.csv')

        if not os.path.exists(pathcsv):
            f = open(pathcsv, "x")
            f.close()
            f = open(pathcsv,'a')
            f.write(f'{title}\n')
            f.write(','.join(lId)+'\n')
            f.close()

        f = open(pathcsv,'a')
        f.write(fcsv+'\n')
        f.close()

    # saving to json
    if '-j' in c.opt:
        pathjson = os.path.join(path,name+'.json')
        if not os.path.exists(pathjson):
            f = open(pathjson, "x")
            f.close()
            f = open(pathjson,'a')
            f.write(f'{{"title":"{title}"}}\n')
            f.close()
        f = open(pathjson ,'a')
        f.write(json.dumps(fdict)+'\n')
        f.close()

    s = shelve.open( os.path.join(path, name+'.db'))

    #função que busca a chave
    #FIXME
    chave = 'nome'
    if chave in s:
        value = s[chave]
        value.append( fdict )
        s[chave] = value
    else:
        s[chave] = [fdict]
    
    s.close()

def mostra_request(yc:list,rfo:dict,rfi:dict)->str:
    'recieved html for the POST method'
    #yc  → yaml conf
    #rfo → request.forms
    #rfi → request.files
    title,*l = yc
    h = '<!DOCTYPE html>\n'
    h  += f'<h1> Received : {title} </h1> <h4> {date()}</h4><ul>'
    fim = '</ul>'

    for dic in l:
        id = dic['id'] # name
        t  = dic.get('t','str') # types

        if t == 'check':
            h += f'<li> {id}: '
            h += str.join(', ',rfo.getlist(id))
            h += '</li>'

        elif t == 'file':
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


def upload_file(d:dict):
    # d is a multidict(request.files)
    for key in d:
        if d[key]: #d[key] != "" houve submissao de ficheiro
            f = d[key] #name
            c = f.read()
             
            oldname = f.filename
            l = oldname.split(sep='.')
            if len(l) > 1:
                ext = '.'+l[-1]
            else:
                ext = ''

            # calculating the file md5 
            newname = hashlib.md5(c).hexdigest()

            idnt = key
            #adding extension and identification
            finalname = idnt + newname + ext

            name = getName(fconf)
            path = app.config['UPLOAD_FOLDER']

            f = open(os.path.join(path, name+"_submitted_files",finalname),'wb')
            f.write(c)
            f.close()

            #f.save(os.path.join(app.config['UPLOAD_FOLDER'], newname)) 


def forms2csv(yc:list,rfo:dict,rfi:dict)->str:
    'forms(multidict) to coma separated values'
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
            if f.filename == None:
                lo = []
            else:
                lo = [ os.path.join(app.config['UPLOAD_FOLDER'],f.filename) ]
        else:
            lo = rfo.getlist(id)

        acc.append(csv(', '.join(lo)))

    acc.append(date())
    acc.append(request.remote_addr)
    return ','.join(acc)


def csv (word:str)->str:
    'string to csv'
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


def forms2dict(yc:list,rfo:dict,rfi:dict)->dict:
    'convert a form (multidict) to a normal dict'
    #yc  → yaml configuration
    #rfo → request.forms
    #rfi → request.files
    #lo  → list of option filled by user
    title,*l = yc
    acc = {}
    for dic in l:
        lo = []
        ident = dic['id']

        if dic['t'] == 'file':
            f = rfi[ident]
            lo += os.path.join(app.config['UPLOAD_FOLDER'],f.filename)
            lo = ''.join(lo)
        else:
            lo = rfo.getlist(ident)

        if len(lo) == 1:
            acc[ident] = lo[0]
        else:
            acc[ident] = lo


        acc['date'] = date()
        acc['ip'] = request.remote_addr
        print(acc)
    return acc


def listId(yc:list)->list:
    'get the list of identifiers form yaml conf'
    title,*l = yc
    lacc = [] # list of identifiers
    for dic in l:
        lacc.append(dic['id'])
    return lacc

def getkey(yc:list)->str:
    li = listId(yc)
    for ident in li:
        if '!' in ident:
            return sub(r'!','',ident) #find replace
    return None

def date()->str:
    'get the date and time'
    now = datetime.datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")



# request.form
#ImmutableMultiDict([('nome', 'joao afonsoa alvim oliveida dias de almeida'), ('sexo', 'masculino'), ('checkbox', 'vaca'), ('checkbox', 'gato'), ('checkbox', 'crocodilo'), ('checkbox', 'bicho pau')])

#json dumps
#{"nome": "joao afonsoa alvim oliveida dias de almeida", "sexo": "masculino", "checkbox": "vaca"}

# yaml.load
#['Torneio de xadrez viii edição Braga', {'id': 'nome', 't': 'str', 'h': 'descriçao nome completo', 'req': True}, {'id': 'sexo', 't': 'radio', 'o': ['masculino', 'feminino'], 'h': 'atençao abcdefghijklmnopqrstuvwxy', 'req': True}, {'id': 'checkbox', 't': 'check', 'o': ['vaca', 'gato', 'crocodilo', 'bicho pau']}]

def list2formFilled(l:list, form:dict)->str:
    title,*l2 = l
    h = '<!DOCTYPE html>\n'
    h += f"<h1>{title}</h1>\n<form method='post' enctype='multipart/form-data'> <ul>"
    fim = "<input type=submit value='done'/> </ul></form>"

    for dic in l2:
        id = dic['id'] # name
        t  = dic.get('t','str') # types
        op = dic.get('o') # options
        d  = dic.get('h','') # description, helper
        r  = dic.get('req',False) # required
        req = 'required' if r else ''

        if t == 'str':
            val = form.get(id,'')
            h += f"<li> {id}: <input type='text' name='{id}' value='{val}' {req} /> </li> <p>{d}</p>\n"
        if t == 'radio': # selects on of diferent buttons 
            h += f'<li>{id}: <br/>'
            for elem in op:
                if elem in form.get(id,''):
                    val = 'checked="checked"'
                else:
                    val = ''
                h += f"<input type='radio' name='{id}' value='{elem}' {val} {req} >  {elem}</input> <br/>"
            h += f'</li>  <p>{d}</p>\n'
        if t == 'check':# checkbox buttons
            h += f'<li>{id}: <br/>'
            for elem in op:
                if elem in form.get(id,''):
                    val = 'checked'
                else:
                    val = ''
                h += f"<input type='checkbox' name='{id}' value='{elem}' {val} >  {elem}</input> <br/>"
            h += f'</li> <p>{d}</p>\n'
        # submit files
        # FIXME fetch the name
        if t == 'file':
            h += f""" 
            <input type='file' id='files'  name ='{id}' multiple>
            """

    return h + fim
