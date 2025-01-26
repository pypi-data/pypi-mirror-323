import starlightproto.stella as star
import pytest


#패키지 목적의 특성 상 대다수의 함수가 명확한 return값 대신 print 표출로 종료되어 pytest에 다소 적합하지 않음

def test_c():
    result = star.select_act("search_c")
    assert not result, "something returns not print(1)"

def test_direction():
    result = star.get_direction(100)
    assert result=="동", "wrong value returns(2)"

def test_observable():
    result = star.is_observable(30, 60)
    assert result, "wrong value returns(3)"


