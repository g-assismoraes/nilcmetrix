def calcular_diferencas_percentuais(lista):
    primeiro = lista[0]
    resultados = []
    for valor in lista[1:]:
        diferenca_percentual = ((valor - primeiro) / primeiro) * 100
        resultados.append(f"{diferenca_percentual:.0f}%")
    return resultados

# Exemplo de uso
lista_floats = [0.30, 0.19, 0.23, 0.21]
diferencas = calcular_diferencas_percentuais(lista_floats)
print("Diferenças percentuais em relação ao primeiro elemento:")
for diferenca in diferencas:
    print(diferenca)
