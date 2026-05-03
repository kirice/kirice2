# Инструкция по сборке Fitness RPG Desktop Application

## ✅ Что уже сделано

Frontend (React + TypeScript) собран успешно:
- `dist/index.html` - главный HTML файл
- `dist/assets/` - CSS и JS бандлы

## 📋 Требования для полной сборки

### 1. Установка Rust

**Windows:**
1. Скачайте rustup-init.exe с https://rustup.rs/
2. Запустите установщик
3. Выберите "Proceed with installation"
4. После установки перезапустите терминал

**macOS:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**Linux:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 2. Проверка установки

```bash
rustc --version
cargo --version
```

Должно показать версии примерно:
```
rustc 1.75.0 (...)
cargo 1.75.0 (...)
```

### 3. Дополнительные зависимости

**Windows:**
- Установите Visual Studio Build Tools 2022
- Включите компонент "Desktop development with C++"
- Ссылка: https://visualstudio.microsoft.com/downloads/

**macOS:**
```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install build-essential libwebkit2gtk-4.1-dev libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

## 🚀 Сборка приложения

### Шаг 1: Установка Node.js зависимостей

```bash
cd fitness-rpg-app
npm install
```

### Шаг 2: Сборка frontend (уже выполнено)

```bash
npm run build
```

### Шаг 3: Сборка Tauri приложения

```bash
npm run tauri build
```

Этот команда:
1. Скомпилирует Rust код
2. Свяжет его с frontend
3. Создаст установочный файл

### Где искать результат

После успешной сборки:

**Windows:**
```
src-tauri/target/release/fitness-rpg-app.exe
src-tauri/target/release/bundle/msi/Fitness RPG_1.0.0_x64.msi
src-tauri/target/release/bundle/nsis/Fitness.RPG.Setup.1.0.0.exe
```

**macOS:**
```
src-tauri/target/release/bundle/macos/Fitness RPG.app
src-tauri/target/release/bundle/dmg/Fitness RPG_1.0.0_x64.dmg
```

**Linux:**
```
src-tauri/target/release/bundle/deb/fitness-rpg-app_1.0.0_amd64.deb
src-tauri/target/release/bundle/appimage/fitness-rpg-app_1.0.0_amd64.AppImage
```

## 🔧 Запуск в режиме разработки

Для тестирования без сборки .exe:

```bash
npm run tauri dev
```

Приложение откроется в отдельном нативном окне (не в браузере!).

## ⚠️ Возможные ошибки и решения

### Ошибка: "Could not find the Rust compiler"

**Решение:** Установите Rust через rustup (см. выше)

### Ошибка: "WebView2 not found" (Windows)

**Решение:** 
```powershell
winget install Microsoft.WebView2
```
Или скачайте с: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### Ошибка: "No package found in source directory"

**Решение:** Убедитесь, что `dist/` папка существует и содержит файлы:
```bash
npm run build
```

### Ошибка компиляции Rust

**Решение:** Проверьте, что все зависимости установлены:
```bash
# Windows: Visual Studio Build Tools с C++
# macOS: Xcode Command Line Tools
# Linux: libwebkit2gtk-4.1-dev и другие (см. выше)
```

### Долгая первая компиляция

Это нормально! Первая сборка Rust может занять 5-10 минут.
Последующие сборки будут быстрее благодаря кэшированию.

## 📦 Распространение приложения

### Для Windows (.exe)

1. Найдите `Fitness.RPG.Setup.1.0.0.exe` в `src-tauri/target/release/bundle/nsis/`
2. Это самодостаточный установщик
3. Пользователю НЕ нужен Rust или Node.js для запуска

### Для macOS (.app или .dmg)

1. Скопируйте `.app` файл или распространяйте через `.dmg`
2. Может потребоваться подпись кода для Gatekeeper

### Для Linux

1. Используйте `.deb` для Debian/Ubuntu
2. Или `.AppImage` для универсальной совместимости

## 🎮 Первый запуск приложения

1. Запустите `.exe` файл
2. Приложение создаст `fitness_rpg.db` в той же папке
3. Инициализируются 10 зон тела
4. Загрузится база из 48 упражнений

## 📝 Тестирование функционала

1. **Запись тренировки:**
   - Выберите упражнение (например, "Squats")
   - Укажите подходы (3) и повторения (10)
   - Нажмите "ЗАПИСАТЬ"
   - Проверьте обновление XP в зонах Legs, Core, Back

2. **Просмотр прогресса:**
   - Кликните на зону тела на силуэте
   - Появится детальная информация
   - Двойные линии соединят зону с панелью

3. **Тест декремента:**
   - Нажмите "Применить декремент (тест)"
   - XP уменьшится согласно формуле потерь

## 🔐 Подпись кода (опционально)

Для профессионального распространения:

**Windows:**
- Купите сертификат подписи кода (EV Certificate)
- Подпишите .exe через signtool

**macOS:**
- Используйте Xcode для подписи
- Нотаризация через Apple Developer

## 💡 Советы по оптимизации размера

В `src-tauri/Cargo.toml` уже настроена оптимизация:

```toml
[profile.release]
panic = "abort"
codegen-units = 1
lto = true
opt-level = "s"
strip = true
```

Это уменьшает размер .exe с ~50MB до ~15MB.

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте версии: `node -v`, `npm -v`, `rustc --version`
2. Очистите кэш: `npm run tauri build -- --clean`
3. Посмотрите логи в консоли при запуске `npm run tauri dev`

---

**Готово!** Теперь у вас есть полностью автономное desktop-приложение для фитнес-трекинга с RPG-системой.
