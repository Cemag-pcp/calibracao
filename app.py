from flask import Flask,render_template, redirect, url_for, request, session, flash, make_response, Response,jsonify  
import psycopg2  # pip install psycopg2
import psycopg2.extras
from functools import wraps
import pandas as pd
import requests

app = Flask(__name__)
app.secret_key = "calibracao"

DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"

def login_required(func): # Lógica do parâmetro de login_required, onde escolhe quais páginas onde apenas o usuário logado pode acessar
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur.execute(
            "SELECT * FROM calibracao.tb_usuario WHERE email = %s AND senha = %s", (username, password))
        user = cur.fetchone()
   
        if user is not None:
            session['loggedin'] = True
            session['username'] = user['email']
            return redirect(url_for('inicio'))
        else:
            pass
    return render_template("login.html")

@app.route('/logout')
def logout(): # Botão de logout
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/')
@login_required
def inicio(): 
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    s = (""" SELECT
                *,
                CAST (data_calibracao+(periodicidade||'months')::interval AS date) 
            FROM calibracao.tb_cadastro_tags """)
    
    query = (""" SELECT *
                FROM tb_matriculas;""")
    
    cur.execute(query)
    data_matricula = cur.fetchall()
    df_data_matricula = pd.DataFrame(data_matricula)
    lista_responsavel = df_data_matricula[2].values.tolist()
    lista_matricula = df_data_matricula[1].values.tolist()
    responsaveis = [f"{mat} - {resp}" for mat, resp in zip(lista_matricula,lista_responsavel)]

    cur.execute(s)
    data = cur.fetchall()
    df = pd.DataFrame(data)

    list_calibracao = df.values.tolist()

    return render_template("home_calibracao.html", list_calibracao=list_calibracao,responsaveis=responsaveis)

@app.route('/cadastro_equip', methods=['GET','POST'])
@login_required
def cadastro_equip(): 

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':

        equipamento = request.form.get('equipamento')
        fabricante = request.form.get('fabricante')
        grandeza = request.form.get('grandeza')
        unidade = request.form.get('unidade')
        nominal = request.form.get('nominal')
        faixa_calibracao = request.form.get('faixa_calibracao')
        preco = request.form.get('preco')

        cur.execute("INSERT INTO calibracao.tb_get_equipamentos (equipamento, fabricante, grandeza, unidade, faixa_nominal, faixa_calibracao, preco) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (equipamento, fabricante, grandeza, unidade, nominal, faixa_calibracao, preco))
            
        conn.commit()

        conn.close()

    return render_template("cadastro.html")

@app.route('/cadastro', methods=['GET','POST'])
@login_required
def cadastro(): 

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':

        tag = request.form.get('tag')
        equipamento = request.form.get('tag_equipamento')
        controle = request.form.get('tag_controle')
        metodo = request.form.get('tag_metodo')
        unidade = request.form.get('tag_unidade')
        responsavel = request.form.get('tag_responsavel')
        data_tag = request.form.get('tag_data')
        periodicidade = request.form.get('tag_periodicidade')
        nominal = request.form.get('tag_nominal')
        localizacao = request.form.get('tag_localizacao')

        print(tag,equipamento,unidade,localizacao,responsavel,controle,data_tag,periodicidade,metodo,nominal)

        # cur.execute("""INSERT INTO calibracao.tb_cadastro_tags (tag,equipamento,unidade,localizacao,
        #             responsavel,tipo_controle,data_calibracao,periodicidade,metodo,faixa_nominal) 
        #             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(tag,equipamento,unidade,localizacao,responsavel,controle,
        #                                                        data_tag,periodicidade,metodo,nominal))
        # conn.commit()

        # conn.close()

        return redirect(url_for('cadastro'))

    s = ("""SELECT DISTINCT equipamento, unidade 
            FROM calibracao.tb_get_equipamentos
            ORDER BY equipamento;""")
    
    query = (""" SELECT *
                FROM tb_matriculas;""")
    
    cur.execute(query)
    data_matricula = cur.fetchall()
    df_data_matricula = pd.DataFrame(data_matricula)
    lista_responsavel = df_data_matricula[2].values.tolist()
    lista_matricula = df_data_matricula[1].values.tolist()
    responsaveis = [f"{mat} - {resp}" for mat, resp in zip(lista_matricula,lista_responsavel)]

    cur.execute(s)
    data = cur.fetchall()
    df_data = pd.DataFrame(data)
    equipamentos = df_data[0].values.tolist()
    equipamentos = list(set(filter(None, equipamentos)))
    unidades = df_data[1].values.tolist()
    unidades = list(set(filter(None, unidades)))
    
    return render_template("cadastro.html",equipamentos=equipamentos,responsaveis=responsaveis,unidades=unidades)

@app.route('/cadastrar_tag', methods=['POST'])
@login_required
def cadastrar_tag(): 
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    tag = request.form.get('tag')
    equipamento = request.form.get('tag_equipamento')
    controle = request.form.get('tag_controle')
    metodo = request.form.get('tag_metodo')
    unidade = request.form.get('tag_unidade')
    responsavel = request.form.get('tag_responsavel')
    data_tag = request.form.get('tag_data')
    periodicidade = request.form.get('tag_periodicidade')
    nominal = request.form.get('tag_nominal')
    localizacao = request.form.get('tag_localizacao')
    status = request.form.get('tag_status')

    print(tag,equipamento,unidade,localizacao,responsavel,controle,data_tag,periodicidade,metodo,nominal,status)
    
    cur.execute(""" select MAX(CAST (RIGHT (tag,3) as int)) + 1 as id_tag 
                    from calibracao.tb_cadastro_tags
                    WHERE tag LIKE '%{}%';""".format(tag))
    
    lista_tags = cur.fetchall()

    valor_lista_tags = lista_tags[0]

    if valor_lista_tags == [None]:
        lista_tags = 1
        nova_tag =  tag + '-00' + str(lista_tags)
    elif valor_lista_tags[0] >= 10:
        nova_tag = tag + '-0' + str(lista_tags[0][0])
    else:
        nova_tag = tag + '-00' + str(lista_tags[0][0])

    cur.execute("""INSERT INTO calibracao.tb_cadastro_tags (tag,equipamento,unidade,localizacao,
                responsavel,tipo_controle,data_calibracao,periodicidade,metodo,faixa_nominal,status) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(nova_tag,equipamento,unidade,localizacao,responsavel,controle,
                                                           data_tag,periodicidade,metodo,nominal,status))
    conn.commit()

    conn.close()

    return redirect(url_for('cadastro'))

@app.route('/editar_tag',methods=['POST'])
@login_required
def editar_tag():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    tag = request.form.get('tag')
    emt = request.form.get('emt')
    ema = request.form.get('ema')
    data_calib = request.form.get('data_calib')

    print(tag,emt,ema,data_calib)

    return render_template('home_calibracao.html')

@app.route('/relacao')
@login_required
def relacao(): 
    
    return render_template("relacao.html")

@app.route('/atualizando_equip', methods=['POST','GET'])
@login_required
def atualizacao():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    equip = request.form['tag_equipamento']

    query = (f"""   SELECT DISTINCT (unidade,faixa_nominal)
                    FROM calibracao.tb_get_equipamentos
                    WHERE equipamento = '{equip}';""")

    cur.execute(query)
    data = cur.fetchall()
    df_data = pd.DataFrame(data)
    unidades_no_equipamento = df_data[0].values.tolist()
    # print(unidades_no_equipamento)

    lista_unidades = []
    lista_faixa_nominal = []

    for tupla in unidades_no_equipamento:
        partes = tupla.strip('()').split(',')
        elemento_0 = partes[0].strip('"')
        elemento_1 = partes[1].strip('"')
        
        # Verifique se o elemento da posição 0 não é vazio e não está na lista
        if elemento_0 and elemento_0 not in lista_unidades:
            lista_unidades.append(elemento_0)
        
        # Verifique se o elemento da posição 1 não é vazio e não está na lista
        if elemento_1 and elemento_1 not in lista_faixa_nominal:
            lista_faixa_nominal.append(elemento_1)  

    return jsonify({'unidades': lista_unidades, 'faixa_nominal': lista_faixa_nominal})

def tabela_inicial():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    df = pd.read_excel(r'C:\Users\TI\teste\Calibração\Controle Plano Mestre de Calibração.xlsx')

    df.columns.values[4] = 'Faixa de calibração'

    df = df.iloc[:, :-1]

    df = df.fillna('')

    for i in range(len(df)):

        sql = """ INSERT INTO calibracao.tb_get_equipamentos (equipamento, faixa_nominal, unidade, grandeza, faixa_calibracao, fabricante) VALUES (%s,%s,%s,%s,%s,%s) """
        
        values = (df['Equipamento'][i], df['Faixa nominal'][i], df['Un'][i], df['Grandeza'][i], df['Faixa de calibração'][i], df['Fabricante'][i])
        
        cur.execute(sql, values)   

    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
