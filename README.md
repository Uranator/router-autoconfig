# router-autoconfig

Автономная подписка и образы прошивок для Tachyon/OpenWrt на **Cudy WR3000S v1** (MT7986, 256MB RAM, 128MB flash).

## 📦 Структура репозитория

```
router-autoconfig/
├── configs/                    # UCI конфиги для прошивки
│   ├── tachyon.config         # Tachyon маршрутизация (Direct_RU, Desync, VPN)
│   ├── network.config         # Сеть (LAN 192.168.2.1, WAN DHCP)
│   ├── firewall.config        # Фаервол + Tachyon include
│   └── dhcp.config            # DNSMasq (8.8.8.8, 1.1.1.1)
├── generated/                  # Сгенерированные подписки (авто-обновление)
│   ├── mix.txt                # Все конфиги (Base64)
│   ├── reality.txt            # Только Reality
│   ├── fast.txt               # Самые быстрые
│   └── clean.txt              # Проверенные
├── sub-builder/
│   └── config-sub-platform/   # Подмодуль: генератор подписок
├── releases/                   # Артефакты (в GitHub Releases)
├── scripts/                    # Вспомогательные скрипты
└── .github/workflows/
    ├── update-subscriptions.yml  # Каждый час: собирает подписки
    └── build-image.yml           # Ручной запуск: собирает .bin прошивку
```

## 🔗 Подписка для роутера (Tachyon)

После первого успешного запуска workflow `update-subscriptions`:

```
https://raw.githubusercontent.com/Uranator/router-autoconfig/main/generated/mix.txt
```

**В Tachyon (LuCI → Services → Tachyon → Подписка):**
- URL: `https://raw.githubusercontent.com/Uranator/router-autoconfig/main/generated/mix.txt`
- Автообновление: каждые 24 часа (или по расписанию)

## 🏗 Сборка прошивки

1. Зайдите в **Actions → Build OpenWrt Image**
2. Нажмите **Run workflow**
3. Укажите версию (например, `v1.0.0`)
4. Профиль: `cudy_wr3000s-v1` (по умолчанию)
5. Готовый `.bin` появится в **Releases** под тегом `firmware-v1.0.0`

**Установка на роутере:**
```
System → Backup/Flash Firmware → Flash new firmware image → выберите .bin
```

## ⚙️ Настроенные секреты (GitHub Settings → Secrets → Actions)

| Секрет | Описание |
|--------|----------|
| `TG_API_ID` | Telegram API ID (для сбора конфигов из каналов) |
| `TG_API_HASH` | Telegram API Hash |

> Получить: https://my.telegram.org/apps

## 🎯 Маршрутизация Tachyon (в прошивке)

| Приоритет | Секция | Тип | Для чего |
|-----------|--------|-----|----------|
| 1 | `Direct_RU` | bypass | RU-банки, Госуслуги, Яндекс, VK, Steam CDN — **напрямую** |
| 10 | `Desync_YouTube` | desync (youtube) | YouTube через DPI-обход |
| 11 | `Desync_Telegram` | desync (auto) | Telegram через DPI-обход |
| 20 | `VPN_Proxy` | connection (VLESS Reality) | Discord, Telegram (фоллбэк), AI, Geoblock — через VPN |

**VPN Outbound:** `vps_vless` → 138.124.112.202:443 (VLESS+Reality, flow=xtls-rprx-vision)

## 🔄 Автоматизация

| Workflow | Триггер | Что делает |
|----------|---------|------------|
| `update-subscriptions` | Каждый час (`0 * * * *`) + ручной | Собирает конфиги из источников, дедуплицирует, скорит, публикует в `generated/` |
| `build-image` | Только ручной | Собирает OpenWrt 24.10 с Tachyon, загружает в Releases |

## 📝 Добавление своих источников

Отредактируйте `sub-builder/config-sub-platform/config/subscription_sources.txt`:
```
https://your-trusted-source.com/subscription.txt
https://another-source.com/vless.txt
```

Или добавьте GitHub репозитории в `sub-builder/config-sub-platform/config/github_sources.json`:
```json
[
  {"repo": "username/repo", "paths": ["configs/"], "branch": "main"}
]
```

## 🛡 Безопасность

- Репозиторий **приватный**
- Все секреты только в **GitHub Secrets**
- Никаких токенов в коде
- Workflow идемпотентны (повторный запуск не ломает)

## 📄 Лицензия

MIT — используйте как шаблон для своих роутеров.
