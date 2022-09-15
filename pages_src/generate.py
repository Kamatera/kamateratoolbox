import os
import sys
import time

import jinja2
import requests
import watchdog.events
import watchdog.observers


CALCULATOR_JS_PHP_URL = "https://console.kamatera.com/info/calculator.js.php"


def generate(calculator_js_php_url=CALCULATOR_JS_PHP_URL):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("pages_src", "templates"),
        autoescape=jinja2.select_autoescape()
    )
    with open(".data/pages/index.html", "w") as f:
        f.write(env.get_template("index.html").render())
    with open(".data/pages/serverconfiggen.html", "w") as f:
        f.write(env.get_template("serverconfiggen.html").render(
            calculator_js_php_url=calculator_js_php_url
        ))
    print('OK')


class EventHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.modified_src_paths = set()


    def on_any_event(self, event):
        if not event.is_directory and not event.src_path.endswith('~'):
            if event.event_type != watchdog.events.EVENT_TYPE_CLOSED:
                self.modified_src_paths.add(event.src_path)


def dev():
    if not os.path.exists(".data/pages/calculator.js.php"):
        res = requests.get(CALCULATOR_JS_PHP_URL)
        res.raise_for_status()
        with open(".data/pages/calculator.js.php", "wb") as f:
            f.write(res.content)
    generate("calculator.js.php")
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
                generate("calculator.js.php")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main(*args):
    os.makedirs(".data/pages", exist_ok=True)
    if '--dev' in args:
        dev()
    else:
        generate()


if __name__ == "__main__":
    main(*sys.argv[1:])
