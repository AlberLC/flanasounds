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

![windows outputs](https://user-images.githubusercontent.com/37489786/113772424-f92c9f00-9724-11eb-86af-80f4f42af3c2.png)


Now we need to make the sound of your microphone be heard by that new output:

![properties](https://user-images.githubusercontent.com/37489786/113772472-077abb00-9725-11eb-8a2b-a744448c21a6.png)

![listen tab settings](https://user-images.githubusercontent.com/37489786/113772535-1bbeb800-9725-11eb-868a-79daf67b9c4a.png)

![listen this device](https://user-images.githubusercontent.com/37489786/113772693-51fc3780-9725-11eb-90f1-bc5e67fea6bd.png)


We are going to use the new audio output as a microphone:

![discord audio settings](https://user-images.githubusercontent.com/37489786/113772712-5aed0900-9725-11eb-9a98-fd8ebb4ed8e9.png)


<ins>**2. Install FlanaSounds.**  </ins>

You have 2 options.

<ins>a) Recommended option:</ins>

Download the release and unzip it:

![releases](https://user-images.githubusercontent.com/37489786/113772761-6a6c5200-9725-11eb-89da-e61b649e137a.png)

![download release](https://user-images.githubusercontent.com/37489786/113772784-735d2380-9725-11eb-8809-a65aee792c35.png)


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
   
    You might prefer to install keyboard separately via root so you don't have to run the program as root every time.    
    ```
    pip install -r requirements.txt
    ```


## Usage
Run `FlanaSounds.exe` if you downloaded the release or run `main.pyw` if you cloned the repository.

Once we see the main screen, the first thing we want to do is choose the folder where the sounds are stored.

Keep in mind that you have to organize the sounds in different subfolders, which FlanaSounds will detect as categories.

![folder](https://user-images.githubusercontent.com/37489786/113772868-8e2f9800-9725-11eb-8b05-98b700a74f07.gif)


The next thing will be to choose the virtual audio output:

![outputs](https://user-images.githubusercontent.com/37489786/113772911-9a1b5a00-9725-11eb-8bb3-e9364e4ad520.gif)


If we activate the checkbox, the sound will be reproduced both by the selected output and by the default output of your operating system. You can adjust the volume of both outputs at the bottom of the interface or by pressing the `+`/`-` keys of the numpad.

![both outputs](https://user-images.githubusercontent.com/37489786/113772968-adc6c080-9725-11eb-9dbe-a3f1cc68083d.png)


We can choose the key to speak. FlanaSounds will automatically press this key before playing a sound and release it when finished.

![keys to talk](https://user-images.githubusercontent.com/37489786/113772994-b4553800-9725-11eb-90ec-dc7a249c7fdb.gif)


Once you have everything ready you can use FlanaSounds. Choose each category by clicking with the mouse or by pressing the normal numeric keys (above qwerty...) and play each sound, within a selected category, with the mouse or by pressing the numeric keys of the numpad. if you want to prevent FlanaSounds from playing sounds you can deselect all categories by pressing `escape` key.

When a sound is playing, you can pause/resume it by clicking the button below or pressing the `0` key on the numpad.

You can stop all sounds by pressing the button or by pressing the `.`/`supr` key of the numpad (period key).


## License
Distributed under the MIT License. See [LICENSE](https://github.com/AlberLC/flananini/blob/main/LICENSE) for more information.

