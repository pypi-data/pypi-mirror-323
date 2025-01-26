
# Overview
An updated DRV8825 stepper motor driver library for Raspberry Pi 5. This library is a fork of the original [DRV8825 library](https://www.waveshare.com/wiki/Stepper_Motor_HAT) and switches RPI.GPIO to lgpio to be compatible with Raspberry Pi 5. Useful for using the wave share stepper motor driver with Raspberry Pi 5.

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)

# Introduction
This is an updated version of the DRV8825 stepper motor driver library for Raspberry Pi 5. The original library was written for Raspberry Pi 3 and used RPI.GPIO. This library switches to lgpio to be compatible with Raspberry Pi 5. There are optional limit switches that can be set to stop the motor when triggered. These are especially useful for limiting the range of motion of the motor.

# Installation
Install using the pip package manager:
```bash
pip install RPI5_DRV8825
```

# Usage
```python
import RPI5_DRV8825

# Define the stepper motor driver
M1 = RPI5_DRV8825.DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20), limit_pins=(6,5))

# Set the microstepping mode
M1.set_microstep(1)
```

`limit_pins` is optional and can be used to set limit switches. If limit_pins is set, the driver will stop the motor when the limit switch is triggered.

# Contributing
Feel free to submit a PR on GitHub

# License
Currently not distributed under any license.

# Contact
* @agadin on github

# Acknowledgements
* [Waveshare](https://www.waveshare.com/wiki/Stepper_Motor_HAT) for the original library

