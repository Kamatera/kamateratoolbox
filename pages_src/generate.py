import os
import sys
import time
import json

import jinja2
import requests
import watchdog.events
import watchdog.observers


CALCULATOR_JS_PHP_URL = "https://console.kamatera.com/info/calculator.js.php"


def generate_template(env, template_filename, target_filename=None, render_kwargs=None):
    if not target_filename:
        target_filename = template_filename
    if not render_kwargs:
        render_kwargs = {}
    with open(f".data/pages/{target_filename}", "w") as f:
        f.write(env.get_template(template_filename).render(**render_kwargs))


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


def generate():
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("pages_src", "templates"),
        autoescape=jinja2.select_autoescape()
    )
    generate_template(env, "index.html")
    generate_template(env, "serverconfiggen.js", render_kwargs={
        "config_templates_json": json.dumps(get_server_config_templates())
    })
    generate_template(env, "serverconfiggen.html", "serverconfiggen.html", {
        "calculator_js_php_url": "calculator.js.php"
    })
    generate_template(env, "serverconfiggen.html", "serverconfiggen_test.html", {
        "calculator_js_php_url": CALCULATOR_JS_PHP_URL
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


def dev():
    download_calculator_js_php()
    generate()
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
                generate()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main(*args):
    os.makedirs(".data/pages", exist_ok=True)
    if '--dev' in args:
        dev()
    else:
        download_calculator_js_php()
        generate()


if __name__ == "__main__":
    main(*sys.argv[1:])
