import os
import sys
import time
import json
import hashlib

import jinja2
import requests
import watchdog.events
import watchdog.observers


CALCULATOR_JS_PHP_URL = "https://console.kamatera.com/info/calculator.js.php"


def generate_template(env, template_filename, target_filename=None, render_kwargs=None, generate_hash=False):
    if not target_filename:
        target_filename = template_filename
    if not render_kwargs:
        render_kwargs = {}
    content = env.get_template(template_filename).render(**render_kwargs)
    with open(f".data/pages/{target_filename}", "w") as f:
        f.write(content)
    if generate_hash:
        return hashlib.sha256(content.encode()).hexdigest()


def encode_js_template(s):
    assert '`' not in s
    return '`' + s + '`'


def get_server_config_templates():
    res = {}
    for config_name, config_extension in {
        'default': 'txt',
        'cloudcli': 'txt',
        'terraform': 'tf',
        'packer': 'pkr.hcl',
    }.items():
        with open(f'pages_src/templates/config_{config_name}.{config_extension}') as f:
            res[config_name] = encode_js_template(f.read())
    return res


def get_server_config_templates_k8s():
    res = {}
    for config_name, config_extension in {
        'default': 'yaml',
    }.items():
        with open(f'pages_src/templates/config_k8s_{config_name}.{config_extension}') as f:
            res[config_name] = encode_js_template(f.read())
    return res


def generate(calculator_js_php_hash, with_timestamp=False):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("pages_src", "templates"),
        autoescape=jinja2.select_autoescape()
    )
    common_render_kwargs = {
        'html_extra': f'<!-- {time.time()} -->' if with_timestamp else '',
    }
    generate_template(env, "index.html", render_kwargs={
        **common_render_kwargs
    })
    serverconfiggen_hash = generate_template(env, "serverconfiggen.js", render_kwargs={
        **common_render_kwargs,
        "config_templates_json": json.dumps(get_server_config_templates()),
        "config_templates_json_k8s": json.dumps(get_server_config_templates_k8s())
    }, generate_hash=True)
    generate_template(env, "serverconfiggen.html", "serverconfiggen.html", {
        **common_render_kwargs,
        "calculator_js_php_url": f"calculator.js.php?h={calculator_js_php_hash}",
        "serverconfiggen_hash": serverconfiggen_hash,
    })
    generate_template(env, "serverconfiggen.html", "serverconfiggen_test.html", {
        **common_render_kwargs,
        "calculator_js_php_url": CALCULATOR_JS_PHP_URL,
        "serverconfiggen_hash": serverconfiggen_hash,
    })
    generate_template(env, "serverconfiggen.html", "serverconfiggen_k8s.html", {
        **common_render_kwargs,
        "calculator_js_php_url": f"calculator.js.php?h={calculator_js_php_hash}",
        "serverconfiggen_hash": serverconfiggen_hash,
        "k8s": True,
    })
    print('OK')


class EventHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.modified_src_paths = set()


    def on_any_event(self, event):
        if not event.is_directory and not event.src_path.endswith('~'):
            if event.event_type != watchdog.events.EVENT_TYPE_CLOSED:
                self.modified_src_paths.add(event.src_path)


def download_calculator_js_php():
    res = requests.get(CALCULATOR_JS_PHP_URL)
    res.raise_for_status()
    with open(".data/pages/calculator.js.php", "wb") as f:
        f.write(res.content)
        print(f'downloaded {CALCULATOR_JS_PHP_URL} to .data/pages/calculator.js.php ({len(res.content)} bytes)')
    return hashlib.sha256(res.content).hexdigest()


def dev():
    calculator_js_php_hash = download_calculator_js_php()
    generate(calculator_js_php_hash)
    event_handler = EventHandler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path='pages_src', recursive=True)
    observer.start()
    print("Watching pages_src for changes...")
    try:
        while True:
            time.sleep(0.1)
            if len(event_handler.modified_src_paths) > 0:
                print(f'Regenerating, changes detected in {event_handler.modified_src_paths}')
                event_handler.modified_src_paths = set()
                generate(calculator_js_php_hash)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main(*args):
    os.makedirs(".data/pages", exist_ok=True)
    if '--dev' in args:
        dev()
    else:
        calculator_js_php_hash = download_calculator_js_php()
        generate(calculator_js_php_hash, with_timestamp='--with-timestamp' in args)


if __name__ == "__main__":
    main(*sys.argv[1:])
