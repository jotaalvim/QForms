import xmlParser
import sys
import os
import json
import unidecode

from flask import Flask, render_template, request, redirect

UPLOAD_FOLDER = './files/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# exemplo: python3 app.py inputTemplate.xml -csv ou python3 app.py inputTemplate.xml results.json
if (len(sys.argv) < 3):
    print("Não passou ficheiro xml de config ou nome do ficheiro de resposta")
    print("Exemplo: python3 app.py inputTemplate.xml results.json")
    exit()

check_last = sys.argv[2].split('.')
if check_last[-1] != "json" and check_last[-1] != "csv":
    print("Apenas devolve ficheiros json e csv")
    exit()

info = xmlParser.parseFile(sys.argv[1])
results = sys.argv[2]

html = xmlParser.createHTML(info)

@app.route('/')
def base():
    return html 

@app.route('/upload', methods = ['POST'])
def upload():
    dic = {}
    first = True
   
    for key in request.form:
        value = [unidecode.unidecode(x) for x in request.form.getlist(key)]
        if len(value) == 1: value = value[0]
        dic[unidecode.unidecode(key)] = value

    for key in request.files:
        if request.files[key]:
            f = request.files[key]
            newname = f.filename
            i = 0
            while os.path.isfile(f'{app.config["UPLOAD_FOLDER"]}/{newname}'):
                separado = f.filename.split('.')
                last = separado.pop(1)
                newname = '.'.join(separado) + f'({i}).' + last
                i += 1
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], newname))
            dic[unidecode.unidecode(key)] = unidecode.unidecode(newname)


        

    print(dic)

    if (results.split('.')[1] == "csv"):
        if (not os.path.isfile(f'./{results}')):
            with open(f'./{results}','w') as f:
                headers = ""
                for x in dic.keys():
                    headers += f'''{x},'''
                f.write(headers[:-1]+'\n')

        with open(f'./{results}','a') as f:
            for x in dic.values():
                if first:
                    f.write(f'''{x}''')
                    first = False 
                else:
                    f.write(',')
                    f.write(f'''{x}''')
            
            f.write('\n')

    elif (results.split('.')[1] == "json"):
        data = []
        if (not os.path.isfile(f'./{results}')):
            with open(f'./{results}','w') as f:
                f.write('[]')
        
        with open(f'./{results}','r') as f:
            data = json.load(f)

        data.append(dic)

        with open(f'./{results}','w') as f:
            f.write(json.dumps(data,indent=4))

    return redirect("/")

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=8000)




# exemplo da estrutura do dicionario que resulta de dar parse ao xml
{
    'id': 'Formulário Teste', 
    
    'item1': 
    {
        'type': 'number', 
        'text': 'Idade'
    }, 
    'item2': 
    {
        'type': 'text', 
        'text': 'Nome'
    }, 
    'item3': 
    {
        'type': 'radio', 
        'title': 'Sexo', 
        'text': ['Masculino', 'Feminino', 'Outro']
    }, 
    'item4': 
    {
        'type': 'checkbox', 
        'title': 'Cores', 
        'text': ['Vermelho', 'Azul', 'Amarelo']
    }, 
    'item5': 
    {
        'type': 'select', 
        'title': 'Estação', 
        'text': ['Verão', 'Primavera', 'Outono', 'Inverno']
    }, 
    'item6': 
    {
        'type': 'file', 
        'text': 'Fotografia'
    }
}


