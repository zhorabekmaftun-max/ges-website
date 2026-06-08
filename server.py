#!/usr/bin/env python3
"""
Простой production-ready сервер для статического сайта GES.

Запуск:
    python3 server.py                 # http://0.0.0.0:8000
    python3 server.py --port 80       # на 80 порту (нужны права root)
    python3 server.py --host 127.0.0.1 --port 8080

Параметры можно задать через переменные окружения:
    HOST, PORT      — адрес и порт
    GES_DIR         — каталог с сайтом (по умолчанию — папка со скриптом)

Зависимостей нет — используется только стандартная библиотека Python 3.7+.
"""

import argparse
import os
import signal
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# Каталог со скриптом — корень сайта по умолчанию
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class GESRequestHandler(SimpleHTTPRequestHandler):
    """Отдаёт статику с корректными MIME-типами, кешированием и SPA-fallback."""

    # Кеширование статики (картинки, шрифты) — на год; HTML — без кеша
    LONG_CACHE_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif",
                      ".webp", ".ico", ".woff", ".woff2", ".css", ".js")

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".js": "application/javascript",
        ".json": "application/json",
    }

    def end_headers(self):
        # Базовые заголовки безопасности
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")

        path = self.path.split("?", 1)[0].lower()
        if path.endswith(self.LONG_CACHE_EXT):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        elif path.endswith(".html") or path in ("/", ""):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        # Любой несуществующий путь отдаёт главную страницу (single-page сайт)
        if code == 404:
            self.path = "/index.html"
            try:
                f = self.send_head()
                if f:
                    try:
                        self.copyfile(f, self.wfile)
                    finally:
                        f.close()
                    return
            except Exception:
                pass
        super().send_error(code, message, explain)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def parse_args():
    parser = argparse.ArgumentParser(description="Статический сервер сайта GES")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"),
                        help="Адрес для прослушивания (по умолчанию 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)),
                        help="Порт (по умолчанию 8000)")
    parser.add_argument("--dir", default=os.environ.get("GES_DIR", BASE_DIR),
                        help="Каталог с сайтом")
    return parser.parse_args()


def main():
    args = parse_args()
    directory = os.path.abspath(args.dir)

    if not os.path.isfile(os.path.join(directory, "index.html")):
        sys.exit(f"Ошибка: index.html не найден в каталоге {directory}")

    handler = partial(GESRequestHandler, directory=directory)
    server = ThreadingHTTPServer((args.host, args.port), handler)

    def shutdown(signum, frame):
        print("\nОстановка сервера…")
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"GES сайт запущен: http://{args.host}:{args.port}")
    print(f"Каталог: {directory}")
    print("Нажмите Ctrl+C для остановки.")
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
