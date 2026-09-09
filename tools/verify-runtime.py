#!/usr/bin/env python3
"""Read-only check for custom module loss after moving or recreating the stack."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default='ac-worldserver')
    parser.add_argument('--image', help='Check an image before deploying it, without starting worldserver')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    expected = {p.name for p in (root / 'modules').glob('mod-*/conf/*.conf.dist')}
    expected.update({'playerbots.conf.dist', 'mod_llm_chatter.conf.dist'})
    if args.image:
        configured_image = args.image
        installed = run('docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'ls',
                        args.image, '-1', '/azerothcore/env/ref/etc/modules')
    else:
        info = json.loads(run('docker', 'inspect', args.container))[0]
        configured_image = info['Config']['Image']
        if not info['State']['Running']:
            print('FAIL: worldserver container is not running.')
            return 1
        installed = run('docker', 'exec', args.container, 'ls', '-1', '/azerothcore/env/ref/etc/modules')
    failures = []
    if not configured_image.startswith('namek/worldserver:'):
        failures.append('Unexpected image: ' + configured_image)
    missing = expected - set(installed.splitlines())
    if missing:
        failures.append('Module configs absent from image: ' + ', '.join(sorted(missing)))
    sql_path = '/azerothcore/modules/mod-playerbots/data/sql/playerbots'
    command = (['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'test', args.image]
               if args.image else ['docker', 'exec', args.container, 'test'])
    if subprocess.run(command + ['-d', sql_path], capture_output=True).returncode:
        failures.append('Playerbots database-update files are absent from the image.')
    if not args.image:
        port_check = subprocess.run(['docker', 'exec', args.container, 'bash', '-c',
                                     'exec 3<>/dev/tcp/127.0.0.1/8085'], capture_output=True)
        if port_check.returncode:
            failures.append('Worldserver is not accepting connections on port 8085 yet.')
        log = run('docker', 'exec', args.container, 'cat', '/azerothcore/env/dist/logs/Server.log')
        block = log.rsplit('Using modules configuration:', 1)[-1].split('Initializing Scripts', 1)[0]
        not_loaded = {name.removesuffix('.dist') for name in expected
                      if '> ' + name.removesuffix('.dist') not in block}
        if not_loaded:
            failures.append('Module configs absent from startup log: ' + ', '.join(sorted(not_loaded)))
        errors = run('docker', 'exec', args.container, 'cat', '/azerothcore/env/dist/logs/Errors.log')
        mismatches = [line for line in errors.splitlines()
                      if 'assigned in the database, but has no code' in line]
        if mismatches:
            failures.append('Database references scripts missing from this executable:\n' + '\n'.join(mismatches))
    for failure in failures:
        print('FAIL: ' + failure)
    if failures:
        return 1
    print(f'PASS: {configured_image}; all {len(expected)} expected module configs present'
          + ('.' if args.image else ' and loaded.'))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (subprocess.CalledProcessError, OSError) as exc:
        print('FAIL: could not inspect Docker runtime:', exc, file=sys.stderr)
        sys.exit(1)
