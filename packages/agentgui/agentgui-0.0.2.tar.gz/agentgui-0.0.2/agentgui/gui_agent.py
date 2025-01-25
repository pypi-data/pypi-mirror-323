"""
AgentGUI - An agent-based wrapper for PyAutoGUI
Provides a multi-agent system for GUI automation with safety features and coordination.
"""

import easyocr
import numpy as np
import pyautogui
import pyperclip
from PIL import Image

import asyncio
import logging
import os
import platform
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pyautogui
from openai import OpenAI
from pydantic import BaseModel, Field
from rich.panel import Panel
from rich.console import Console

# Add required imports
import psutil
import shutil
import signal
import webbrowser
from subprocess import PIPE, Popen

# Configure logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
console = Console()

APP_COMMANDS = {
    "linux": {
        # Browsers
        "edge": "microsoft-edge",
        "chrome": "google-chrome",
        "firefox": "firefox",
        "chromium": "chromium-browser",

        # Terminals
        "terminal": "gnome-terminal",
        "konsole": "konsole",
        "xterm": "xterm",

        # IDEs and Editors
        "code": "code",
        "sublime": "subl",
        "pycharm": "pycharm-community",
        "pycharm-community": "pycharm-community",
        "gedit": "gedit",
        "kate": "kate",
        "vim": "vim",
        "nano": "nano",

        # File Managers
        "nautilus": "nautilus",
        "dolphin": "dolphin",
        "thunar": "thunar",
        "nemo": "nemo",

        # System Tools
        "system-monitor": "gnome-system-monitor",
        "settings": "gnome-control-center",
        "calculator": "gnome-calculator"
    },
    "windows": {
        # Browsers
        "edge": "msedge.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",

        # Terminals
        "terminal": "cmd.exe",
        "powershell": "powershell.exe",
        "windows-terminal": "wt.exe",

        # IDEs and Editors
        "code": "code.exe",
        "sublime": "sublime_text.exe",
        "pycharm": "pycharm64.exe",
        "notepad": "notepad.exe",
        "wordpad": "wordpad.exe",

        # File Managers
        "explorer": "explorer.exe",

        # System Tools
        "task-manager": "taskmgr.exe",
        "control-panel": "control.exe",
        "calculator": "calc.exe"
    },
    "darwin": {  # macOS
        # Browsers
        "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
        "safari": "/Applications/Safari.app/Contents/MacOS/Safari",

        # Terminals
        "terminal": "/System/Applications/Terminal.app/Contents/MacOS/Terminal",
        "iterm": "/Applications/iTerm.app/Contents/MacOS/iTerm2",

        # IDEs and Editors
        "code": "/Applications/Visual Studio Code.app/Contents/MacOS/Electron",
        "sublime": "/Applications/Sublime Text.app/Contents/MacOS/sublime_text",
        "pycharm": "/Applications/PyCharm.app/Contents/MacOS/pycharm",
        "textedit": "/System/Applications/TextEdit.app/Contents/MacOS/TextEdit",

        # File Managers
        "finder": "/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder",

        # System Tools
        "activity-monitor": "/System/Applications/Utilities/Activity Monitor.app/Contents/MacOS/Activity Monitor",
        "system-preferences": "/System/Applications/System Settings.app/Contents/MacOS/System Settings",
        "calculator": "/System/Applications/Calculator.app/Contents/MacOS/Calculator"
    }
}


class GUIMessageType(Enum):
    """Extended message types for system automation"""
    # Previous message types
    AI_MESSAGE = "ai_message"
    DEFAULT = "default"
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_DRAG = "mouse_drag"
    MOUSE_SCROLL = "mouse_scroll"
    KEYBOARD_TYPE = "keyboard_type"
    KEYBOARD_HOTKEY = "keyboard_hotkey"
    KEYBOARD_PRESS = "keyboard_press"
    SCREEN_LOCATE = "screen_locate"
    SCREEN_SHOT = "screen_shot"
    SCREEN_OCR_COORDINATES = "screen_ocr_coordinates"
    ALERT = "alert"

    # New message types
    TERMINAL_COMMAND = "terminal_command"
    APP_LAUNCH = "app_launch"
    APP_CLOSE = "app_close"
    APP_FOCUS = "app_focus"
    SYSTEM_INFO = "system_info"
    FILE_OPERATION = "file_operation"
    BROWSER_OPEN = "browser_open"
    CODE_EXECUTION = "code_execution"

    ERROR = "error"
    SUCCESS = "success"


@dataclass
class GUIMessage:
    """Message format for communication between agents"""
    target: str
    type: GUIMessageType | str = 'default'
    content: str | Dict[str, Any] | None = None
    source: str = 'default'
    id: Optional[str] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        self.timestamp = time.time()
        if self.content is None:
            self.content = {}
        elif isinstance(self.content, str):
            self.content = {"text": self.content}


class GUIAgentException(Exception):
    """Base exception for GUI agents"""
    pass


class BaseGUIAgent(ABC):
    """Base class for all GUI agents"""

    def __init__(self, name: str, failsafe: bool = True, pause: float = 0.1):
        self.name = name
        self.failsafe = failsafe
        self.pause = pause
        self.message_queue: List[GUIMessage] = []
        self._setup_safety()

    def _setup_safety(self):
        """Configure PyAutoGUI safety settings"""
        pyautogui.FAILSAFE = self.failsafe
        pyautogui.PAUSE = self.pause

    @abstractmethod
    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Process incoming messages"""
        pass

    async def send_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Send a message to another agent"""
        if message.source != self.name:
            message.source = self.name
        try:
            logger.debug(f"Agent: {self.name} sending message to Agent: {message.target} Action: {message.type.value}")
            return await self.runtime.route_message(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise GUIAgentException(f"Message sending failed: {e}")

    def __str__(self):
        return self.name


class MouseAgent(BaseGUIAgent):
    """Agent responsible for mouse operations"""

    def __init__(self, name: str = "mouse_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle mouse-related messages"""
        try:
            if message.type == GUIMessageType.MOUSE_MOVE:
                x = message.content.get("x")
                y = message.content.get("y")
                duration = message.content.get("duration", 0)
                tween = message.content.get("tween", pyautogui.easeInOutQuad)

                if self.runtime.validate_coordinates(x, y):
                    pyautogui.moveTo(x, y, duration=duration, tween=tween)
                    return GUIMessage(
                        type=GUIMessageType.SUCCESS,
                        content={"position": pyautogui.position()},
                        source=self.name,
                        target=message.source
                    )

            elif message.type == GUIMessageType.MOUSE_CLICK:
                button = message.content.get("button", "left")
                clicks = message.content.get("clicks", 1)
                interval = message.content.get("interval", 0.0)
                pyautogui.click(button=button, clicks=clicks, interval=interval)

            elif message.type == GUIMessageType.MOUSE_DRAG:
                x = message.content.get("x")
                y = message.content.get("y")
                duration = message.content.get("duration", 0.0)
                button = message.content.get("button", "left")
                pyautogui.dragTo(x, y, duration=duration, button=button)

            elif message.type == GUIMessageType.MOUSE_SCROLL:
                clicks = message.content.get("clicks", 1)
                pyautogui.scroll(clicks)

            return GUIMessage(
                type=GUIMessageType.SUCCESS,
                content={"action": message.type.value},
                source=self.name,
                target=message.source
            )

        except Exception as e:
            logger.error(f"Mouse action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class WritingAgent(BaseGUIAgent):
    """Agent specialized for writing text with customizable typing behavior"""

    def __init__(self, name: str = "writing_agent", typing_speed: float = 0.01):
        super().__init__(name)
        self.typing_speed = typing_speed

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle text writing with various options"""
        try:
            if message.type == GUIMessageType.DEFAULT.value:
                text = message.content.get("text", "")
                speed = message.content.get("speed", self.typing_speed)
                pause_after = message.content.get("pause_after", 0.0)

                # Write the text with specified interval
                pyautogui.write(text, interval=speed)

                if pause_after > 0:
                    time.sleep(pause_after)

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={
                        "text": text,
                        "speed": speed,
                        "action": "text_written"
                    },
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Writing action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class EnterAgent(BaseGUIAgent):
    """Agent specialized for pressing Enter key with various options"""

    def __init__(self, name: str = "enter_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle Enter key presses with various options"""
        try:
            if message.content is None:
                message.content = {}

            if message.type == GUIMessageType.DEFAULT.value:
                times = message.content.get("times", 1)
                interval = message.content.get("interval", 0.1)
                pause_after = message.content.get("pause_after", 0.0)

                # Press Enter the specified number of times
                pyautogui.press('enter', presses=times, interval=interval)

                if pause_after > 0:
                    time.sleep(pause_after)

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={
                        "times": times,
                        "interval": interval,
                        "action": "enter_pressed"
                    },
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Enter key action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class CloseWindowAgent(BaseGUIAgent):
    """Agent specialized for pressing Enter key with various options"""

    def __init__(self, name: str = "close_window_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage = None) -> Optional[GUIMessage]:
        """Handle Enter key presses with various options"""
        try:
            if message.type == GUIMessageType.DEFAULT.value:
                # Press Enter the specified number of times
                pyautogui.hotkey('ctrl', 'w')

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Enter key action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class CloseApplicationAgent(BaseGUIAgent):
    """Agent specialized for pressing Enter key with various options"""

    def __init__(self, name: str = "close_application_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage = None) -> Optional[GUIMessage]:
        """Handle Enter key presses with various options"""
        try:
            if message.type == GUIMessageType.DEFAULT.value:
                # Press Enter the specified number of times
                pyautogui.hotkey('alt', 'f4')

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={},
                    source=self.name,
                    target=message.source
                )
            else:
                logger.info('No key Pressed')

        except Exception as e:
            logger.error(f"Enter key action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class CopyDisplayTextAgent(BaseGUIAgent):
    """Agent specialized for pressing Enter key with various options"""

    def __init__(self, name: str = "copy_display_text_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage = None) -> Optional[GUIMessage]:
        """Handle Enter key presses with various options"""
        try:
            if message.type == GUIMessageType.KEYBOARD_PRESS:
                pyautogui.hotkey('ctrl', 'a')
                await asyncio.sleep(1)
                pyautogui.hotkey('ctrl', 'c')
                clipboard_content = pyperclip.paste()

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"text": clipboard_content},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Enter key action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )

class Answer(BaseModel):
    reason:str
    yes_or_no:str
    single_word:str = Field(description='most relevant word in given words that suits to answer ( each word is clickable)')

class AIAgent(BaseGUIAgent):
    """Agent specialized for pressing Enter key with various options"""

    def __init__(self, name: str = "ai_agent"):
        self.client = OpenAI()
        super().__init__(name)

    async def handle_message(self, message: GUIMessage = None) -> Optional[GUIMessage]:
        """Handle Enter key presses with various options"""
        try:
            if message.type == GUIMessageType.AI_MESSAGE:
                messages = message.content.get('text', message.content.get('messages', []))

                res = self.client.beta.chat.completions.parse(
                    temperature=0,
                    model=os.environ['OPENAI_MODEL_NAME'],
                    messages=messages,
                response_format=Answer).choices[0].message.parsed

                renderable = ""
                if isinstance(messages, list):
                    for m in messages:
                        renderable += m["role"].center(50, '-') + f"\n{m['content']}\n"
                else:
                    renderable = "Input".center(50, '-') + f"\n{messages}"

                renderable += "assistant".center(50, '-') + f"\n{res}\n"

                console.print(Panel(renderable=renderable,
                                    title_align='left',
                                    title=f'Agent: {self.name}',
                                    ))
                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"text": res.single_word},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Enter key action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class KeyboardAgent(BaseGUIAgent):
    """Agent responsible for keyboard operations"""

    def __init__(self, name: str = "keyboard_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle keyboard-related messages"""
        try:
            if message.type == GUIMessageType.KEYBOARD_TYPE:
                text = message.content.get("text")
                interval = message.content.get("interval", 0.0)
                pyautogui.write(text, interval=interval)

            elif message.type == GUIMessageType.KEYBOARD_HOTKEY:
                keys = message.content.get("keys", [])
                pyautogui.hotkey(*keys)

            elif message.type == GUIMessageType.KEYBOARD_PRESS:
                key = message.content.get("key")
                presses = message.content.get("presses", 1)
                interval = message.content.get("interval", 0.0)
                pyautogui.press(key, presses=presses, interval=interval)

            return GUIMessage(
                type=GUIMessageType.SUCCESS,
                content={"action": message.type.value},
                source=self.name,
                target=message.source
            )

        except Exception as e:
            logger.error(f"Keyboard action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class ScreenAgent(BaseGUIAgent):
    """Agent responsible for screen operations"""

    def __init__(self, name: str = "screen_agent"):
        super().__init__(name)
        self.ocr_reader = easyocr.Reader(['en'])

    def get_ocr_coords(self, path):
        result = self.ocr_reader.readtext(path)
        return result

    async def get_word_coordinate(self, path, word):
        result = self.get_ocr_coords(path)
        await asyncio.sleep(1)
        ans = []
        for w in result:
            if word in w[-2]:
                ans.append(w)
        return ans[0] if len(ans) == 1 else None

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle screen-related messages"""
        try:
            if message.type == GUIMessageType.SCREEN_SHOT:
                region = message.content.get("region", None)
                filename = message.content.get("filename", None)

                if region:
                    screenshot = pyautogui.screenshot(filename, region=region)
                else:
                    screenshot = pyautogui.screenshot(filename)

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"screenshot": screenshot},
                    source=self.name,
                    target=message.source
                )

            elif message.type == GUIMessageType.SCREEN_OCR_COORDINATES:
                region = message.content.get("region", None)
                filename = message.content.get("filename", None)

                if region:
                    screenshot = pyautogui.screenshot(filename, region=region)
                else:
                    screenshot = pyautogui.screenshot(filename)

                coords = self.get_ocr_coords(np.array(screenshot))

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"coords": coords},
                    source=self.name,
                    target=message.source
                )

            elif message.type == GUIMessageType.SCREEN_LOCATE:
                text = message.content.get("text")
                confidence = message.content.get("confidence", 0.9)

                img = pyautogui.screenshot()
                await asyncio.sleep(1)
                loc = await self.get_word_coordinate(np.array(img), text)
                if loc and loc[-1] >= confidence:
                    loc = loc[0]
                    center = pyautogui.click(x=(loc[0][0] + loc[1][0]) / 2,
                                             y=(loc[0][1] + loc[2][1]) / 2)
                    return GUIMessage(
                        type=GUIMessageType.SUCCESS,
                        content={"location": loc, "center": center},
                        source=self.name,
                        target=message.source
                    )
                else:
                    return GUIMessage(
                        type=GUIMessageType.ERROR,
                        content={"error": "Image not found"},
                        source=self.name,
                        target=message.source
                    )

        except Exception as e:
            logger.error(f"Screen action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class AlertAgent(BaseGUIAgent):
    """Agent responsible for alerts and message boxes"""

    def __init__(self, name: str = "alert_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle alert-related messages"""
        try:
            if message.type == GUIMessageType.DEFAULT.value:
                text = message.content.get("text", "")
                title = message.content.get("title", "")
                button = message.content.get("button", "OK")

                pyautogui.alert(text=text, title=title, button=button)
                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"action": "alert_shown"},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Alert action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class ConfirmAgent(BaseGUIAgent):
    """Agent responsible for alerts and message boxes"""

    def __init__(self, name: str = "confirm_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle alert-related messages"""
        try:
            if message.type == GUIMessageType.DEFAULT.value:
                text = message.content.get("text", "")
                title = message.content.get("title", "")
                button = message.content.get("button", ["OK", "CANCEL"])

                res = pyautogui.confirm(text=text, title=title, buttons=button)

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"text": res},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Alert action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class PromptAgent(BaseGUIAgent):
    """Agent responsible for alerts and message boxes"""

    def __init__(self, name: str = "prompt_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle alert-related messages"""
        try:
            if message.type == GUIMessageType.DEFAULT.value:
                text = message.content.get("text", "")
                title = message.content.get("title", "")
                default = message.content.get("default", "")

                res = pyautogui.prompt(text=text, title=title, default=default)
                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"text": res},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Alert action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class TerminalAgent(BaseGUIAgent):
    """Agent for terminal operations with persistent working directory"""

    def __init__(self, name: str = "terminal_agent"):
        super().__init__(name)
        self.is_windows = platform.system() == "Windows"
        self.current_working_dir = os.getcwd()

    async def execute_single_command(self, command: str, cwd: str) -> dict:
        """Execute a single command and update working directory if needed"""
        try:
            logger.info(f"Executing command: {command}")

            # Handle cd commands specially
            if command.strip().startswith('cd '):
                new_dir = command.strip()[3:].strip()
                # Handle both absolute and relative paths
                if os.path.isabs(new_dir):
                    target_dir = new_dir
                else:
                    target_dir = os.path.join(self.current_working_dir, new_dir)

                if os.path.exists(target_dir) and os.path.isdir(target_dir):
                    self.current_working_dir = os.path.abspath(target_dir)
                    return {
                        "command": command,
                        "stdout": "",
                        "stderr": "",
                        "returncode": 0,
                        "success": True,
                        "error": None,
                        "cwd": self.current_working_dir
                    }
                else:
                    return {
                        "command": command,
                        "stdout": "",
                        "stderr": f"Directory not found: {target_dir}",
                        "returncode": 1,
                        "success": False,
                        "error": "Directory not found",
                        "cwd": self.current_working_dir
                    }

            # For non-cd commands, execute in current working directory
            if self.is_windows:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=self.current_working_dir,
                    text=True
                )
            else:
                process = subprocess.Popen(
                    ['bash', '-c', command],
                    stdout=PIPE,
                    stderr=PIPE,
                    cwd=self.current_working_dir,
                    text=True
                )

            stdout, stderr = process.communicate()

            return {
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": process.returncode,
                "success": process.returncode == 0,
                "error": None,
                "cwd": self.current_working_dir
            }

        except Exception as e:
            logger.error(f"Command failed: {command} with error: {e}")
            return {
                "command": command,
                "stdout": "",
                "stderr": "",
                "returncode": -1,
                "success": False,
                "error": str(e),
                "cwd": self.current_working_dir
            }

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle terminal-related messages with support for command lists"""
        try:
            if message.type == GUIMessageType.TERMINAL_COMMAND:
                command = message.content.get("command")
                initial_cwd = message.content.get("cwd")

                # Set initial working directory if provided
                if initial_cwd:
                    self.current_working_dir = os.path.abspath(initial_cwd)

                wait = message.content.get("wait", True)

                # Handle both single command and list of commands
                commands = command if isinstance(command, list) else [command]

                if not wait:
                    # For non-waiting execution, launch all commands and return PIDs
                    processes = []
                    for cmd in commands:
                        if self.is_windows:
                            process = subprocess.Popen(cmd, shell=True, cwd=self.current_working_dir)
                        else:
                            process = subprocess.Popen(['bash', '-c', cmd], cwd=self.current_working_dir)
                        processes.append({"command": cmd, "pid": process.pid})

                    return GUIMessage(
                        type=GUIMessageType.SUCCESS,
                        content={"processes": processes, "cwd": self.current_working_dir},
                        source=self.name,
                        target=message.source
                    )

                # For waiting execution, run commands sequentially and collect results
                results = []
                all_successful = True
                final_returncode = 0

                for cmd in commands:
                    result = await self.execute_single_command(cmd, self.current_working_dir)
                    results.append(result)

                    if not result["success"]:
                        all_successful = False
                        final_returncode = result["returncode"] if result["returncode"] != -1 else 1

                # Prepare summary statistics
                summary = {
                    "total_commands": len(commands),
                    "successful_commands": sum(1 for r in results if r["success"]),
                    "failed_commands": sum(1 for r in results if not r["success"]),
                    "all_successful": all_successful,
                    "final_returncode": final_returncode,
                    "final_cwd": self.current_working_dir
                }

                return GUIMessage(
                    type=GUIMessageType.SUCCESS if all_successful else GUIMessageType.ERROR,
                    content={
                        "results": results,
                        "summary": summary
                    },
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Terminal agent failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={
                    "error": str(e),
                    "results": [],
                    "summary": {
                        "total_commands": 0,
                        "successful_commands": 0,
                        "failed_commands": 0,
                        "all_successful": False,
                        "final_returncode": -1,
                        "final_cwd": self.current_working_dir
                    }
                },
                source=self.name,
                target=message.source
            )


class ApplicationAgent(BaseGUIAgent):
    """Agent for application management"""

    def __init__(self, name: str = "application_agent"):
        super().__init__(name)
        self.system = platform.system().lower()

    def _get_app_command(self, app_name: str) -> str:
        """Get the command to launch an application based on the system"""
        return APP_COMMANDS.get(self.system, {}).get(app_name.lower(), app_name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle application-related messages"""
        try:
            if message.type == GUIMessageType.APP_LAUNCH:
                app_name = message.content.get("text")
                args = message.content.get("args", [])

                cmd = self._get_app_command(app_name)

                if self.system == "darwin":
                    subprocess.Popen(["open", "-a", cmd] + args)
                else:
                    subprocess.Popen([cmd] + args)

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"app": app_name, "action": "launched"},
                    source=self.name,
                    target=message.source
                )

            elif message.type == GUIMessageType.APP_CLOSE:
                app_name = message.content.get("app_name")
                cmd = self._get_app_command(app_name)

                for proc in psutil.process_iter(['name']):
                    if cmd.lower() in proc.info['name'].lower():
                        proc.terminate()

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"app": app_name, "action": "closed"},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"Application action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class SystemAgent(BaseGUIAgent):
    """Agent for system operations"""

    def __init__(self, name: str = "system_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle system-related messages"""
        try:
            if message.type == GUIMessageType.SYSTEM_INFO:
                info_type = message.content.get("type", "all")

                if info_type == "all":
                    info = {
                        "platform": platform.platform(),
                        "processor": platform.processor(),
                        "memory": dict(psutil.virtual_memory()._asdict()),
                        "disk": dict(psutil.disk_usage('/')._asdict()),
                        "cpu_percent": psutil.cpu_percent(interval=1),
                        "battery": dict(psutil.sensors_battery()._asdict()) if psutil.sensors_battery() else None
                    }
                else:
                    info = {}
                    if info_type == "memory":
                        info["memory"] = dict(psutil.virtual_memory()._asdict())
                    elif info_type == "cpu":
                        info["cpu_percent"] = psutil.cpu_percent(interval=1)
                    elif info_type == "disk":
                        info["disk"] = dict(psutil.disk_usage('/')._asdict())

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content=info,
                    source=self.name,
                    target=message.source
                )

            elif message.type == GUIMessageType.FILE_OPERATION:
                operation = message.content.get("operation")
                src = message.content.get("source")
                dst = message.content.get("destination")

                if operation == "copy":
                    shutil.copy2(src, dst)
                elif operation == "move":
                    shutil.move(src, dst)
                elif operation == "delete":
                    os.remove(src)
                elif operation == "mkdir":
                    os.makedirs(src, exist_ok=True)

                return GUIMessage(
                    type=GUIMessageType.SUCCESS,
                    content={"operation": operation, "path": src},
                    source=self.name,
                    target=message.source
                )

        except Exception as e:
            logger.error(f"System action failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


class CodeAgent(BaseGUIAgent):
    """Agent for code execution and management"""

    def __init__(self, name: str = "code_agent"):
        super().__init__(name)

    async def handle_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Handle code-related messages"""
        try:
            if message.type == GUIMessageType.CODE_EXECUTION:
                code = message.content.get("code")
                language = message.content.get("language", "python")

                if language == "python":
                    # Create a temporary file
                    temp_file = "temp_code.py"
                    with open(temp_file, "w") as f:
                        f.write(code)

                    # Execute the code
                    result = subprocess.run(
                        ["python", temp_file],
                        capture_output=True,
                        text=True
                    )

                    # Clean up
                    os.remove(temp_file)

                    return GUIMessage(
                        type=GUIMessageType.SUCCESS,
                        content={
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "returncode": result.returncode
                        },
                        source=self.name,
                        target=message.source
                    )

        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return GUIMessage(
                type=GUIMessageType.ERROR,
                content={"error": str(e)},
                source=self.name,
                target=message.source
            )


@dataclass
class GUIResult:
    final_answer: GUIMessage
    intermediate_steps: List[GUIMessage]


class GUIRuntime:
    """Runtime environment for GUI agents"""

    def __init__(self, delay: int = 1):
        self.delay = delay
        self.agents: Dict[str, BaseGUIAgent] = {}
        self.screen_size = pyautogui.size()
        self.runtime_agent = None

    def register_agent(self, agent: BaseGUIAgent):
        """Register an agent with the runtime"""
        self.agents[agent.name] = agent
        agent.runtime = self
        logger.info(f"Registered agent: {agent.name}")

    async def route_message(self, message: GUIMessage) -> Optional[GUIMessage]:
        """Route a message to its target agent"""
        await asyncio.sleep(self.delay)
        if message.target in self.agents:
            target_agent = self.agents[message.target]
            return await target_agent.handle_message(message)
        else:
            raise GUIAgentException(f"Target agent not found: {message.target}")

    async def start(self, messages: GUIMessage | List[GUIMessage]) -> GUIResult:
        messages = messages if isinstance(messages, list) else [messages]
        steps = []
        for each_message in messages:
            res = await self.route_message(message=each_message)
            steps.append(res)

        if steps and steps[-1].source == 'close_window_agent':
            res = steps[-2] if len(steps) > 1 else steps[-1]
        return GUIResult(final_answer=res, intermediate_steps=steps)

    def validate_coordinates(self, x: int, y: int) -> bool:
        """Validate if coordinates are within screen bounds"""
        width, height = self.screen_size
        return 0 <= x < width and 0 <= y < height


# Example usage
async def main():
    # Create runtime
    runtime = GUIRuntime()

    # Create all agents
    terminal_agent = TerminalAgent()
    app_agent = ApplicationAgent()
    system_agent = SystemAgent()
    code_agent = CodeAgent()
    mouse_agent = MouseAgent()
    keyboard_agent = KeyboardAgent()
    screen_agent = ScreenAgent()
    alert_agent = AlertAgent()

    # Register agents
    runtime.register_agent(mouse_agent)
    runtime.register_agent(keyboard_agent)
    runtime.register_agent(screen_agent)
    runtime.register_agent(alert_agent)
    runtime.register_agent(terminal_agent)
    runtime.register_agent(app_agent)
    runtime.register_agent(system_agent)
    runtime.register_agent(code_agent)

    # Example: Move mouse and click
    # move_message = GUIMessage(
    #     type=GUIMessageType.MOUSE_MOVE,
    #     content={"x": 100, "y": 100, "duration": 1},
    #     source="main",
    #     target="mouse_agent"
    # )
    # await runtime.route_message(move_message)

    # click_message = GUIMessage(
    #     type=GUIMessageType.MOUSE_CLICK,
    #     content={"clicks": 2},
    #     source="main",
    #     target="mouse_agent"
    # )
    # await runtime.route_message(click_message)
    #
    # # Example: Type text
    # type_message = GUIMessage(
    #     type=GUIMessageType.KEYBOARD_TYPE,
    #     content={"text": "Hello AgentGUI!", "interval": 0.1},
    #     source="main",
    #     target="keyboard_agent"
    # )
    # await runtime.route_message(type_message)
    #
    # # Example: Take screenshot
    # screenshot_message = GUIMessage(
    #     type=GUIMessageType.SCREEN_CAPTURE,
    #     content={"filename": "screenshot.png"},
    #     source="main",
    #     target="screen_agent"
    # )
    # await runtime.route_message(screenshot_message)
    #
    # # Example: Show alert
    # alert_message = GUIMessage(
    #     type=GUIMessageType.ALERT,
    #     content={
    #         "text": "Task completed!",
    #         "title": "AgentGUI Demo",
    #         "button": "OK"
    #     },
    #     source="main",
    #     target="alert_agent"
    # )
    # await runtime.route_message(alert_message)

    #
    # # Example: Launch terminal and run command
    await runtime.route_message(GUIMessage(
        type=GUIMessageType.APP_LAUNCH,
        content={"app_name": "terminal"},
        source="main",
        target="application_agent"
    ))

    await runtime.route_message(GUIMessage(
        type=GUIMessageType.TERMINAL_COMMAND,
        content={"command": "ls -la"},
        source="main",
        target="terminal_agent"
    ))
    #
    # # Example: Open browser and navigate
    # await runtime.route_message(GUIMessage(
    #     type=GUIMessageType.BROWSER_ACTION,
    #     content={
    #         "action": "open",
    #         "url": "https://www.google.com"
    #     },
    #     source="main",
    #     target="browser_agent"
    # ))
    #
    # # Example: Get system info
    # response = await runtime.route_message(GUIMessage(
    #     type=GUIMessageType.SYSTEM_INFO,
    #     content={"type": "all"},
    #     source="main",
    #     target="system_agent"
    # ))
    # print("System Info:", response.content)
    #
    # # Example: Execute Python code
    # await runtime.route_message(GUIMessage(
    #     type=GUIMessageType.CODE_EXECUTION,
    #     content={
    #         "code": """
    # print('Hello from executed code!')
    # result = sum(range(10))
    # print(f'Sum: {result}')
    #             """,
    #         "language": "python"
    #     },
    #     source="main",
    #     target="code_agent"
    # ))


################3

async def app2():
    # Create runtime
    runtime = GUIRuntime()

    # Create and register all agents
    terminal_agent = TerminalAgent()
    app_agent = ApplicationAgent()
    system_agent = SystemAgent()
    code_agent = CodeAgent()
    mouse_agent = MouseAgent()
    keyboard_agent = KeyboardAgent()
    screen_agent = ScreenAgent()
    alert_agent = AlertAgent()

    # Register agents
    for agent in [mouse_agent, keyboard_agent, screen_agent, alert_agent,
                  terminal_agent, app_agent, system_agent, code_agent]:
        runtime.register_agent(agent)

    # Test 1: Terminal Commands
    print("\nExecuting terminal commands...")
    commands = [
        "ls -la",
        "pwd",
        "echo 'Hello from terminal!'",
        "date"
    ]

    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        response = await runtime.route_message(GUIMessage(
            type=GUIMessageType.TERMINAL_COMMAND,
            content={"command": cmd},
            source="main",
            target="terminal_agent"
        ))
        if response:
            print("Output:", response.content.get("stdout", ""))

    # Test 2: System Information
    print("\nGetting system information...")
    response = await runtime.route_message(GUIMessage(
        type=GUIMessageType.SYSTEM_INFO,
        content={"type": "all"},
        source="main",
        target="system_agent"
    ))
    if response:
        print("System Info:", response.content)

    # Test 3: Browser Actions
    print("\nOpening browser...")
    await runtime.route_message(GUIMessage(
        type=GUIMessageType.BROWSER_ACTION,
        content={
            "action": "open",
            "url": "https://www.google.com"
        },
        source="main",
        target="browser_agent"
    ))

    # Test 4: Execute Python Code
    print("\nExecuting Python code...")
    code_to_run = """
import platform
import os

print('Python Version:', platform.python_version())
print('Current Directory:', os.getcwd())
print('Simple calculation:', sum(range(10)))
"""

    response = await runtime.route_message(GUIMessage(
        type=GUIMessageType.CODE_EXECUTION,
        content={
            "code": code_to_run,
            "language": "python"
        },
        source="main",
        target="code_agent"
    ))
    if response:
        print("Code Output:", response.content.get("stdout", ""))

    # Test 5: File Operations
    print("\nPerforming file operations...")
    # Create a test directory
    await runtime.route_message(GUIMessage(
        type=GUIMessageType.FILE_OPERATION,
        content={
            "operation": "mkdir",
            "source": "test_dir"
        },
        source="main",
        target="system_agent"
    ))

    # Create a test file
    await runtime.route_message(GUIMessage(
        type=GUIMessageType.TERMINAL_COMMAND,
        content={"command": "echo 'Test content' > test_dir/test.txt"},
        source="main",
        target="terminal_agent"
    ))

    # List the contents
    response = await runtime.route_message(GUIMessage(
        type=GUIMessageType.TERMINAL_COMMAND,
        content={"command": "ls -la test_dir"},
        source="main",
        target="terminal_agent"
    ))
    if response:
        print("Test directory contents:", response.content.get("stdout", ""))

    # Clean up
    await runtime.route_message(GUIMessage(
        type=GUIMessageType.FILE_OPERATION,
        content={
            "operation": "delete",
            "source": "test_dir/test.txt"
        },
        source="main",
        target="system_agent"
    ))

    # Show completion alert
    await runtime.route_message(GUIMessage(
        type=GUIMessageType.ALERT,
        content={
            "text": "All tests completed successfully!",
            "title": "AgentGUI Tests",
            "button": "OK"
        },
        source="main",
        target="alert_agent"
    ))


if __name__ == "__main__":
    asyncio.run(app2())
