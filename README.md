# FlanaSounds
An application to play sounds through the microphone, perfect for discord or any game with voice chat.

## Built with
1. [Python](https://www.python.org/) - Programming Language.
2. [PySide2](https://pypi.org/project/PySide2/) - The official Python module from the Qt for Python project, which provides access to the complete Qt 5.12+ framework.
3. [keyboard](https://github.com/boppreh/keyboard) - Library to handle the keyboard.

## Installation
### Windows
**1. Install a virtual cable.**
  Install a virtual cable like https://vb-audio.com/Cable/.

  Once you have installed it, go to the windows audio output settings. Be careful, when you install this vb-audio cable, the virtual output is set by default, change it to the one you had before:  
  ![windows outputs](https://user-images.githubusercontent.com/37489786/113630009-84475f80-9667-11eb-8141-9de8d21f8704.png)

  Now we need to make the sound of your microphone be heard by that new output:  
  ![properties](https://user-images.githubusercontent.com/37489786/113629638-01260980-9667-11eb-853f-35a73f87e3c7.png)
  ![listen tab settings](https://user-images.githubusercontent.com/37489786/113629634-008d7300-9667-11eb-9ab4-00e62bb34e43.png)
  ![listen this device](https://user-images.githubusercontent.com/37489786/113629637-008d7300-9667-11eb-8a6e-b3a2f342ef18.png)

  We are going to use the new audio output as a microphone:  
  ![discord audio settings](https://user-images.githubusercontent.com/37489786/113629551-dd62c380-9666-11eb-89a3-e622820af162.png)

**2. Install FlanaSounds.**  
      You have 2 options:
  
  **a) Recommended option:**  
        Download the release and run FlanaSounds.exe
        ![releases](https://user-images.githubusercontent.com/37489786/113630870-e3f23a80-9668-11eb-8de4-5f9a051685b5.png)
        ![download release](https://user-images.githubusercontent.com/37489786/113630864-e0f74a00-9668-11eb-92ff-0d72df2802fd.png)
  
  **b) Clone the repository**    
  1. Install Python.
  2. Clone the repository.  
     ` git clone https://github.com/AlberLC/flanasounds.git`
  3. Install the pip packages.  
     `pip install -r requirements.txt`

### Linux
keyboard library needs root on Linux.

1. Install Python.
2. Clone the repository.  
    `git clone https://github.com/AlberLC/flanasounds.git`
3. Install the pip packages.  
   You might prefer to install keyboard via root so you don't have to run the program as root every time.  
   `pip install -r requirements.txt`

## Usage
Run `FlanaSounds.exe` if you downloaded the release or run `main.pyw` if you cloned the repository.

## License
Distributed under the MIT License. See [LICENSE](https://github.com/AlberLC/flananini/blob/main/LICENSE) for more information.

