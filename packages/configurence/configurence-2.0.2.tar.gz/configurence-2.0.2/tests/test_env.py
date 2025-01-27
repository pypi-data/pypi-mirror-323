def test_environment(local_config, environ) -> None:
    cfg = local_config.from_environment()

    assert cfg.opt_float is None
    assert cfg.opt_int is None
    assert cfg.opt_str is None
    assert cfg.some_bool is True
    assert cfg.some_float == 2.0
    assert cfg.some_int == 5
    assert cfg.some_other.name == "foo"
    assert cfg.some_str == "bar"
