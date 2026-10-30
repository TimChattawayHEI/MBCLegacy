"""One Meshy picture (nano-banana-pro image-to-image, 16:9, 9 credits): python3 tools/v64/meshy_free.py <stage> <name> "<prompt>" <refs>

refs: comma separated; a bare word is a style picture in tools/v64/img/style (street, alley, under: Tim's Meshy London
scenes, the look every stage is painted in), anything else a path. Needs the Meshy CLI logged in (meshy auth login
--device). Saves <work>/<stage>/<name>_raw.png (1376x768) and a half size _view.png; MESHY_WORK picks <work>.
Copy a panel you keep into tools/v64/img/<stage>/<name>.webp and list it in stages.json."""
import json, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
stage, name, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
refs = [s if (s.endswith('.png') or os.path.exists(s)) else os.path.join(HERE, 'img', 'style', s + '.webp') for s in sys.argv[4].split(',')]
D = os.path.join(WORK, stage); os.makedirs(D, exist_ok=True)
env = dict(os.environ, NO_PROXY='localhost', no_proxy='localhost', npm_config_noproxy='localhost', NODE_USE_ENV_PROXY='1', NODE_NO_WARNINGS='1')
M = ['npm', 'exec', '--yes', '--package=meshy-cli@0.4.0', '--', 'meshy']
def find_id(o):
    if isinstance(o, dict):
        for k in ('task_id', 'id'):
            if isinstance(o.get(k), str): return o[k]
        for v in o.values():
            x = find_id(v)
            if x: return x
    if isinstance(o, list):
        for v in o:
            x = find_id(v)
            if x: return x
tid = os.environ.get('TID')
if not tid:
    r = subprocess.run(M + ['image-to-image', 'create', '--ai-model', os.environ.get('MODEL', 'nano-banana-pro'), '--prompt', prompt, '--reference-image-urls', ','.join(refs),
                            '--aspect-ratio', os.environ.get('ASPECT', '16:9'), '--async', '--output-schema', 'v1', '--format', 'json', '--no-update-check'], capture_output=True, text=True, env=env, cwd='/tmp')
    tid = find_id(json.loads(r.stdout).get('result')) if r.stdout.strip() else None
    if not tid: sys.exit('meshy create failed: ' + (r.stdout + r.stderr)[-800:])
print('task', tid, flush=True)
open(os.path.join(D, 'tasks.txt'), 'a').write(f'{name} {tid} {prompt[:120]}\n')
subprocess.run(M + ['image-to-image', 'wait', tid, '--output-schema', 'v1', '--format', 'json', '--no-update-check'], capture_output=True, text=True, env=env, cwd='/tmp')
od = os.path.join(D, 'dl_' + name); os.makedirs(od, exist_ok=True)
subprocess.run(M + ['download', '--resource', 'image-to-image', '--task-id', tid, '--kind', 'image', '--output-dir', od, '--overwrite', '--output-schema', 'v1', '--format', 'json', '--no-update-check'], capture_output=True, text=True, env=env, cwd='/tmp')
fs = sorted(f for f in os.listdir(od) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')))
im = Image.open(os.path.join(od, fs[0])).convert('RGB'); im.save(os.path.join(D, name + '_raw.png'))
im.resize((im.width // 2, im.height // 2)).save(os.path.join(D, name + '_view.png')); print('saved', name, im.size)
