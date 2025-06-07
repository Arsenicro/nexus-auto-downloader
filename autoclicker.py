import threading
import time

import keyboard
import pyautogui
import pygetwindow as gw


class WindowNotFoundException(Exception):
    pass


class ButtonNotFoundException(Exception):
    pass


class WindowNotActiveException(Exception):
    pass


def get_window_by_partial_title(title: str):
    """
    Returns the first window containing the partial title (case-insensitive).
    Raises WindowNotFoundException if no matching window is found.
    """
    title = title.lower()
    for win in gw.getAllWindows():
        if title in win.title.lower():
            return win
    raise WindowNotFoundException(f"No window with partial title '{title}' found.")


def activate_window_by_partial_title(partial_title: str):
    """
    Restores and activates the first window containing the partial_title (case-insensitive).
    Raises WindowNotFoundException if no matching window is found.
    """
    win = get_window_by_partial_title(partial_title)

    win.restore()
    win.activate()
    center_x = win.left + win.width // 2
    center_y = win.top + win.height // 2

    pyautogui.moveTo(center_x, center_y)

    return True


def find_on_screen(image_path: str, confidence=0.999, timeout=1):
    """
    Waits up to timeout seconds for the image to appear on screen.
    Returns (x, y) center coordinates if found.
    Raises ButtonNotFoundException if not found within timeout.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            print(f"Found button at: {location} in {time.time() - start:.2f} seconds")
            return location
        except pyautogui.ImageNotFoundException:
            time.sleep(0.3)
    raise ButtonNotFoundException(
        f"Button image '{image_path}' not found after {timeout} seconds."
    )


def click_button_on_screen(image_path: str, confidence=0.999, timeout=1):
    """
    Finds the button on screen and clicks it.
    Raises ButtonNotFoundException if not found within timeout.
    """
    location = find_on_screen(image_path, confidence, timeout)
    pyautogui.click(location)
    return True


def click_button_with_fallback(
    button_image: str,
    scroll_amount: int = 300,
    button_confidence: float = 0.99,
    timeout: int = 1,
):
    try:
        click_button_on_screen(
            button_image, confidence=button_confidence, timeout=timeout
        )
    except ButtonNotFoundException:
        print(f"Initial click of '{button_image}' failed. Trying fallback...")

        pyautogui.scroll(-scroll_amount)

        click_button_on_screen(
            button_image, confidence=button_confidence, timeout=timeout
        )


stop_event = threading.Event()


def run_process_loop(partial_browser_title, retry_limit=3):
    retry_number = 0
    try:
        while not stop_event.is_set():
            try:
                activate_window_by_partial_title("Nexus Mods App")
                click_button_with_fallback(
                    button_image="nexus_app_download.png",
                    scroll_amount=900,
                )
                time.sleep(1)
                browser = get_window_by_partial_title(partial_browser_title)
                active = gw.getActiveWindow()
                if active is not None and active.title != browser.title:
                    raise WindowNotActiveException(
                        f"Active window '{active.title}' is not the expected browser '{browser.title}'."
                    )
                click_button_on_screen(
                    "nexus_page_download.png", confidence=0.8, timeout=10
                )
                pyautogui.hotkey("ctrl", "w")
                retry_number = 0
                time.sleep(1)
            except (
                ButtonNotFoundException,
                WindowNotFoundException,
                WindowNotActiveException,
            ) as e:
                print(f"Error during process loop: {e}")
                retry_number += 1
                if retry_number >= retry_limit:
                    print("Max retries reached, stopping process.")
                    raise e
                print(f"Retrying... ({retry_number}/{retry_limit})")
                time.sleep(1)
    except (
        ButtonNotFoundException,
        WindowNotFoundException,
        WindowNotActiveException,
    ) as e:
        print(f"Process stopped due to error: {e}")


def on_stop_hotkey():
    print("Stop hotkey pressed, stopping process...")
    stop_event.set()


# Register hotkey Ctrl+Shift+S to stop the loop
keyboard.add_hotkey("ctrl+shift+s", on_stop_hotkey)

worker_thread = threading.Thread(target=run_process_loop, args=["Mozilla Firefox"])
worker_thread.start()

print("Running... Press Ctrl+Shift+S to stop.")

worker_thread.join()
print("Process stopped cleanly.")
