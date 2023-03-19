import sys
from protodeep.cli import parse_and_run
import pytest
from pathlib import Path


def _run_and_check(capsys, expected_data, args):
    """Helper function that invokes protodeep and validates the output"""
    __tracebackhide__ = True
    sys.argv = ['test_deep', '-t', 'protobuf'] + args
    parse_and_run()
    out, err = capsys.readouterr()  # Grab stdout, stderr (and clear capture buffers)
    out = out.replace('\r\n', '\n')
    assert 'Bruteforce index : 0' in out
    assert expected_data in out
    assert err == ''


def test_cli_help(capsys):
    """Test showing that without arguments, protodeep shows the help"""
    sys.argv = ['test_deep']
    with pytest.raises(SystemExit) as excinfo:
        parse_and_run()
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 0

    out, err = capsys.readouterr()
    assert 'Usage: test_deep' in out
    assert err == ''


@pytest.mark.parametrize('testfile', ['bad_utf8_string', 'golden_message_proto3'])
def test_google_testdata(capsys, testfile):
    """Run ProtoDeep's cli against google testdata

    Args:
        capsys (pytest.capture.CaptureFixture): Fixture that enables sys.stdout and sys.stderr capturing
        testfile (str): The name of the test file (without extension)
    """
    datadir = Path(__file__).parent / 'data'
    # Read in expected ProtoDeep output
    with open(datadir / (testfile + '.txt'), 'rb') as expected_file:
        expected_data = expected_file.read().decode('utf-8')
    expected_data = expected_data.replace('\r\n', '\n')

    # Test the binary, base64 and hex-encoded versions of the file
    _run_and_check(capsys, expected_data, [f'{datadir / testfile}'])
    _run_and_check(capsys, expected_data, ['--base64', f'{datadir / testfile}.b64'])
    _run_and_check(capsys, expected_data, ['--hex', f'{datadir / testfile}.hex'])
