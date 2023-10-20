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
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"

def enviar_email_mes(df):

    email_qualidade = "saulmarinho@edu.unifor.br"
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'sistema@cemag.com.br'
    smtp_password = 'cem@1600'

    corpo_email = df.to_html(index=False)

    data_de_hoje = datetime.date.today()

    # Formata a data para o padrão brasileiro (dia/mês/ano)
    data_formatada = data_de_hoje.strftime('%d/%m/%Y')

    mensagem = MIMEMultipart()
    mensagem['From'] = 'sistema@cemag.com.br'
    mensagem['To'] = email_qualidade
    mensagem['Subject'] = 'Sistema de Calibração - {}'.format(data_formatada) 

    mensagem.attach(MIMEText(corpo_email, 'html'))

    with smtplib.SMTP(smtp_host, smtp_port) as servidor_smtp:
        servidor_smtp.starttls()
        servidor_smtp.login(smtp_user, smtp_password)
        servidor_smtp.send_message(mensagem)
        print('E-mail enviado com sucesso!')

    return "E-MAIL ENVIADO 1"

def calcular_nova_coluna(row):
    if row[18] == 'Email Enviado 1':
        return f'Está atrasada: {row[15] - row[14]} dias'
    elif row[18] == 'Email Enviado 2':
        return 'Hoje é o dia programado para a calibração'
    elif row[18] == 'Email Enviado 3':
        return f'Faltam: 10 dias'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

s = (""" SELECT *, 
		 CASE	 
			WHEN novo_status != 'A Calibrar' THEN 'Email Não Enviado'
			WHEN periodicidade_dias * 0.8 = dias_apos_calibracao THEN 'Email Enviado 1'
			WHEN periodicidade_dias = dias_apos_calibracao THEN 'Email Enviado 2'
			WHEN periodicidade_dias = dias_apos_calibracao + 10 THEN 'Email Enviado 3'
			ELSE ''
		END as novo_status
 FROM (
	 SELECT DISTINCT ON (t3.tag)
		t3.*,
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
		ORDER BY envio.tag, cadastro.data_envio DESC
		) AS t3
    ) as t4
    """)

cur.execute(s)
data = cur.fetchall()
df = pd.DataFrame(data)

df = df[df[16] == 'A Calibrar'].reset_index(drop=True)[[0, 1, 14, 15, 18]]
df = df[df[18] != '']
df['Prazo para calibrar'] = df.apply(calcular_nova_coluna, axis=1)
df = df[[0,1,'Prazo para calibrar']]
df.rename(columns={0:'Tag',1:'Equipamento'},inplace=True)

if not df.empty:
    enviar_email_mes(df)
else:
    print("Email não enviado pois a lista está vazia, execute novamente amanhã")




    