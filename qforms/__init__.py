"""
Qforms: google-forms like local form generator tool
"""

from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import sys, os, yaml, json, jjcli, waitress
import hashlib, shelve, datetime

import csv
__version__ = "0.4"
app = Flask(__name__)

conf={}
c = None
fconf = None


def main():
    """Personal form generator 

    Usage: qforms [options] config.yaml
    Options: 
        -h : this help
        -c : export to <title>.csv
        -d <domain> : server host = domain (def: localhost) 
    """
    # -s <path>: allow user to load their own css file

    global c,conf, fconf
    c = jjcli.clfilter(opt="s:nd:cjh",doc=main.__doc__)

    if '-h' in c.opt:
        print(
        """Usage: qforms [options] [config.yaml]
        Options: 
            -h : this help
            -c : export to <title>.csv
            -d <domain> : server host = domain (def: localhost) 
        """)
    # -s <path>: allow user to load their own css file
        sys.exit(0)

    fconf = c.args[-1]  # last argument is the yaml config
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


    if '-n' in c.opt:
        run_with_ngrok(app)
        app.run()

    elif '-d' in c.opt:
        print(f'[host] {c.opt["-d"]}:8080/quest')
        waitress.serve(app, host=c.opt["-d"], port=8080)
    else:
        print(f'[host] localhost:8080/quest')
        waitress.serve(app, host="localhost", port=8080)



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

        list_files = upload_file(request.files)

        form2file(conf, request.form, request.files, list_files)

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





css = """
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

        <!--------------------------------------------------------------->
        #files-area{
    	width: 30%;
    	margin: 0 auto;
    }
    .file-block{
    	border-radius: 10px;
    	background-color: rgba(144, 163, 203, 0.2);
    	margin: 5px;
    	color: initial;
    	display: inline-flex;
    	& > span.name{
    		padding-right: 10px;
    		width: max-content;
    		display: inline-flex;
    	}
    }
    .file-delete{
    	display: flex;
    	width: 24px;
    	color: initial;
    	background-color: #6eb4ff00;
    	font-size: large;
    	justify-content: center;
    	margin-right: 3px;
    	cursor: pointer;
    	&:hover{
    		background-color: rgba(144, 163, 203, 0.2);
    		border-radius: 10px;
    	}
    	& > span{
    		transform: rotate(45deg);
    	}
    }
    """


def list2form(l:list)->str:
    title,*l2 = l
    h = '<!DOCTYPE html>\n'
    
    
    h += """<head> 
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

        """


    h += '<style>'

    # Allow user to upload their ows css style
    if '-s' in c.opt :
        with open (c.opt['-s'], 'r') as f:
            content = f.read()
            h += content

    else:
        h += css
    h += '</style> </head>'

#    h += "<body>"
    h += f"<h1>{title}</h1>\n"

    h += "<form method='post' enctype='multipart/form-data'> <ul>"

    fim = '</br></br><input type="submit" value="Submit Form" style="padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;" />'

    #fim = "</br></br><input type=submit value='Submit Form'/> </ul></form>"

    for dic in l2:
        id = dic['id'] # name
        t  = dic.get('t','str') # types
        op = dic.get('o') # options
        d  = dic.get('h','') # description, helper
        r  = dic.get('r',False) # required
        req     = 'required' if r else ''
        redstar = '<span style="color: red;">*</span>' if r else ''

        if t == 'str':
            h += f"<li> <h3>{id}{redstar} </h3> "
            h+= f'<p>{d}</p>\n'
            #h+= f"<input type='text' name='{id}' {req} /> </li> "
            h+= f'<textarea  name="{id}" rows="1" cols="50" {req} ></textarea>'

        if t == 'radio': # selects on of diferent buttons 
            h += f'<li> <h3>{id}{redstar} </h3> '
            h += f'<p>{d}</p>'
            h += '<div class="checkbox-container">'
            for elem in op:
                h += f"<div><input type='radio' name='{id}' value='{elem}' {req} > {elem}</input> </div><br/>\n"
            h += '</div>'
            h += f'</li> \n'

        if t == 'check':# checkbox buttons
            h += f'<li> <h3>{id}{redstar} </h3>'
            h += f'<p>{d}</p>\n'

            h += '<div class="checkbox-container">'
            for elem in op:
                h += f"<div><input type='checkbox' name='{id}' value='{elem}' >  {elem} </input></div> <br/> \n"
            h += '</div></li> '
        # submit files
        if t == 'file':
            h += f'<li><h3>{id}{redstar}</h3>'
            h += f'</li> <p>{d}</p>\n'
            #h += f"<input type='file' name ='{id}' multiple {req} > \n"

                    # <a class="btn btn-primary text-light" role="button" aria-disabled="false">+ Add</a>
            h += """
            <p class="mt-5 text-center">
                <label for="attachment">
                    <a class="btn text-light" role="button" aria-disabled="false" style="background-color: #517891 ; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">+ Add</a>

                    
                </label>
            """
            h+= f' <input type="file" name="{id}" id="attachment" style="visibility: hidden; position: absolute;" multiple/>'
                
            h+= """
            </p>
            <p id="files-area">
                <span id="filesList">
                    <span id="files-names"></span>
                </span>
            </p> </li>
            """
    # Thing responsible for file slection and removel
    h += """ <script> const dt = new DataTransfer(); $("#attachment").on('change', function(e){ for(var i = 0; i < this.files.length; i++){ let fileBloc = $('<span/>', {class: 'file-block'}), fileName = $('<span/>', {class: 'name', text: this.files.item(i).name}); fileBloc.append('<span class="file-delete"><span>+</span></span>') .append(fileName); $("#filesList > #files-names").append(fileBloc); }; for (let file of this.files) { dt.items.add(file); } this.files = dt.files; $('span.file-delete').click(function(){ let name = $(this).next('span.name').text(); $(this).parent().remove(); for(let i = 0; i < dt.items.length; i++){ if(name === dt.items[i].getAsFile().name){ dt.items.remove(i); continue; } } document.getElementById('attachment').files = dt.files; }); }); </script> """




    return h + fim

    
def form2file(yc:list,rfo:dict,rfi:dict, list_files)->str:
    'takes a form and a list os dicts(from yaml) and stores it in json, csv files'
    global fconf
    #fconf path to yaml

    #rfo → request.forms
    #rfi → request.files
    
    fdict = forms2dict(yc,rfo,rfi, list_files)

    title,*l = yc

    name = getName(fconf)
    path = app.config['UPLOAD_FOLDER']
    pathcsv = os.path.join(path, name+'.csv')



    lId = listId(yc) # list of dentifiers 

    # saving to csv
    if '-c' in c.opt:
        if not os.path.exists(pathcsv):
            f = open(pathcsv, "x")
            f.close()
            f = open(pathcsv,'a')
            f.write(f'{title}\n')
            f.write(','.join(lId)+'\n')
            f.close()

        fcsv  = forms2csv (yc,rfo,rfi,list_files)

        with open(pathcsv,'a') as f:
            f.write(fcsv+'\n')

    # saving to json
    pathjson = os.path.join(path,name+'.json')

    if not os.path.exists(pathjson):
        f = open(pathjson, "x")
        f.close()
        f = open(pathjson,'a')
        f.write('{ "title":  "'+ title+'", "questions" : [] , "forms" : []}')
        f.close()

    with open(pathjson, 'r') as json_file:
        data = json.load(json_file)
        data['questions'] = list(set(data['questions']).union(set(lId)))  # perserve old identifiers in case we delete something
        data['forms'].append(fdict) 
        #print(data)

    with open(pathjson, 'w') as json_file:
        json.dump(data, json_file, indent=4) 

    #f = open(pathjson ,'a') # append mode
    #f.write(json.dumps(fdict)+'\n')
    #f.close()

    #s = shelve.open( os.path.join(path, name+'.db'))
    #função que busca a chave
    #FIXME
    #chave = 'nome'
    #if chave in s:
    #    value = s[chave]
    #    value.append( fdict )
    #    s[chave] = value
    #else:
    #    s[chave] = [fdict]
    #
    #s.close()

def mostra_request(yc:list,rfo:dict,rfi:dict)->str:
    'recieved html for the POST method'
    #yc  → yaml conf
    #rfo → request.forms
    #rfi → request.files
    title,*l = yc
    h = '<!DOCTYPE html>\n'
    h += "<style>" + css + "</style>"
    h  += f'<h1> Received : {title} </h1>'

    h += '<h1 style="padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;" > ✓ </h1>'

    h += f'<h4> {date()}</h4><ul>'
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


def upload_file(d):
    # d is a multidict(request.files)
    list_files = []
    for key in d:
        uploaded_files = d.getlist(key)

        # f is a FileStorage object
        # https://tedboy.github.io/flask/generated/generated/werkzeug.FileStorage.html
        for f in uploaded_files:
            #print(f.content_type, f.mimetype, f.content_length)
            if f.filename != '':

                c = f.read()

                # calculating the file md5 
                newname = hashlib.md5(c).hexdigest()
                 
                oldname = f.filename
                l = oldname.split(sep='.')
                if len(l) > 1:
                    ext = '.'+l[-1]
                else:
                    ext = ''

                #adding extension and identification
                finalname = key + "-" + ".".join(l[:-1]) + "-" + newname + ext

                list_files.append((key,finalname))

                name = getName(fconf)
                path = app.config['UPLOAD_FOLDER']

                file = open(os.path.join(path, name+"_submitted_files",finalname),'wb')
                file.write(c)
                file.close()

                #f.save(os.path.join(app.config['UPLOAD_FOLDER'], newname)) 
    return list_files


def forms2csv(yc:list,rfo:dict,rfi:dict,list_files)->str:
    'forms(multidict) to coma separated values'
    # l yaml conf
    #rfo → request.forms
    #rfi → request.files
    title,*l = yc
    lId = listId(yc) # list of identifiers
    acc = []
    for dic in l:
        lo = []
        ident = dic['id']

        if 't' in dic and dic['t'] == 'file':
            filtered_by_ident = [ n for i,n in filter_by_fst(ident, list_files)] 
            list_paths = [ os.path.join(app.config['UPLOAD_FOLDER'], x) for x in filtered_by_ident ]

            lo = list_paths
        else:
            lo = rfo.getlist(ident)

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


def forms2dict(yc:list,rfo:dict,rfi:dict,list_files)->dict:
    'convert a form (multidict) to a normal dict'
    #yc  → yaml configuration
    #rfo → request.forms
    #rfi → request.files
    #lo  → list of option filled by user
    #list_files → list of new files names

    title,*l = yc
    acc = {}
    for dic in l:
        lo = []
        ident = dic['id']

        if 't' in dic and dic['t'] == 'file':

            filtered_by_ident = [ n for i,n in filter_by_fst(ident, list_files)]

            list_paths = [ os.path.join(app.config['UPLOAD_FOLDER'], x) for x in filtered_by_ident ]
            #print(filtered_by_ident)
            #print(list_paths)
            lo = list_paths
        else:
            lo = rfo.getlist(ident)

        acc[ident] = lo[0] if len(lo) == 1 else lo

        acc['date'] = date()
        acc['ip'] = request.remote_addr
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

def filter_by_fst( pattern , list_t ):
    return list( filter ( lambda x: x[0] == pattern, list_t) )




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
        r  = dic.get('r',False) # required
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
