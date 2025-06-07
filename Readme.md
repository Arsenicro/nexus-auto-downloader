# Nexus Mods Auto Clicker

A Python automation script to assist with downloading mods using the **Nexus Mods App** and a browser (e.g., Firefox).

The script:

- Focuses the Nexus Mods App window
- Scrolls and attempts to click the download button
- Waits for the browser window to become active (expects the app to switch automatically)
- Clicks the web download button
- Closes the tab
- Repeats until stopped or a retry limit is reached

> Stop anytime with `Ctrl+Shift+S`.

---

## ⚙️ Requirements

- Python 3.7+
- GUI environment (relies on screenshots and mouse automation)

---

## 🧪 Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Usage

1. Open the following applications:

   - The **Nexus Mods App**
   - A browser (such as **Mozilla Firefox**) that will be used to open and confirm the mod download

2. Ensure the following image files are present in the same directory as the script:

   - `nexus_app_download.png` — an exact screenshot of the download button in the Nexus Mods App
   - `nexus_page_download.png` — an exact screenshot of the download button on the Nexus Mods website

3. The script will perform the following steps in a loop:

   - Activates the Nexus Mods App window (matched by partial title)
   - Scrolls downward (default: 900px) to ensure the download button is visible
   - Attempts to locate and click the button image (`nexus_app_download.png`)
   - Waits for the browser to become active (note: the browser must activate itself — the script does **not** switch tabs or windows automatically)
   - Verifies that the browser window is currently focused
   - Clicks the download confirmation button on the web page (`nexus_page_download.png`)
   - Closes the browser tab with `Ctrl+W`
   - Repeats the process

4. If the script encounters errors (e.g., window not found, button image not located, or wrong window active), it retries the operation up to **3 times**. If the issue persists, the script stops and prints the reason.

5. Press `Ctrl+Shift+S` at any time to stop the loop cleanly.
