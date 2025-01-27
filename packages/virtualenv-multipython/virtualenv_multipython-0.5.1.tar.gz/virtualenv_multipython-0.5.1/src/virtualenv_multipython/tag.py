import re
from subprocess import check_output
import sys

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # ruff: noqa: F401 = Optional is actually used for typing below
    from typing import Optional


RX = (
    re.compile(r'^(?P<impl>py)(?P<maj>[23])(?P<min>[0-9][0-9]?)$'),
    re.compile(r'^(?P<impl>py)(?P<maj>3)(?P<min>[1-9][0-9])(?P<suffix>t)$'),
)


def match_tag(tag):  # type: (str) -> bool
    return any(rx.match(tag) for rx in RX)


def get_tag_expected_command(tag):  # type: (str) -> Optional[str]
    for rx in RX:
        match = rx.match(tag)
        if match:
            impl = {'py': 'python'}[match.group('impl')]
            ver = '{}.{}'.format(match.group('maj'), match.group('min'))
            suffix = match.groupdict().get('suffix', '')
            return '{impl}{ver}{suffix}'.format(impl=impl, ver=ver, suffix=suffix)
    return None


def get_tag_path(tag):  # type: (str) -> Optional[str]
    # ruff: noqa: S603,S607
    out = check_output(['py', 'bin', '--path', tag])
    enc = sys.getfilesystemencoding()
    path = (out.decode() if enc is None else out.decode(enc)).strip()
    return path or None
