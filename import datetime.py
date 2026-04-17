import datetime

ARQUIVO = "gastos.txt"

# Função para adicionar gasto
def adicionar_gasto():
    descricao = input("Descrição do gasto: ")
    valor = float(input("Valor (R$): ").replace(",", "."))

    data = datetime.datetime.now().strftime("%d/%m/%Y")

    with open(ARQUIVO, "a") as f:
        f.write(f"{data} | {descricao} | {valor}\n")

    print("✅ Gasto anotado com sucesso!")

# Função para ver gastos
def ver_gastos():
    try:
        with open(ARQUIVO, "r") as f:
            print("\n📋 Seus gastos:\n")
            print(f.read())
    except FileNotFoundError:
        print("Nenhum gasto registrado ainda.")

# Função para calcular total do mês
def total_mes():
    total = 0

    try:
        with open(ARQUIVO, "r") as f:
            for linha in f:
                partes = linha.strip().split(" | ")
                valor = float(partes[2])
                total += valor

        print(f"\n💰 Total gasto: R$ {total:.2f}")
    except FileNotFoundError:
        print("Nenhum gasto registrado.")

# Menu
while True:
    print("\n=== CONTROLE FINANCEIRO ===")
    print("1 - Adicionar gasto")
    print("2 - Ver gastos")
    print("3 - Ver total gasto")
    print("4 - Sair")

    opcao = input("Escolha: ")

    if opcao == "1":
        adicionar_gasto()
    elif opcao == "2":
        ver_gastos()
    elif opcao == "3":
        total_mes()
    elif opcao == "4":
        print("Saindo...")
        break
    else:
        print("Opção inválida!")