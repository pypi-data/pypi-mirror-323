# E2B Desktop Sandbox (beta)

E2B Desktop Sandbox is an isolated cloud environment with a desktop-like interface powered by [E2B](https://e2b.dev).

Launching E2B Sandbox takes about 300-500ms. You can customize the desktop environment and preinstall any dependencies you want using our [custom sandbox templates](https://e2b.dev/docs/sandbox-template).

![Desktop Sandbox](screenshot.png)

**Work in progress**
This repository is a work in progress. We welcome feedback and contributions. Here's the list of features we're working on:
- [ ] JavaScript SDK
- [ ] Streaming live desktop
- [ ] Tests
- [ ] Docstrings

## Getting started
The E2B Desktop Sandbox is built on top of [E2B Sandbox](https://e2b.dev/docs).

### 1. Get E2B API key
Sign up at [E2B](https://e2b.dev) and get your API key.
Set environment variable `E2B_API_KEY` with your API key.

### 2. Install SDK
**Python**
```bash
pip install e2b-desktop
```

**JavaScript**
```bash
Coming soon
```

### 3. Create Desktop Sandbox
```python
from e2b_desktop import Sandbox

desktop = Sandbox()
```

## Features

### Mouse control
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

desktop.double_click()
desktop.left_click()
desktop.right_click()
desktop.middle_click()
desktop.scroll(10) # Scroll by the amount. Positive for up, negative for down.
desktop.mouse_move(100, 200) # Move to x, y coordinates
```

### Locate on screen
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

# Find "Home" text on the screen and return the coordinates
x, y = desktop.locate_on_screen("Home")
# Move the mouse to the coordinates
desktop.mouse_move(x, y)
```

### Keyboard control
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

desktop.write("Hello, world!") # Write text at the current cursor position
desktop.hotkey("ctrl", "c") # Press ctrl+c
```

### Screenshot
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

# Take a screenshot and save it as "screenshot.png" locally
desktop.screenshot("screenshot.png")
```

### Open file
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

# Open file with default application
desktop.files.write("/home/user/index.js", "console.log('hello')") # First create the file
desktop.open("/home/user/index.js") # Then open it
```

### Run any bash commands
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

# Run any bash command
desktop.commands.run("ls -la /home/user")
```

### Run PyAutoGUI commands
```python
from e2b_desktop import Sandbox
desktop = Sandbox()

# Run any PyAutoGUI command
desktop.pyautogui("pyautogui.click()")
```

<!-- ### Customization
```python
from e2b_desktop import Sandbox
desktop = Sandbox()
``` -->

## Under the hood
You can use [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/) to control the whole environment programmatically.

The desktop-like environment is based on Linux and [Xfce](https://www.xfce.org/) at the moment. We chose Xfce because it's a fast and lightweight environment that's also popular and actively supported. However, this Sandbox template is fully customizable and you can create your own desktop environment.
Check out the code [here](./template/)
