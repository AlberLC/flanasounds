import json
from collections import defaultdict
from random import choice

from PySide2 import QtCore, QtGui, QtMultimedia, QtWidgets
from pynput import keyboard

from config import config, settings, volume
from gui import Gui
from my_qt.threads import FFmpegThread

VK_TO_CATEGORY = {
    49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9', 48: '0', 219: "'?", 221: '¡?'
}

VK_TO_NUMPAD = {
    96: 0, 97: 1, 98: 2, 99: 3, 100: 4, 101: 5, 102: 6, 103: 7, 104: 8, 105: 9, 107: '+', 109: '-', 110: '.'
}


class Controller:
    # signal = QtCore.Signal()

    def __init__(self, gui: Gui):
        self.gui = gui
        self.folder = None
        self.outputs_info = None
        self.selected_output_info = None
        self.speakers_output_info = None
        self.selected_outputs = set()
        self.speakers_outputs = set()
        self.last_output = None
        self.play_on_speakers = True
        self.selected_output_volume = 0
        self.speakers_volume = 0
        self.keyboard = keyboard.Controller()
        self.talk_key = None
        self.current_top_level_item = None
        self.sounds = defaultdict(dict)
        self.thread = None
        self.movie = None
        self.pool = None
        # self.signal.connect(self.pause)

        self._load_system_outputs()
        self._load_settings()
        self._add_hotkeys()

    def _add_hotkeys(self):
        listener = keyboard.Listener(on_press=self._pressed_key)
        listener.start()

    def _changed_selected_output_volume(self, value):
        self.selected_output_volume = value
        volume['selected_output'] = str(value)
        config.save()
        self._set_selected_output_volume()

    def _changed_speakers_volume(self, value):
        self.speakers_volume = value
        volume['speakers_output'] = str(value)
        config.save()
        if self.play_on_speakers:
            self._set_speakers_volume()

    def _delete_output(self, output):
        state = output.state()
        if state not in (QtMultimedia.QAudio.IdleState, QtMultimedia.QAudio.StoppedState):
            return

        if output in self.selected_outputs:
            self.selected_outputs.discard(output)

            if self.selected_outputs:
                if state == QtMultimedia.QAudio.StoppedState:
                    return

                self.last_output = next(iter(self.selected_outputs))
                if self.last_output.state() == QtMultimedia.QAudio.SuspendedState:
                    self.gui.set_pause_mode()
            else:
                self.gui.set_stop_mode()
                self.last_output = None
                self._release_key_to_talk()
        else:
            self.speakers_outputs.discard(output)

    def _load_folder_settings(self):
        self.folder = settings['folder']
        if self.folder:
            self.gui.line_folder.setText(self.folder)
            try:
                sounds = json.loads(settings['sounds'])
            except:
                sounds = {}
            self.sounds = defaultdict(dict, sounds)
            self._load_tree_items()

    def _load_output_settings(self):
        settings_output_name = settings['output']
        if not settings_output_name:
            self.selected_output_info = self.outputs_info[0]
            return

        for output_info in self.outputs_info:
            if output_info.deviceName() == settings_output_name:
                self.selected_output_info = output_info
                self.gui.combo_output.setCurrentText(settings_output_name)
                break
        else:
            self.selected_output_info = self.outputs_info[0]

    def _load_play_on_speakers_settings(self):
        self.play_on_speakers = settings.getboolean('play_on_speakers')
        if self.play_on_speakers:
            state = QtCore.Qt.Checked
        else:
            state = QtCore.Qt.Unchecked
        self.gui.check_play_on_speakers.setCheckState(state)

    def _load_settings(self):
        self._load_output_settings()
        self._load_play_on_speakers_settings()
        self._load_talk_key_settings()
        self._load_volume_settings()
        self._load_folder_settings()

    def _load_system_outputs(self):
        """Get output devices without repetitions."""

        system_outputs_info = QtMultimedia.QAudioDeviceInfo.availableDevices(QtMultimedia.QAudio.AudioOutput)
        if not system_outputs_info:
            return

        self.speakers_output_info = system_outputs_info[0]

        self.outputs_info = []
        for output_info in system_outputs_info:
            loaded_outputs_names = (loaded_output_info.deviceName() for loaded_output_info in self.outputs_info)
            if output_info.deviceName() not in loaded_outputs_names:
                self.outputs_info.append(output_info)

        self.gui.combo_output.addItems(output.deviceName() for output in self.outputs_info)

    def _load_talk_key_settings(self):
        try:
            self.talk_key = set(json.loads(settings['talk_key']))
        except json.decoder.JSONDecodeError:
            self.talk_key = set()
        self.gui.line_talk_key.set_pressed_keys(self.talk_key)

    def _load_tree_items(self):
        self.set_loading_gif_visible(True)
        if self.thread:
            self.thread.terminate()
        self.thread = FFmpegThread(self.gui, self)
        self.thread.start()

    def _load_volume_settings(self):
        self.selected_output_volume = volume.getint('selected_output')
        self.speakers_volume = volume.getint('speakers_output')

        self.gui.slider_volume_selected.setValue(self.selected_output_volume)
        self.gui.spin_volume_selected.setValue(self.selected_output_volume)
        self.gui.slider_volume_speakers.setValue(self.speakers_volume)
        self.gui.spin_volume_speakers.setValue(self.speakers_volume)

    def _make_output(self, output_info, data, volume):
        output = QtMultimedia.QAudioOutput(output_info, output_info.preferredFormat())
        output.setVolume(volume)
        output.stateChanged.connect(lambda: self._delete_output(output))

        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.ReadWrite)
        buffer.write(data)
        buffer.seek(0)
        output.start(buffer)

        return output

    def _play(self, index):
        try:
            data = self.sounds[self.current_top_level_item.name][self.current_top_level_item.child(index).name]
        except IndexError:
            return

        self._press_key_to_talk()
        self.gui.set_play_mode()

        selected_output = self._make_output(self.selected_output_info, data, self.selected_output_volume * 0.01)
        self.selected_outputs.add(selected_output)
        self.last_output = selected_output

        speakers_output = self._make_output(self.speakers_output_info,
                                            data,
                                            volume=self.speakers_volume * 0.01 if self.play_on_speakers else 0)
        self.speakers_outputs.add(speakers_output)

    def _press_key_to_talk(self):
        for key in self.talk_key:
            self.keyboard.press(self._str_to_key(key))

    def _pressed_key(self, key):
        if key is keyboard.Key.esc:
            self.gui.tree_sounds.setCurrentItem(None)
            return

        if (
                type(key) is not keyboard.KeyCode
                or
                self.gui.spin_volume_selected.hasFocus()
                or
                self.gui.spin_volume_speakers.hasFocus()
                or
                self.gui.line_talk_key.hasFocus()
        ):
            return

        if key.vk in (*range(48, 58), 219, 221):  # vk codes for numbers and '? ¡¿
            try:
                index = list(VK_TO_CATEGORY.keys()).index(key.vk)
            except ValueError:
                index = None

            if index is not None and index < self.gui.tree_sounds.topLevelItemCount():
                self.gui.tree_sounds.setCurrentItem(self.gui.tree_sounds.topLevelItem(index))

        elif key.vk in range(97, 106):  # vk codes for keypad numbers
            try:
                self.gui.tree_sounds.itemActivated.emit(self.current_top_level_item.child(VK_TO_NUMPAD[key.vk] - 1), 0)
            except ValueError:
                return

        elif key.vk == 107:  # key numpad +
            self._volume_up()
        elif key.vk == 109:  # key numpad -
            self._volume_down()
        elif key.vk == 96:  # key numpad 0
            self.gui.play_pause_signal.emit()
        elif key.vk == 110:  # key numpad .
            self.stop()

    def _release_key_to_talk(self):
        for key in self.talk_key:
            self.keyboard.release(self._str_to_key(key))

    def _set_selected_output_volume(self, volume=None, outputs=None):
        volume = volume if volume is not None else self.selected_output_volume
        outputs = outputs if outputs is not None else self.selected_outputs.copy()
        for output in outputs:
            output.setVolume(volume * 0.01)

    def _set_speakers_volume(self, volume=None, outputs=None):
        volume = volume if volume is not None else self.speakers_volume
        outputs = outputs if outputs is not None else self.speakers_outputs.copy()
        for output in outputs:
            output.setVolume(volume * 0.01 if self.play_on_speakers else 0)

    def _str_to_key(self, key_str):
        if len(key_str) == 1:
            return keyboard.KeyCode(char=key_str)
        else:
            try:
                return keyboard.KeyCode(int(key_str.replace('<', '').replace('>', '')))
            except ValueError:
                return keyboard.Key[key_str]

    def _volume_down(self):
        self.gui.slider_volume_selected.setValue(self.selected_output_volume - 1)
        self.gui.slider_volume_speakers.setValue(self.speakers_volume - 1)

    def _volume_up(self):
        self.gui.slider_volume_selected.setValue(self.selected_output_volume + 1)
        self.gui.slider_volume_speakers.setValue(self.speakers_volume + 1)

    def activated_item(self, item):
        if not item or not item.parent():
            return

        self._play(index=self.gui.tree_sounds.indexFromItem(item).row())

    def changed_selected_output_volume_slider(self, value):
        self.gui.spin_volume_selected.setValue(value)
        self._changed_selected_output_volume(value)

    def changed_slected_output_volume_spin(self, value):
        self.gui.slider_volume_selected.setValue(value)
        self._changed_selected_output_volume(value)

    def changed_speakers_volume_slider(self, value):
        self.gui.spin_volume_speakers.setValue(value)
        self._changed_speakers_volume(value)

    def changed_speakers_volume_spin(self, value):
        self.gui.slider_volume_speakers.setValue(value)
        self._changed_speakers_volume(value)

    def changed_talk_key(self):
        self.talk_key = self.gui.line_talk_key.sorted_pressed_keys
        settings['talk_key'] = json.dumps(self.talk_key)
        config.save()

    def changed_tree_selection(self, item):
        if not item:
            self.current_top_level_item = None
            self.gui.tree_sounds.collapseAll()
            return
        if item.parent():
            return

        self.gui.tree_sounds.collapseAll()
        self.gui.tree_sounds.expandItem(item)
        self.gui.tree_sounds.scrollToItem(item, QtWidgets.QTreeWidget.ScrollHint.PositionAtTop)
        self.current_top_level_item = item

    def checked_play_on_speakers(self, state):
        self.play_on_speakers = bool(state)
        self._set_speakers_volume()
        settings['play_on_speakers'] = str(self.play_on_speakers)
        config.save()

    def open_explorer(self):
        self.folder = QtWidgets.QFileDialog.getExistingDirectory(dir=self.gui.line_folder.text())
        if self.folder:
            self.gui.line_folder.setText(self.folder)
            settings['folder'] = self.folder
            config.save()
            self.sounds.clear()
            self._load_tree_items()

    def play_pause(self):
        if not self.selected_outputs:
            return

        if self.last_output.state() == QtMultimedia.QAudio.State.ActiveState:
            self.gui.set_pause_mode()

            for output in self.selected_outputs.copy():
                output.suspend()
            for output in self.speakers_outputs.copy():
                output.suspend()

            self._release_key_to_talk()
        else:
            self.gui.set_play_mode()

            self._press_key_to_talk()

            for output in self.selected_outputs.copy():
                output.resume()
            for output in self.speakers_outputs.copy():
                output.resume()

    def save_sounds(self):
        sounds_dict = defaultdict(dict)
        for category, sounds in self.sounds.items():
            for sound in sounds:
                sounds_dict[category][sound] = None

        settings['sounds'] = json.dumps(sounds_dict)
        config.save()

    def set_loading_gif_visible(self, is_visible):
        gifs = [
            'loading.gif',
            'banana.gif',
            'orcas.gif',
            'reloj_de_nieve.gif',
            'nyan_cat.gif',
            'tortuga.gif',
            'epicsaxguy.gif',
            'gatocargaerror.gif',
            'cat_parade.gif'
        ]
        if is_visible:
            self.movie = QtGui.QMovie(f'resources/{choice(gifs)}')
            self.gui.label_loading_gif.setMovie(self.movie)
            self.movie.start()
            self.gui.label_loading_gif.show()
        else:
            self.gui.label_loading_gif.hide()
            self.movie.stop()

    def set_output(self, index):
        self.selected_output_info = self.outputs_info[index]
        settings['output'] = self.selected_output_info.deviceName()
        config.save()

    def stop(self):
        if not self.selected_outputs:
            return

        self.gui.set_stop_mode()
        selected_outputs = self.selected_outputs.copy()
        speakers_outputs = self.speakers_outputs.copy()

        self._set_selected_output_volume(0, selected_outputs)
        self._set_speakers_volume(0, speakers_outputs)

        for output in selected_outputs:
            output.stop()
        for output in speakers_outputs:
            output.stop()
