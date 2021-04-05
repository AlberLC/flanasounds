# FlanaSounds
An application to play sounds through the microphone, perfect for discord or any game with voice chat.

## Built with
1. [Python](https://www.python.org/) - Programming Language.
2. [PySide2](https://pypi.org/project/PySide2/) - The official Python module from the Qt for Python project, which provides access to the complete Qt 5.12+ framework.
3. [keyboard](https://github.com/boppreh/keyboard) - Library to handle the keyboard.

## Installation
### Windows
<ins>**1. Install a virtual cable.**</ins>

Install a virtual cable like https://vb-audio.com/Cable/.

Once you have installed it, go to the windows audio output settings. Be careful, when you install this vb-audio cable, the virtual output is set by default, change it to the one you had before:

Now we need to make the sound of your microphone be heard by that new output:

We are going to use the new audio output as a microphone:

<ins>**2. Install FlanaSounds.**  </ins>

You have 2 options:

<ins>a) Recommended option:</ins>

Download the release and run FlanaSounds.exe

<ins>b) Clone the repository:</ins>
1. Install Python.
2. Clone the repository.

```
git clone https://github.com/AlberLC/flanasounds.git
```

3. Install the pip packages.  
```
pip install -r requirements.txt
```

### Linux
keyboard library needs root on Linux.

1. Install Python.
2. Clone the repository.  
    ```
    git clone https://github.com/AlberLC/flanasounds.git
    ```
3. Install the pip packages.

   You might prefer to install keyboard via root so you don't have to run the program as root every time.
   
   ```
   pip install -r requirements.txt
   ```

## Usage
Run `FlanaSounds.exe` if you downloaded the release or run `main.pyw` if you cloned the repository.

## License
Distributed under the MIT License. See [LICENSE](https://github.com/AlberLC/flananini/blob/main/LICENSE) for more information.

