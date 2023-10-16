from flask import Flask,render_template, redirect, url_for, request, session, flash, make_response, Response,jsonify  
import psycopg2  # pip install psycopg2
import psycopg2.extras
from functools import wraps
import pandas as pd
import requests
from datetime import date
import json
import datetime
import logging
import traceback

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
            flash('Usuário ou Senha inválida', category='error')
    return render_template("login.html")

@app.route('/logout')
def logout(): # Botão de logout
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/',methods=['GET','POST'])
@login_required
def inicio(): 

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        
        tagValue= request.form.get('tag')
        
        query = ("""SELECT id, data_calib, link_certificado, ema, emt,
                    ROW_NUMBER() OVER (ORDER BY id) - 1 AS id_tag
                FROM calibracao.tb_registro_tags
                WHERE tag = '{}'""").format(tagValue)
        
        cur.execute(query)
        data = cur.fetchall()
        tabela = pd.DataFrame(data)

        lista_historico = tabela.values.tolist()
    
        for registro in lista_historico:
            if registro[1] is not None:
                registro[1] = registro[1].strftime('%Y-%m-%d')

        conn.commit()
        cur.close()

        return jsonify(lista_historico)

    s = (""" SELECT *,
                CASE 
                    WHEN t3.data_envio IS NOT NULL AND t3.data_chegada IS NULL THEN 'Em Calibração'
                    WHEN t3.periodicidade_dias * 0.8 <= t3.dias_apos_calibracao THEN 'A Calibrar'
                    ELSE 'Calibrado'
                END as novo_status,
                CAST (t3.data_calibracao + (t3.periodicidade || ' months')::interval AS date) as proxima_data_calibracao
            FROM (
                SELECT envio.*, cadastro.data_envio, cadastro.data_chegada, envio.periodicidade * 30 as periodicidade_dias,
                    CURRENT_DATE - DATE(envio.data_calibracao) as dias_apos_calibracao
                FROM calibracao.tb_cadastro_tags  AS envio
                LEFT JOIN calibracao.tb_envio_tags_calibracao AS cadastro
                ON envio.tag = cadastro.tag AND envio.tag = cadastro.tag
                ) AS t3; """)
    
    query = (""" SELECT *
                FROM tb_matriculas;""")
    
    query_historico = """ WITH ranked_tags AS (
                SELECT
                    rt.tag,
                    ct.equipamento,
                    ct.localizacao,
                    rt.data_calib,
                    ROW_NUMBER() OVER (PARTITION BY rt.tag ORDER BY rt.data_calib DESC) AS row_num
                FROM
                    calibracao.tb_registro_tags rt
                    LEFT JOIN calibracao.tb_cadastro_tags ct ON rt.tag = ct.tag
                )
                SELECT tag, equipamento, localizacao,data_calib
                FROM ranked_tags
                WHERE row_num = 1;"""
    
    # query_equip_unidade = ("""SELECT DISTINCT equipamento,faixa_nominal, unidade 
    #                         FROM calibracao.tb_get_equipamentos
    #                         ORDER BY equipamento;""")
    
    # cur.execute(query_equip_unidade)
    # equip_unidade = cur.fetchall()
    # df_data = pd.DataFrame(equip_unidade)
    # equipamentos = df_data[0].values.tolist()
    # equipamentos = list(set(filter(None, equipamentos)))
    # unidades = df_data[1].values.tolist()
    # unidades = list(set(filter(None, unidades)))
    # faixas_nominais = df_data[2].values.tolist()
    # faixas_nominais = list(set(filter(None, faixas_nominais)))

    cur.execute(query_historico)
    data_historico = cur.fetchall()
    tabela = pd.DataFrame(data_historico)
    list_tabela = tabela.values.tolist()

    cur.execute(query)
    data_matricula = cur.fetchall()
    df_data_matricula = pd.DataFrame(data_matricula)
    lista_responsavel = df_data_matricula[2].values.tolist()
    lista_matricula = df_data_matricula[1].values.tolist()
    responsaveis = [f"{mat} - {resp}" for mat, resp in zip(lista_matricula,lista_responsavel)]

    cur.execute(s)
    data = cur.fetchall()
    df = pd.DataFrame(data)
    custom_order = ["A Calibrar", "Em Calibração", "Calibrado"]
    df = df.sort_values(by=16, key=lambda x: x.map({value: i for i, value in enumerate(custom_order)}))
    list_calibracao = df.values.tolist()
    
    return render_template("home_calibracao.html", list_calibracao=list_calibracao,responsaveis=responsaveis, list_tabela=list_tabela)

@app.route('/editar_modal_historico', methods=['POST','GET'])
@login_required
def modal_historico():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':

        dados = json.loads(request.data)

        id = dados['valoresNovos']['id']
        valor_novo_ema = dados['valoresNovos']['valor_novo_ema']
        valor_novo_emt = dados['valoresNovos']['valor_novo_emt']
        valor_novo_link = dados['valoresNovos']['link_novo_certificado']

        nova_data = dados['dataInput']
        if nova_data == '':
            nova_data = dados['valoresNovos']['data_antiga']
            nova_data = datetime.datetime.strptime(nova_data, '%Y-%m-%d') 
        else:
            nova_data = datetime.datetime.strptime(nova_data, '%Y-%m-%d') 
        if valor_novo_link == '':
            valor_novo_link = dados['valoresNovos']['link_certificado']

        print(id,nova_data,valor_novo_ema,valor_novo_emt,valor_novo_link)

        cur.execute("""UPDATE calibracao.tb_registro_tags
                    SET ema = %s,
                        emt = %s,
                        data_calib = %s,
                        link_certificado = %s
                    WHERE id = %s;""",(valor_novo_ema,valor_novo_emt,nova_data,valor_novo_link,id))
        
        conn.commit()
        cur.close()

    return render_template('home_calibracao.html')

# Envio 

@app.route('/modal_data_envio', methods = ['POST'])
@login_required
def envio():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    tagValue = request.form.get('tagValue')
    editar_fornecedor = request.form.get('editar_fornecedor')
    editar_data_envio = request.form.get('editar_data_envio')

    print(tagValue,editar_fornecedor,editar_data_envio)

    cur.execute("""INSERT INTO calibracao.tb_envio_tags_calibracao (tag, fornecedor, data_envio) 
                VALUES (%s,%s,%s)""",(tagValue,editar_fornecedor,editar_data_envio))

    conn.commit()

    conn.close()

    return render_template('home_calibracao.html')

# Cadastro Equipamentos

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

# Cadastro de Tags

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

# Botão Recebimento

@app.route('/editar_tag',methods=['POST'])
@login_required
def editar_tag():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    tagValue= request.form.get('tagValue')
    editar_emt = request.form.get('editar_emt')
    editar_ema = request.form.get('editar_ema')
    editar_data_calib = request.form.get('editar_data_calib')
    editar_url = request.form.get('editar_url')

    cur.execute("""INSERT INTO calibracao.tb_registro_tags (tag, ema, emt, data_calib,link_certificado) 
                VALUES (%s,%s,%s,%s,%s)""",(tagValue,editar_ema,editar_emt,editar_data_calib,editar_url))
    
    cur.execute("""UPDATE calibracao.tb_envio_tags_calibracao
                            SET data_chegada = %s
                            WHERE tag = %s and data_chegada ISNULL;""",(editar_data_calib,tagValue))
    
    cur.execute("""UPDATE calibracao.tb_cadastro_tags
                        SET data_calibracao = %s
                        WHERE tag = %s;""",(editar_data_calib,tagValue))

    conn.commit()

    conn.close()

    return redirect(url_for('inicio'))

@app.route('/relacao')
@login_required
def relacao(): 
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = (""" SELECT *,
                CASE 
                    WHEN data_chegada IS NULL THEN CURRENT_DATE - DATE(data_envio)
                    ELSE DATE(data_chegada) - DATE(data_envio)
                END as contagem_dias
            FROM calibracao.tb_envio_tags_calibracao;""")
    
    cur.execute(query)
    data = cur.fetchall()
    tabela = pd.DataFrame(data)

    list_tags_enviadas = tabela.values.tolist()

    return render_template('relacao.html',list_tags_enviadas=list_tags_enviadas)

@app.route('/atualizando_equip', methods=['POST','GET'])
@login_required
def atualizacao():
 
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    equip = request.form['tag_equipamento']

    query = f"""SELECT DISTINCT (unidade,faixa_nominal)
                FROM calibracao.tb_get_equipamentos
                WHERE equipamento = '{equip}';"""

    cur.execute(query)
    data = cur.fetchall()
    df_data = pd.DataFrame(data)
    unidades_no_equipamento = df_data[0].values.tolist()

    if conn is not None:
        conn.close()

    lista_unidades = []
    lista_faixa_nominal = []

    for tupla in unidades_no_equipamento:
        partes = tupla.strip('()').split(',')
        elemento_0 = partes[0].strip('"')
        elemento_1 = partes[1].strip('"')
        
        if elemento_0 and elemento_0 not in lista_unidades:
            lista_unidades.append(elemento_0)
        
        if elemento_1 and elemento_1 not in lista_faixa_nominal:
            lista_faixa_nominal.append(elemento_1)

    # Se as listas não estiverem vazias, retornar os dados normalmente
    return jsonify({'unidades': lista_unidades, 'faixa_nominal': lista_faixa_nominal})

@app.route('/atualizando_equip_config', methods=['POST','GET'])
@login_required
def atualizacao_config():
 
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        equip = request.form.get('equip')
        unidade = request.form.get('unidade')
        localizacao = request.form.get('localizacao')
        responsavel = request.form.get('responsavel')
        tipoControle = request.form.get('tipoControle')
        periodicidade = request.form.get('periodicidade')
        metodo = request.form.get('metodo')
        faixaNominal = request.form.get('faixaNominal')
        tag = request.form.get('tag')

        print(equip,unidade,localizacao,tag,faixaNominal)

        # cur.execute("""UPDATE calibracao.tb_cadastro_tags
        #             SET equipamento = %s,
        #                 unidade = %s,
        #                 localizacao = %s,
        #                 responsavel = %s,
        #                 tipo_controle = %s,
        #                 periodicidade = %s,
        #                 metodo = %s,
        #                 faixa_nominal = %s
        #             WHERE tag = %s;""",(equip,unidade,localizacao,responsavel,tipoControle,periodicidade,metodo,faixaNominal,tag))
        
        conn.commit()
        cur.close()

        return render_template('home_calibracao.html')
        
    equip = request.form['equip']

    query = f"""SELECT DISTINCT (equipamento,unidade,faixa_nominal)
                FROM calibracao.tb_get_equipamentos
                WHERE equipamento = '{equip}';"""

    cur.execute(query)
    data = cur.fetchall()
    df_data = pd.DataFrame(data)
    unidades_no_equipamento = df_data[0].values.tolist()

    lista_equipamentos = []
    lista_unidades = []
    lista_faixa_nominal = []

    for tupla in unidades_no_equipamento:
        partes = tupla.strip('()').split(',')
        elemento_0 = partes[0].strip('"')
        elemento_1 = partes[1].strip('"')
        elemento_2 = partes[2].strip('"')
        
        if elemento_0 and elemento_0 not in lista_equipamentos:
            lista_equipamentos.append(elemento_0)
        
        if elemento_1 and elemento_1 not in lista_unidades:
            lista_unidades.append(elemento_1)

        if elemento_2 and elemento_2 not in lista_faixa_nominal:
            lista_faixa_nominal.append(elemento_2)

    # Se as listas não estiverem vazias, retornar os dados normalmente
    return jsonify({'equipamentos':lista_equipamentos,'unidades': lista_unidades, 'faixa_nominal': lista_faixa_nominal})

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
