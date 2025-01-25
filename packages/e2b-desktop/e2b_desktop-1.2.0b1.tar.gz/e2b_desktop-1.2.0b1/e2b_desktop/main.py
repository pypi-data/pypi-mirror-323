import uuid
from typing import Literal, Iterator, overload

from typing import Callable, Optional
from e2b import Sandbox as SandboxBase
import requests


class Sandbox(SandboxBase):
    default_template = "desktop"
    stream_base_url = "https://e2b.dev"

    @staticmethod
    def start_video_stream(sandbox: "Sandbox", api_key: str, sandbox_id: str):

        # First we need to get the stream key
        response = requests.post(
            f"{Sandbox.stream_base_url}/api/stream/sandbox",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            json={"sandboxId": sandbox_id},
        )

        if not response.ok:
            raise Exception(
                f"Failed to start video stream {response.status_code}: {response.text}"
            )

        data = response.json()
        sandbox.video_stream_token = data["token"]
        command = (
            "ffmpeg -video_size 1024x768 -f x11grab -i :99 -c:v libx264 -c:a aac -g 50 "
            "-b:v 4000k -maxrate 4000k -bufsize 8000k -f flv rtmp://global-live.mux.com:5222/app/$STREAM_KEY"
        )
        sandbox.commands.run(
            command,
            background=True,
            envs={"STREAM_KEY": data["streamKey"]},
        )

    def __init__(self, *args, video_stream=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not self._connection_config.api_key:
            raise ValueError("API key is required")

        if video_stream:
            self.start_video_stream(
                self,
                self._connection_config.api_key,
                self.sandbox_id,
            )

    def get_video_stream_url(self):
        """
        Get the video stream URL.
        """
        # We already have the token
        if hasattr(self, "video_stream_token") and self.video_stream_token:
            return f"{self.stream_base_url}/stream/sandbox/{self.sandbox_id}?token={self.video_stream_token}"

        # In cases like when a user reconnects to the sandbox, we don't have the token yet and need to get it from the server
        response = requests.get(
            f"{self.stream_base_url}/api/stream/sandbox/{self.sandbox_id}",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self._connection_config.api_key,
            },
        )

        if not response.ok:
            raise Exception(
                f"Failed to get stream token: {response.status_code} {response.reason}"
            )

        data = response.json()
        self.video_stream_token = data["token"]

        return f"{self.stream_base_url}/stream/sandbox/{self.sandbox_id}?token={self.video_stream_token}"

    @overload
    def take_screenshot(self, format: Literal["stream"]) -> Iterator[bytes]:
        """
        Take a screenshot and return it as a stream of bytes.
        """
        ...

    @overload
    def take_screenshot(
        self,
        format: Literal["bytes"],
    ) -> bytearray:
        """
        Take a screenshot and return it as a bytearray.
        """
        ...

    def take_screenshot(
        self,
        format: Literal["bytes", "stream"] = "bytes",
    ):
        """
        Take a screenshot and return it in the specified format.
        :param format: The format of the screenshot. Can be 'bytes', 'blob', or 'stream'.
        :returns: The screenshot in the specified format.
        """
        screenshot_path = f"/tmp/screenshot-{uuid.uuid4()}.png"

        self.commands.run(
            f"scrot --pointer {screenshot_path}",
        )

        file = self.files.read(screenshot_path, format=format)
        self.files.remove(screenshot_path)
        return file

    def left_click(self):
        """
        Left click on the current mouse position.
        """
        return self.pyautogui("pyautogui.click()")

    def double_click(self):
        """
        Double left click on the current mouse position.
        """
        return self.pyautogui("pyautogui.doubleClick()")

    def right_click(self):
        """
        Right click on the current mouse position.
        """
        return self.pyautogui("pyautogui.rightClick()")

    def middle_click(self):
        """
        Middle click on the current mouse position.
        """
        return self.pyautogui("pyautogui.middleClick()")

    def scroll(self, amount: int):
        """
        Scroll the mouse wheel by the given amount.
        :param amount: The amount to scroll.
        """
        return self.pyautogui(f"pyautogui.scroll({amount})")

    def move_mouse(self, x: int, y: int):
        """
        Move the mouse to the given coordinates.
        :param x: The x coordinate.
        :param y: The y coordinate.
        """
        return self.pyautogui(f"pyautogui.moveTo({x}, {y})")

    def get_cursor_position(self):
        """
        Get the current cursor position.
        :return: A tuple with the x and y coordinates.
        """
        # We save the value to a file because stdout contains warnings about Xauthority.
        self.pyautogui(
            """
x, y = pyautogui.position()
with open("/tmp/cursor_position.txt", "w") as f:
    f.write(str(x) + " " + str(y))
"""
        )
        # pos is like this: 100 200
        pos = self.files.read("/tmp/cursor_position.txt")
        return tuple(map(int, pos.split(" ")))

    def get_screen_size(self):
        """
        Get the current screen size.
        :return: A tuple with the width and height.
        """
        # We save the value to a file because stdout contains warnings about Xauthority.
        self.pyautogui(
            """
width, height = pyautogui.size()
with open("/tmp/size.txt", "w") as f:
    f.write(str(width) + " " + str(height))
"""
        )
        # size is like this: 100 200
        size = self.files.read("/tmp/size.txt")
        return tuple(map(int, size.split(" ")))

    def write(self, text: str):
        """
        Write the given text at the current cursor position.
        :param text: The text to write.
        """
        return self.pyautogui(f"pyautogui.write({text!r})")

    def press(self, key: str):
        """
        Press a key.
        :param key: The key to press (e.g. "enter", "space", "backspace", etc.).
        """
        return self.pyautogui(f"pyautogui.press({key!r})")

    def hotkey(self, *keys):
        """
        Press a hotkey.
        :param keys: The keys to press (e.g. `hotkey("ctrl", "c")` will press Ctrl+C).
        """
        return self.pyautogui(f"pyautogui.hotkey({keys!r})")

    def open(self, file_or_url: str):
        """
        Open a file or a URL in the default application.
        :param file_or_url: The file or URL to open.
        """
        return self.commands.run(f"xdg-open {file_or_url}", background=True)

    @staticmethod
    def _wrap_pyautogui_code(code: str):
        return f"""
import pyautogui
import os
import Xlib.display

display = Xlib.display.Display(os.environ["DISPLAY"])
pyautogui._pyautogui_x11._display = display

{code}
exit(0)
"""

    def pyautogui(
        self,
        pyautogui_code: str,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
    ):
        code_path = f"/tmp/code-{uuid.uuid4()}.py"

        code = self._wrap_pyautogui_code(pyautogui_code)

        self.files.write(code_path, code)

        out = self.commands.run(
            f"python {code_path}",
            on_stdout=on_stdout,
            on_stderr=on_stderr,
        )
        self.files.remove(code_path)
        return out
