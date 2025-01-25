from cobstickettoy.cobstickettoy import today_num

def test_t1():
    g = today_num(1,10)
    assert g >= 1
    assert g <= 10
