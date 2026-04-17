from flask import Flask, request
import datetime

app = Flask(__name__)

ARQUIVO = "gastos.txt"

def salvar_gasto(texto):
    try:
        texto = texto.lower().strip()
        hoje = datetime.datetime.now()
        mes_atual = hoje.strftime("%m/%Y")

        # 🗑 APAGAR TUDO
        if texto == "apagar tudo":
            open(ARQUIVO, "w").close()
            return "🗑 Histórico apagado!"

        # 📅 APAGAR SÓ O MÊS ATUAL
        elif texto == "limpar mes":
            novas_linhas = []

            try:
                with open(ARQUIVO, "r") as f:
                    for linha in f:
                        data, desc, valor = linha.strip().split(" | ")

                        if mes_atual not in data:
                            novas_linhas.append(linha)

                with open(ARQUIVO, "w") as f:
                    f.writelines(novas_linhas)

                return "📅 Gastos do mês atual apagados!"

            except FileNotFoundError:
                return "Nenhum gasto encontrado."

        # 📤 EXPORTAR HISTÓRICO
        elif texto == "exportar":
            try:
                with open(ARQUIVO, "r") as f:
                    dados = f.read()

                if not dados:
                    return "Nenhum gasto registrado."

                return f"📤 Histórico:\n\n{dados}"

            except FileNotFoundError:
                return "Nenhum gasto registrado."

        # 💰 TOTAL DO MÊS
        elif texto == "total":
            total = 0

            try:
                with open(ARQUIVO, "r") as f:
                    for linha in f:
                        data, desc, valor = linha.strip().split(" | ")

                        if mes_atual in data:
                            total += float(valor)

                return f"💰 Total do mês: R${total:.2f}"

            except FileNotFoundError:
                return "Nenhum gasto ainda."

        # 💸 SALVAR GASTO
        partes = texto.split()

        if len(partes) < 2:
            return "❌ Use: mercado 30"

        descricao = partes[0]
        valor = float(partes[1].replace(",", "."))

        data = hoje.strftime("%d/%m/%Y")

        with open(ARQUIVO, "a") as f:
            f.write(f"{data} | {descricao} | {valor}\n")

        return f"✅ Anotado PH!\n{descricao} - R${valor}"

    except Exception as e:
        return f"Erro: {e}"

@app.route("/webhook", methods=["POST"])
def webhook():
    mensagem = request.form.get("Body")

    resposta = salvar_gasto(mensagem)

    return f"""
    <Response>
        <Message>{resposta}</Message>
    </Response>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)