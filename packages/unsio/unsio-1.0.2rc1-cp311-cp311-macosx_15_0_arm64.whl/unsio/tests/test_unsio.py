import pytest

import unsio.test.ctestunsio as mytest

def test_gadget3():
    x=mytest.CTestunsio(100000)
    x.testIO(["gadget3"])
    

def test_gadget2():
    x=mytest.CTestunsio(100000)
    x.testIO(["gadget2"])

def test_nemo():
    x=mytest.CTestunsio(100000)
    x.testIO(["nemo"])

