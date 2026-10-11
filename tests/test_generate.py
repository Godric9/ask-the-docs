from ask_the_docs.generate import extraire_numeros


def test_ordre_et_sans_doublon():
    assert extraire_numeros("A [1]. B [3]. C [1].") == [1, 3]


def test_citations_collees():
    assert extraire_numeros("A [2][4].") == [2, 4]


def test_aucune_citation():
    assert extraire_numeros("Pas de source.") == []


def test_ignore_ce_qui_n_est_pas_un_numero():
    assert extraire_numeros("Voir [a] et [12].") == [12]
