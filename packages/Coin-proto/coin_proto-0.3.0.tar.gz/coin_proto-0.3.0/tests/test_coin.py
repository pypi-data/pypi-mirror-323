from coin_proto.where_now import add

def test_add():
    r = add(1, 10)
    assert r == 11
