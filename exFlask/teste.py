from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return 'hello <h1>teste <h1>'

@app.route('/joao/<int:i>')
def joao(i):
    return f'hello joao <h1> { i*4 } <h1>'

@app.route('/mult/<int:i>/<int:j>') 
def mult(i,j):
    return f'hello joao <h1> { i* j} <h1>'


@app.route('/mult2/<int:i>/<int:j>')
def mult2(i,j):
    return render_template('conta.html', **{'v1':i,'v2':j,'op':'*','r':i*j} )


#------------------------------------------------------------------------

@app.route('/quest',methods = ['GET','POST'])
def quest():
    l = ['nome','idade']

    l2 = [ 'titulo', 
        { 'id':'nome','t':'str', 'h':'descriçao: nome completo'},
        { 'id':'sexo','t':'radio','o': ['masculino','femenino'] , 'h':'descriçao: nome completo', 'req':True },
        { 'id':'teste','t':'check','o': ['asadadas','ola','masculino','femenino'] , 'h':'descriçao: nome completo', 'req':True }]

    if request.method == 'GET':
        #return list2form (l)
        return list2form2 (l2)

    #if request.method == 'POST':
    #    return mostra_request (l,request.form)


def list2form(l:list)->str:
    h = "<form method='post'> <ul>"
    fim = " <input type=submit value='done'/> </ul></form>"
    for elem in l:
        h += f"<li> {elem}: <input type='text' name='{elem}' /> </li>\n"
    #print (h+fim)
    return h + fim
    
def mostra_request(l:list, d:dict)->str:
    h   = "<h1>recebido</h1> <ul>"
    fim = "</ul>"
    for elem in l:
        h += f"<li> {elem}: {d[elem]} </li>\n"
    #print (h+fim)
    return h + fim

#------------------------------------------------------------------------
# complex version of list2form
def list2form2(l:list)->str:
    titulo = l.pop(0)
    h = f"<h1>{titulo}</h1>\n<form method='post'> <ul>"
    fim = "<input type=submit value='done'/> </ul></form>"

    for dic in l:
        id = dic['id'] # name
        t  = dic.get('t','str')  # type
        op = dic.get('o') #options
        d  = dic['h']  # description, helper
        r  = dic.get('req',False)# required

        if t == 'str':
            h += f"<li> {id}: <input type='text' name='{id}' /> </li> <p>{d}</p>\n"

        if t == 'radio':# selectes one varius buttons
            h += f'<li>{id}: <br/>'
            for elem in op:
                h += f"<input type='radio' name='{id}' value='{elem}'>  {elem}</input> <br/>"
            h += '</li>'

        if t == 'check':# checkbox buttons
            h += f'<li>{id}: <br/>'
            for elem in op:
                h += f"<input type='checkbox' name='{id}' value='{elem}'>  {elem}</input> <br/>"
            h += '</li>'

        # inserir ficheiros



    return h + fim

#[ "titulo", { id :"nome", t:['f','m','outro'], h:"descriçao", req:True }]

#if __name__ == '__main__':
app.run()
