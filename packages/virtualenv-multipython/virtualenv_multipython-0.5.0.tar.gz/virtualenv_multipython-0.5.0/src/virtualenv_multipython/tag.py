import re
from subprocess import check_output
import sys


RX = (
    re.compile(r'^(?P<impl>py)(?P<maj>[23])(?P<min>[0-9][0-9]?)$'),
    re.compile(r'^(?P<impl>py)(?P<maj>3)(?P<min>[1-9][0-9])(?P<suffix>t)$'),
)


def match_tag(tag):  # type: (str) -> bool
    return any(rx.match(tag) for rx in RX)


def get_tag_path(tag):  # type: (str) -> str | None
    # ruff: noqa: S603,S607
    out = check_output(['py', 'bin', '--path', tag])
    enc = sys.getfilesystemencoding()
    path = (out.decode() if enc is None else out.decode(enc)).strip()
    return path or None
