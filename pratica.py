"""Aquecimento: escreva o corpo de cada funcao. Rode:  uv run python pratica.py"""


# --- EXEMPLO (ja feito, serve de modelo) ---
def dobro(n):
    """Entra um numero, sai o dobro dele."""
    return n * 2


# --- EXERCICIO 1 ---
def soma_lista(numeros):
    """Entra uma lista de numeros, sai a soma de todos.
    Ex.: soma_lista([1, 2, 3]) -> 6
    Dica: comece com total = 0, percorra a lista com 'for', va somando, retorne total.
    """
    total = 0
    for n in numeros:
        total = total + n
    return total


# --- EXERCICIO 2 ---
def maiusculas(palavras):
    """Entra uma lista de textos, sai uma lista NOVA com cada texto em MAIUSCULO.
    Ex.: maiusculas(["oi", "tchau"]) -> ["OI", "TCHAU"]
    Dica: crie uma lista vazia, percorra com 'for', use .upper() em cada uma,
          .append() na lista nova, retorne a lista nova.
    """
    nova = []
    for palavra in palavras:
        nova.append(palavra.upper())
    return nova


# --- EXERCICIO 3 ---
def maiores_que(numeros, minimo):
    """Entra uma lista de numeros e um valor 'minimo'.
    Sai uma lista so com os numeros MAIORES que 'minimo'.
    Ex.: maiores_que([1, 5, 2, 9], 3) -> [5, 9]
    Dica: lista vazia, 'for', dentro do for um 'if numero > minimo:', .append().
    """
    resultado = []
    for numero in numeros:
        if numero > minimo:
            resultado.append(numero)
    return resultado


# ------------------------------------------------------------------
# TESTES - nao mexa aqui. Rode o arquivo; se passar, imprime "OK".
# ------------------------------------------------------------------
if __name__ == "__main__":
    assert dobro(4) == 8

    assert soma_lista([1, 2, 3]) == 6
    assert soma_lista([]) == 0
    assert soma_lista([10, 20, 30, 40]) == 100

    assert maiusculas(["oi", "tchau"]) == ["OI", "TCHAU"]
    assert maiusculas([]) == []
    assert maiusculas(["Python"]) == ["PYTHON"]

    assert maiores_que([1, 5, 2, 9], 3) == [5, 9]
    assert maiores_que([1, 2, 3], 10) == []
    assert maiores_que([7, 7, 7], 5) == [7, 7, 7]

    print("OK - todos os testes passaram!")
