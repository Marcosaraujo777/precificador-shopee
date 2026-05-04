from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

df = pd.read_excel("Base calculo planilha Shopee APP.xlsx")

# =============================
# CÁLCULO COMPLETO
# =============================
def calcular_preco(row, margem, qtd):

    custo = row["Custo Produto"]
    embalagem = row["Embalagem"]

    marketing = row["Marketing %"]
    ir = row["IR/CSLL %"]
    pis = row["PIS/COFINS %"]
    icms = row["ICMS %"]
    difal = row["DIFAL %"]
    operacional = row["Despesa Operacional %"]

    custo_total = (custo + embalagem) * qtd
    impostos_pct = ir + pis + icms + difal

    preco = 50

    for _ in range(30):

        if preco <= 79.99:
            comissao = 0.20
            fixo = 4
        elif preco <= 99.99:
            comissao = 0.14
            fixo = 16
        elif preco <= 199.99:
            comissao = 0.14
            fixo = 20
        elif preco <= 499.99:
            comissao = 0.14
            fixo = 26
        else:
            comissao = 0.14
            fixo = 26

        total_pct = comissao + impostos_pct + marketing + operacional + margem
        preco = (custo_total + fixo) / (1 - total_pct)

    lucro = preco * margem
    markup = (preco / custo_total - 1) * 100

    return {
        "qtd": qtd,
        "preco": round(preco,2),
        "lucro": round(lucro,2),
        "markup": round(markup,2),
        "custo_total": round(custo_total,2),
        "comissao": round(comissao*100,2),
        "fixo": fixo
    }

# =============================
# ROTA PRINCIPAL
# =============================
@app.route("/", methods=["GET","POST"])
def home():

    resultados = []
    erro = None
    produto_info = None

    if request.method == "POST":

        sku = request.form["sku"]
        margem = float(request.form["margem"])

        produto = df[df["SKU"].astype(str) == sku]

        if produto.empty:
            erro = "SKU não encontrado"
            return render_template("index.html", erro=erro)

        row = produto.iloc[0]

        # 🔥 INFO DO PRODUTO
        produto_info = {
            "nome": row["Descrição"],
            "ean": row["EAN"],
            "sku": sku
        }

        # 🔥 KITS AUTOMÁTICOS
        kits = [1, 2, 3, 5, 10]

        for k in kits:
            calc = calcular_preco(row, margem, k)
            resultados.append(calc)

    return render_template(
        "index.html",
        resultados=resultados,
        erro=erro,
        produto=produto_info
    )

if __name__ == "__main__":
    app.run(debug=True)