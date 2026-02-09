import threading
import time
import keyboard
import pyautogui
import pygetwindow as gw


# --- Exceptions -------------------------------------------------------------

class WindowNotFoundException(Exception): pass
class WindowNotActiveException(Exception): pass
class ButtonNotFoundException(Exception): pass


# --- Window helpers ---------------------------------------------------------

def get_window_by_partial_title(title: str):
    title = title.lower()
    for w in gw.getAllWindows():
        if title in w.title.lower():
            return w
    raise WindowNotFoundException(f"No window with partial title '{title}' found.")


def activate_window_by_partial_title(partial_title: str, retries=5, delay=0.25):
    partial_title = partial_title.lower()

    for _ in range(retries):
        try:
            win = get_window_by_partial_title(partial_title)
        except WindowNotFoundException:
            time.sleep(delay)
            continue

        # ensure restored
        try:
            if win.isMinimized:
                win.restore()
                time.sleep(delay)
        except Exception:
            pass

        # first normal activation attempt
        try:
            win.activate()
        except Exception as e:
            if "Error code from Windows: 0" not in str(e):
                raise

        time.sleep(delay)

        active = gw.getActiveWindow()
        if active and active.title == win.title:
            return True

        # fallback: minimize + restore to break Windows focus lock
        try:
            win.minimize()
            time.sleep(0.15)
            win.restore()
            time.sleep(0.25)
        except Exception:
            pass

        active = gw.getActiveWindow()
        if active and active.title == win.title:
            return True

        time.sleep(delay)

    raise WindowNotActiveException(
        f"Could not activate window with partial title '{partial_title}'."
    )


# --- Image helpers ----------------------------------------------------------

def find_on_screen(image_path: str, confidence=0.999, timeout=1):
    """
    Wait up to `timeout` seconds for image to appear on screen.
    Returns (x, y) center coordinates if found, otherwise False.
    Handles cases where pyautogui.locateCenterOnScreen returns None
    and catches transient GUI/display exceptions.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if loc:  # locateCenterOnScreen returns None when not found
                print(f"Found button at: {loc} in {time.time() - start:.2f} seconds")
                return (loc.x, loc.y) if hasattr(loc, "x") else loc  # pyautogui may return a Point-like object or tuple
        except OSError as e:
            # transient errors (display, PIL issues, etc). Log and retry.
            print(f"Transient error while searching for '{image_path}': {e}")
        except Exception as e:
            # unexpected errors: log and break/raise depending on severity
            print(f"Unexpected error while searching for '{image_path}': {e}")
            # if you prefer to fail fast, uncomment next line:
            # raise

        time.sleep(0.25)

    # not found within timeout
    print(f"Image '{image_path}' not found after {timeout:.2f}s")
    return False


def get_on_screen(image_path: str, confidence=0.999, timeout=1):
    """
    Calls find_on_screen and raises ButtonNotFoundException if not found.
    Returns (x, y) tuple when found.
    """
    coords = find_on_screen(image_path, confidence=confidence, timeout=timeout)
    if not coords:
        raise ButtonNotFoundException(f"Button image '{image_path}' not found after {timeout} seconds.")
    return coords


def click_button_on_screen(image_path: str, confidence=0.999, timeout=1):
    pos = get_on_screen(image_path, confidence, timeout)
    pyautogui.click(pos)
    pos2 = find_on_screen(image_path, confidence, timeout=0.3)
    if pos != pos2:
        pyautogui.click(pos2)

    return True


def click_button_with_fallback(
    button_image: str,
    scroll_amount: int = 300,
    button_confidence: float = 0.99,
    timeout: int = 1,
):
    try:
        click_button_on_screen(button_image, confidence=button_confidence, timeout=timeout)
    except ButtonNotFoundException:
        print(f"Initial click failed: {button_image}. Trying scroll fallback...")
        pyautogui.scroll(-scroll_amount)
        click_button_on_screen(button_image, confidence=button_confidence, timeout=timeout)


# --- Active window assertion ------------------------------------------------

def assert_active_window(expected_title: str, retries=5, delay=0.5):
    expected = get_window_by_partial_title(expected_title)

    for _ in range(retries):
        active = gw.getActiveWindow()
        if active and active.title == expected.title:
            return
        time.sleep(delay)

    active_title = active.title if active else "None"
    raise WindowNotActiveException(
        f"Active window '{active_title}' != expected '{expected.title}'"
    )


# --- Process loop -----------------------------------------------------------

stop_event = threading.Event()

def run_process_loop(partial_browser_title, retry_limit=3):
    retries = 0

    try:
        while not stop_event.is_set():
            try:
                activate_window_by_partial_title(partial_browser_title)

                if find_on_screen("started.png", confidence=0.8, timeout=0.3):
                    pyautogui.hotkey("ctrl", "w")

                if find_on_screen("nexus_page_download.png", confidence=0.8, timeout=0.3):
                    pyautogui.hotkey("ctrl", "w")

                activate_window_by_partial_title("Vortex", retries=3)

                click_button_on_screen("nexus_app_download.png", confidence=0.8, timeout=10)
                assert_active_window(partial_browser_title)

                time.sleep(0.5)

                click_button_on_screen("nexus_page_download.png", confidence=0.7, timeout=10)

                retries = 0
                assert_active_window("Vortex")

            except (ButtonNotFoundException, WindowNotFoundException, WindowNotActiveException) as e:
                print(f"Error in loop: {e}")
                retries += 1
                if retries >= retry_limit:
                    print("Max retries reached. Stopping.")
                    raise
                print(f"Retrying... ({retries}/{retry_limit})")
                time.sleep(1)

    except (ButtonNotFoundException, WindowNotFoundException, WindowNotActiveException) as e:
        print(f"Process stopped due to error: {e}")


# --- Hotkey handler ---------------------------------------------------------

def on_stop_hotkey():
    print("Stop hotkey pressed. Stopping...")
    stop_event.set()


keyboard.add_hotkey("ctrl+shift+s", on_stop_hotkey)

worker = threading.Thread(target=run_process_loop, args=["Firefox"])
worker.start()

print("Running... Press Ctrl+Shift+S to stop.")

worker.join()
print("Process stopped cleanly.")
