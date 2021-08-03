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
    if request.method == 'GET':
        return list2form (l)

    if request.method == 'POST':
        return mostra_request (l,request.form)


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


#if __name__ == '__main__':
app.run()
