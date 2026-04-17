from flask import Flask, request, Response, send_file
import datetime
import psycopg2
import os
import re
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# ☁️ CONEXÃO POSTGRESQL
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS gastos (
    id SERIAL PRIMARY KEY,
    data TEXT,
    descricao TEXT,
    valor REAL,
    categoria TEXT
)
""")
conn.commit()

# 🤖 CATEGORIZAÇÃO
def categorizar(desc):
    if "ifood" in desc or "almoço" in desc:
        return "alimentacao"
    if "uber" in desc or "onibus" in desc:
        return "transporte"
    if "netflix" in desc:
        return "lazer"
    return "outros"

# 🤖 IA SIMPLES
def interpretar(texto):
    texto = texto.lower()

    match = re.search(r'(\d+[.,]?\d*)', texto)
    if not match:
        return None

    valor = float(match.group(1).replace(",", "."))

    if "ontem" in texto:
        data = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        data = datetime.datetime.now()

    descricao = texto
    categoria = categorizar(texto)

    return descricao, valor, data, categoria

# 💾 SALVAR / COMANDOS
def processar(texto):
    texto = texto.lower().strip()
    hoje = datetime.datetime.now()
    data_str = hoje.strftime("%d/%m/%Y")
    mes_atual = hoje.strftime("%m/%Y")

    # 📊 TOTAL
    if texto == "total":
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE data LIKE %s", (f"%/{mes_atual}",))
        total = cursor.fetchone()[0] or 0
        return f"💰 Total do mês: R${total:.2f}"

    # 📊 RESUMO
    if texto == "resumo":
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE data LIKE %s", (f"%/{mes_atual}",))
        total = cursor.fetchone()[0] or 0

        cursor.execute("""
        SELECT categoria, SUM(valor)
        FROM gastos
        WHERE data LIKE %s
        GROUP BY categoria
        """, (f"%/{mes_atual}",))

        dados = cursor.fetchall()

        resp = f"📊 Resumo do mês:\n\n💰 Total: R${total:.2f}\n"
        for cat, val in dados:
            resp += f"{cat}: R${val:.2f}\n"

        return resp

    # 📤 EXPORTAR
    if texto == "exportar":
        cursor.execute("SELECT data, descricao, valor FROM gastos ORDER BY id DESC LIMIT 20")
        dados = cursor.fetchall()

        resp = "📤 Últimos gastos:\n\n"
        for d in dados:
            resp += f"{d[0]} | {d[1]} | R${d[2]:.2f}\n"

        return resp

    # 🗑 LIMPAR
    if texto == "apagar tudo":
        cursor.execute("DELETE FROM gastos")
        conn.commit()
        return "🗑 Tudo apagado!"

    # 🤖 INTERPRETAÇÃO
    interpretado = interpretar(texto)

    if interpretado:
        desc, valor, data_obj, categoria = interpretado
        data_formatada = data_obj.strftime("%d/%m/%Y")

        cursor.execute(
            "INSERT INTO gastos (data, descricao, valor, categoria) VALUES (%s, %s, %s, %s)",
            (data_formatada, desc, valor, categoria)
        )
        conn.commit()

        # 🔔 ALERTA
        cursor.execute("SELECT SUM(valor) FROM gastos WHERE data = %s", (data_formatada,))
        total_dia = cursor.fetchone()[0] or 0

        resp = f"✅ R${valor:.2f} ({categoria})"

        if total_dia > 100:
            resp += f"\n⚠️ Hoje já gastou R${total_dia:.2f}"

        return resp

    return "❌ Não entendi. Ex: 'ifood 30' ou 'gastei 20 ontem'"

# 🔥 WEBHOOK TWILIO
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body")
    resp = processar(msg)

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
<Message>{resp}</Message>
</Response>"""

    return Response(xml, mimetype="application/xml")

# 📈 GRÁFICO
@app.route("/grafico")
def grafico():
    hoje = datetime.datetime.now()
    mes_atual = hoje.strftime("%m/%Y")

    cursor.execute("""
    SELECT categoria, SUM(valor)
    FROM gastos
    WHERE data LIKE %s
    GROUP BY categoria
    """, (f"%/{mes_atual}",))

    dados = cursor.fetchall()

    categorias = [d[0] for d in dados]
    valores = [float(d[1]) for d in dados]

    plt.figure()
    plt.pie(valores, labels=categorias, autopct='%1.1f%%')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

# 👀 HOME
@app.route("/")
def home():
    return "🤖 BOT FINANCEIRO PROFISSIONAL ONLINE"