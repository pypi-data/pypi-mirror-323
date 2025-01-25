# World Model Kit

[![PyPI](https://img.shields.io/pypi/v/wmk.svg)](https://pypi.org/project/wmk/)
[![Tests](https://github.com/journee-live/wmk/actions/workflows/test.yml/badge.svg)](https://github.com/journee-live/wmk/actions/workflows/test.yml)

**World Model Kit (WMK)** is a comprehensive toolkit designed to streamline the development, deployment, and operation of interactive world models.

### Key Features

* **High-Performance Rendering**
   Native system integration for efficient real-time visualization of world model outputs, optimized for various display environments.

* **Interactive User Interface**
   Comprehensive input processing system with support for keyboard and mouse interactions, event handling, and real-time response capabilities.

* **Extensible Architecture**
   Built on top of Pyglet, enabling easy creation of custom window classes, event handlers, and graphics components.

* **Advanced Communication Layer**
   Robust inter-process communication system featuring seamless integration with web clients and flexible message passing capabilities.

## Installation

```bash
pip install wmk
```
## Usage

Example of using the Player and Messenger modules to create a simple interactive application with a world model frame generator:

```python
   from wmk.player import Player
   from wmk.messenger import Messenger

   is_user_connected = False

   def handle_user_connection(message):
       nonlocal is_user_connected
       is_user_connected = True if message["type"] == "connected" else False

   messenger = Messenger("/tmp/server.sock", "/tmp/client.sock")
   messenger.add_listener("connected", handle_user_connection)
   messenger.add_listener("disconnected", handle_user_connection)
   
   def frame_generator(window, dt):
       # Generate and return your frame here
       return frame if is_user_connected else empty_frame

   player = Player(frame_generator)
   player.run()

   messenger.start()
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd wmk
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.'
```
To run the tests:
```bash
python -m pytest
```
