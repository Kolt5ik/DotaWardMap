# Демонстрация DotaWardMap

[← Главная](../README.md) · [Использование](usage.md) · [English](#english)

## Попробовать без установки

Скачай [interactive-demo.html](interactive-demo.html) и открой двойным кликом в браузере. На GitHub HTML отображается как исходный файл: используй Download raw file. Эта демонстрация полностью автономна: карта, Plotly и учебные данные включены в файл.

Можно переключать точки и тепловой слой, выбирать Observer/Sentry, показывать маркеры поверх плотности, приближать карту и скачать CSV. Кнопка «Показать сценарий» по очереди демонстрирует режимы. Это презентационная оболочка с той же отрисовкой карты, а не скриншот всего приложения.

**Все числа в интерактивном демо — учебные.** Оно не загружает Steam-профили, не запрашивает OpenDota и не показывает реальные матчи. Статические скриншоты в README сняты автором в настоящем приложении.

## Настоящий интерфейс на учебных данных

Для демонстрации именно Streamlit-интерфейса установи зависимости по [инструкции](installation.md), затем выполни в корне проекта:

```powershell
.\.venv\Scripts\python.exe -m streamlit run demo_app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

На Linux/macOS:

```bash
.venv/bin/python -m streamlit run demo_app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

Этот отдельный вход запускает **существующий app.py** с фиксированными данными из `docs/demo-data.json`. Загрузка начинается сразу. Запросы API подменяются только внутри демо; исходный `app.py` и обычный EXE не изменены.

Счётчики учебного набора: **68 Observer, 53 Sentry, всего 121 установка**. Разные числовые ID и лимиты оставляют тот же набор: это демонстрация интерфейса, а не подбор матчей. Custom Steam URL в этом режиме не разрешается через сеть. «Обновить историю» не запускает настоящее обновление. Выход — Ctrl+C в терминале.

## Сценарий для знакомства или записи ролика

| Шаг | Действие | Что показать |
| --- | --- | --- |
| 1 | Открыть демо | Профиль, показатели, карту и предупреждение о данных |
| 2 | Скрыть Sentry в режиме точек | Observer и счётчик постановок при наведении |
| 3 | Вернуть Sentry | Разницу кругов и квадратов |
| 4 | Включить «Тепловой слой» | Плавные пятна и прозрачные области |
| 5 | Переключить Observer → Sentry | Раздельную плотность типов |
| 6 | Включить «Показать точки поверх» | Точные позиции обоих типов поверх слоя |
| 7 | Выделить участок, двойным кликом сбросить | Управление масштабом без колеса |
| 8 | Скачать CSV | Столбцы type, x, y, count и агрегирование |
| 9 | Отключить тепловой слой | Возврат к маркерам и их настройкам |

В подписи ролика явно укажи, используется ли учебный набор или реальные данные OpenDota. Не обещай полное покрытие матчей. При демонстрации EXE покажи кнопку завершения; в исходниках сервер останавливается через Ctrl+C.

## English

Download [interactive-demo.html](interactive-demo.html) and open it locally. On GitHub, use **Download raw file**. It includes the map, Plotly and sample data, so it needs no server or network. Explore points, separate Observer/Sentry density, overlays, zoom and CSV. **Show tour** cycles through the display modes.

For the real Streamlit interface, install the dependencies and run `python -m streamlit run demo_app.py` through your virtual environment. This entry point renders the existing app with deterministic fixtures: 68 Observer and 53 Sentry placements. All profile IDs and match limits use the same sample data; refresh is simulated. No live OpenDota or Steam requests are made. Stop with Ctrl+C.

The cover is a schematic placement graphic, not a gameplay map. README screenshots show the actual v9.0.4 interface. Keep these distinctions visible when sharing the demo.
