"""Writes ota.txt, the list the app uses to update itself without a new APK (Version 66, in-app updates).

python3 tools/ota/manifest.py <out file> <build number> <commit>     (run from the repo root, as the APK build does)

One line per game file under web/, with its SHA-256 and size. The app compares this with the copy bundled inside its
APK, downloads only the files that differ (from raw.githubusercontent.com at that exact commit), checks every hash and
swaps them in on a restart. `native` fingerprints the Android side (android/): if it differs from the installed app's,
the update needs a real APK and the app shows the old download card instead.

Plain text on purpose, so the Java side needs no JSON library:
    ota 1
    build 123
    commit 0123abcd...
    native 89abcdef0123
    f <sha256> <bytes> <path relative to web/>
"""
import hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB = os.path.join(ROOT, 'web')


def native_fingerprint():
    # blob hashes of everything tracked under android/: changes only when the Android code or settings change
    out = subprocess.run(['git', 'ls-files', '-s', 'android'], cwd=ROOT, check=True, capture_output=True).stdout
    return hashlib.sha256(out).hexdigest()[:16]


def main():
    out, build, commit = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    lines = ['ota 1', f'build {build}', f'commit {commit}', f'native {native_fingerprint()}']
    for d, _, names in os.walk(WEB):
        for n in names:
            p = os.path.join(d, n)
            rel = os.path.relpath(p, WEB).replace(os.sep, '/')
            if any(c in rel for c in '\r\n') or rel.startswith('.') or '/.' in rel:
                continue
            data = open(p, 'rb').read()
            lines.append(f'f {hashlib.sha256(data).hexdigest()} {len(data)} {rel}')
    lines[4:] = sorted(lines[4:], key=lambda l: l.split(' ', 3)[3])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print(f'ota.txt: build {build}, {len(lines) - 4} files')


if __name__ == '__main__':
    main()
