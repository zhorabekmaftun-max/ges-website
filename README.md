# GES Website

Статический сайт образовательного центра **GES — Global Education Sayram**.

Сайт состоит из одной страницы (`index.html`) и изображений (`images/`).
Для отдачи используется лёгкий сервер на Python без сторонних зависимостей.

## Требования

- Python 3.7+
- Сторонних библиотек не нужно — только стандартная библиотека.

## Быстрый запуск (локально)

```bash
python3 server.py
```

Сайт будет доступен на http://localhost:8000

## Параметры запуска

```bash
python3 server.py --host 0.0.0.0 --port 8000   # явно адрес и порт
python3 server.py --port 80                     # на 80 порту (нужны права root)
python3 server.py --dir /path/to/site           # другой каталог сайта
```

Те же значения можно задать через переменные окружения `HOST`, `PORT`, `GES_DIR`:

```bash
PORT=8080 python3 server.py
```

## Запуск на сервере (systemd)

1. Скопируйте файлы сайта в `/var/www/ges-website`:

   ```bash
   sudo mkdir -p /var/www/ges-website
   sudo cp -r index.html images server.py /var/www/ges-website/
   sudo chown -R www-data:www-data /var/www/ges-website
   ```

2. Установите unit-файл и запустите сервис:

   ```bash
   sudo cp ges-website.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now ges-website
   ```

3. Проверьте статус и логи:

   ```bash
   sudo systemctl status ges-website
   sudo journalctl -u ges-website -f
   ```

> При необходимости отредактируйте `WorkingDirectory`, `ExecStart`, `User`
> и порт в `ges-website.service` под свой сервер.

## Reverse proxy (рекомендуется для production)

Сервер слушает HTTP. Для HTTPS и домена поставьте перед ним nginx:

```nginx
server {
    listen 80;
    server_name ges.example.kz;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Затем выпустите бесплатный TLS-сертификат через `certbot --nginx`.
