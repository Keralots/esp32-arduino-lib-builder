# TouchDeck P4 libs

Arduino-ESP32 3.3.8 precompiled libs with the ESP32-P4 folders (`esp32p4`,
`esp32p4_es`) rebuilt with `CONFIG_LCD_DSI_ISR_CACHE_SAFE=y` (upstream #407),
so MIPI-DSI panels keep scanning during flash writes. Every other chip folder is
taken unchanged from the released `esp32-core-3.3.8-libs.tar.xz`.

The rebuild uses the same sources as the 3.3.8 release (`pins/versions-3.3.8.txt`):
ESP-IDF v5.5.4, arduino-esp32 c6428be92, TinyUSB eae25b531, and the component
versions from the released `dependencies.lock` files (`pins/`). The workflow
fails if a rebuilt lock differs from the released one.

Workflow: `.github/workflows/touchdeck-p4-libs.yml`, runs on pushes to
`touchdeck/**` branches. The combined archive is the `touchdeck-libs` artifact.
