from toolkit_common.cli.exit_codes import ExitCode


def test_exit_codes():
    assert ExitCode.SUCCESS == 0
    assert ExitCode.BLOCKING_FINDINGS == 1
    assert ExitCode.INVALID_CONFIG == 2
    assert ExitCode.RUNTIME_ERROR == 3
    assert ExitCode.UNSUPPORTED == 4
