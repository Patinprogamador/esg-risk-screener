"""Aquecimento 2 - dicionarios e listas de dicionarios.

Isto e exatamente o que fetch.py e report.py fazem: cada noticia e um dict,
e a gente filtra / conta / resume uma lista deles.

Rode:  uv run python pratica2.py
Preencha cada funcao. Quando passar, imprime "OK".
"""


# --- EXEMPLO (ja feito) ---
def pega_titulo(noticia):
    """Entra um dict de noticia, sai o valor da chave 'titulo'."""
    return noticia["titulo"]


# --- EXERCICIO 1 ---
def so_negativas(noticias):
    """Entra uma lista de dicts. Cada dict tem a chave 'sinal'.
    Sai uma lista NOVA so com os dicts onde sinal == 'negativo'.
    Dica: lista vazia, for, if noticia["sinal"] == "negativo": append.
    """
    ...


# --- EXERCICIO 2 ---
def conta_por_categoria(noticias):
    """Entra uma lista de dicts, cada um com a chave 'categoria'.
    Sai um DICT {categoria: quantidade}.
    Ex.: [{"categoria": "s"}, {"categoria": "s"}, {"categoria": "g"}]
         -> {"s": 2, "g": 1}
    Dica: crie um dict vazio. Para cada noticia, pegue cat = noticia["categoria"].
          Se cat ainda nao esta no dict, coloque 0. Depois some 1.
          (ou pesquise: dict.get(cat, 0))
    """
    ...


# --- EXERCICIO 3 ---
def media_severidade(noticias):
    """Entra uma lista de dicts com a chave 'severidade' (numero 0-3).
    Sai a media (soma / quantidade) como float.
    Se a lista estiver vazia, retorne 0.0.
    Dica: trate o caso vazio primeiro (if not noticias: return 0.0).
    """
    ...


# --- EXERCICIO 4 ---
def titulo_do_maior_risco(noticias):
    """Entra uma lista de dicts com as chaves 'titulo' e 'risco' (numero).
    Sai o 'titulo' do dict com o maior 'risco'.
    Dica: guarde um 'melhor = noticias[0]'. Percorra o resto; se
          noticia["risco"] > melhor["risco"], troque. No fim, return melhor["titulo"].
    """
    ...


# ------------------------------------------------------------------
# TESTES - nao mexa aqui.
# ------------------------------------------------------------------
if __name__ == "__main__":
    dados = [
        {"titulo": "Vazamento em refinaria", "categoria": "ambiental", "sinal": "negativo", "severidade": 3, "risco": 100},
        {"titulo": "Empresa troca por energia solar", "categoria": "ambiental", "sinal": "positivo", "severidade": 1, "risco": 0},
        {"titulo": "Greve por horas extras", "categoria": "social", "sinal": "negativo", "severidade": 2, "risco": 75},
        {"titulo": "Juros mantidos", "categoria": "nenhuma", "sinal": "neutro", "severidade": 0, "risco": 10},
        {"titulo": "Fraude contabil investigada", "categoria": "social", "sinal": "negativo", "severidade": 3, "risco": 100},
    ]

    assert pega_titulo(dados[0]) == "Vazamento em refinaria"

    neg = so_negativas(dados)
    assert len(neg) == 3
    assert all(n["sinal"] == "negativo" for n in neg)
    assert so_negativas([]) == []

    assert conta_por_categoria(dados) == {"ambiental": 2, "social": 2, "nenhuma": 1}
    assert conta_por_categoria([]) == {}

    assert media_severidade(dados) == 1.8
    assert media_severidade([]) == 0.0

    assert titulo_do_maior_risco(dados) in ("Vazamento em refinaria", "Fraude contabil investigada")

    print("OK - todos os testes passaram!")
