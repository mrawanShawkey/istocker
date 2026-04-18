import os
import subprocess
import sys

commands = [
    ['flask', 'db', 'migrate', '--directory', 'api/migrations', '-m', 'initial'],
    ['flask', 'db', 'upgrade', '--directory', 'api/migrations'],
    ['flask', 'seed'],
]

if not os.path.exists('api/migrations'):
    subprocess.run(['flask', 'db', 'init', '--directory', 'api/migrations'])
for cmd in commands:
    print(f'Running: {" ".join(cmd)}')
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f'Failed at: {" ".join(cmd)}')
        sys.exit(1)