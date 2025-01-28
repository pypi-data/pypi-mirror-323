# -*- coding: utf-8 -*-


def test_default_file(local_config, local_filename) -> None:
    assert local_config.file == local_filename


def test_default_global_file(global_config, global_filename) -> None:
    assert global_config.file == global_filename


def test_no_file(local_config_no_file, local_filename) -> None:
    assert local_config_no_file.file == local_filename


def test_save_file(local_config, local_filename, write_config_file) -> None:
    local_config.to_file()
    write_config_file.assert_called_with(
        local_filename,
        dict(
            opt_bool=None,
            opt_float=None,
            opt_int=None,
            opt_str=None,
            some_bool=True,
            some_float=1.0,
            some_int=1,
            some_other="default",
            some_str="some_str",
        ),
    )
