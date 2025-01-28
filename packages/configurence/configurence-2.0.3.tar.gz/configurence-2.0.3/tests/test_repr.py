# -*- coding: utf-8 -*-


def test_repr(config, snapshot) -> None:
    assert repr(config) == snapshot
