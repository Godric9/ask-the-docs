from types import SimpleNamespace as P

from ask_the_docs.search import fusion_rrf


def test_rrf():
    a, b, c = P(id="a"), P(id="b"), P(id="c")
    assert [p.id for p in fusion_rrf([a, b, c], [b, c, a])] == ["b", "a", "c"]
