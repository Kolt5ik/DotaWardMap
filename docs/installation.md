# Установка и сборка

[← Главная](../README.md) · [Использование](usage.md) · [Решение проблем](troubleshooting.md)

## Выбор способа

| Способ | Что нужно | Для кого |
| --- | --- | --- |
| Windows EXE | Windows, браузер, интернет для статистики | Быстро запустить готовое приложение |
| Исходники | Python 3.12, браузер, интернет для установки зависимостей и данных | Windows, Linux/macOS, разработка |
| Сборка EXE | Windows, Python 3.12, зависимости и PyInstaller | Создать свой Windows-файл |

Python 3.12 используется в GitHub Actions. Отдельной проверки всех версий Python и всех ОС сейчас нет.

## Windows EXE

Скачай **DotaWardMap.exe** из **Assets** [последнего релиза](https://github.com/Kolt5ik/DotaWardMap/releases/latest). Отдельная установка Python не требуется.

Запусти файл и дождись открытия браузера. Если вкладка не открылась, перейди на [http://127.0.0.1:8501](http://127.0.0.1:8501). При первом старте распаковка компонентов может занять некоторое время.

Для выхода используй **«Завершить приложение»**. Перед запуском новой версии заверши старую.

## Получение исходников

Можно скачать **Code → Download ZIP** и распаковать архив. Альтернатива, если Git установлен:

```powershell
git clone https://github.com/Kolt5ik/DotaWardMap.git
cd DotaWardMap
```

Все следующие команды выполняются в папке, где лежат `app.py` и `requirements.txt`. При скачивании ZIP это обычно вложенная папка `DotaWardMap-main`.

## Windows / PowerShell

Установи [Python 3.12](https://www.python.org/downloads/windows/) и включи **Add python.exe to PATH**. Открой новое окно PowerShell и проверь:

```powershell
python --version
```

В папке проекта выполни:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

Активация окружения и изменение ExecutionPolicy не нужны.

Для повторного запуска достаточно последней команды. Также можно открыть `run_windows.bat`: он использует готовое окружение, но не устанавливает зависимости.

## Linux / macOS

Установи Python 3.12. В Ubuntu/Debian для создания окружения может понадобиться системный пакет `python3-venv`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

Оставь терминал открытым. **Ctrl+C** завершает сервер.

## Тёмная тема

В корне проекта есть пример `.streamlit_config_example.toml`. Чтобы применить его, скопируй в `.streamlit/config.toml`.

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force .streamlit
Copy-Item .streamlit_config_example.toml .streamlit/config.toml
```

**Linux / macOS:**

```bash
mkdir -p .streamlit
cp .streamlit_config_example.toml .streamlit/config.toml
```

## Локальная сборка Windows EXE

На Windows запусти `build_exe.bat`. Он создаёт окружение при необходимости, устанавливает зависимости и PyInstaller, затем собирает приложение.

Ручной эквивалент после установки зависимостей:

```powershell
.\.venv\Scripts\python.exe -m pip install "pyinstaller>=6.10,<7"
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean dota_ward_map.spec
```

Результат: **`dist/DotaWardMap.exe`**. Сборка включает приложение, зависимости и локальную карту. Проверь запуск, загрузку профиля и завершение сервера.

## GitHub Actions: тестовая сборка

1. Запушь изменения в отдельную ветку.
2. Открой **Actions → Build Windows EXE → Run workflow**.
3. Выбери свою ветку и запусти сборку.
4. После успеха открой запуск **по его названию**.
5. Внизу, в **Artifacts**, скачай **DotaWardMap-Windows**.
6. Распакуй ZIP и запусти EXE.

Ручная сборка даёт artifact; новый релиз от неё не появляется. Скачивание artifacts может требовать входа в GitHub.

## Публикация релиза

Только после проверки и слияния pull request обнови локальную `main`:

```powershell
git switch main
git pull --ff-only origin main
```

Выбери **новый, ещё не существующий тег**. Например, если последняя версия v9.0.4 и готовится следующий patch-релиз:

```powershell
git tag v9.0.5
git push origin v9.0.5
```

Workflow реагирует на теги `v*`, собирает EXE и публикует его в Releases. Дождись успешной сборки. Для изменения только документации новый EXE-релиз обычно не нужен.
