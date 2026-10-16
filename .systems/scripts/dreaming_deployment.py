"""Render local systemd files for review. Never install, enable or start units."""
import argparse
import os
from pathlib import Path
from dreaming_universal_evidence import need

TEMPLATES = Path(__file__).resolve().parents[1]/'ai/templates/dreaming/universal/v2'


def render(system_home, config_path):
    values = {'@SYSTEM_HOME@': str(system_home), '@CONFIG_PATH@': str(config_path)}
    for value in values.values():
        need(Path(value).is_absolute() and all(c not in value for c in '\n\r\t%$"\'\\ ') and
             '..' not in Path(value).parts, 'unsupported-unit-path')
    result = {}
    for name in ('dreaming-universal.service', 'dreaming-universal.timer'):
        text = (TEMPLATES/name).read_text()
        for key, value in values.items(): text = text.replace(key, value)
        need('@SYSTEM_HOME@' not in text and '@CONFIG_PATH@' not in text, 'unrendered-unit')
        result[name] = text
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system-home', required=True); parser.add_argument('--config', required=True)
    parser.add_argument('--output-directory', required=True)
    args = parser.parse_args()
    directory = Path(args.output_directory)
    need(directory.is_absolute() and directory.is_dir() and not directory.is_symlink(), 'invalid-unit-output')
    for name, text in render(args.system_home, args.config).items():
        fd = os.open(directory/name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd,'w') as stream: stream.write(text)
    print('Rendered two review files; no systemd action performed.')


if __name__ == '__main__': main()
