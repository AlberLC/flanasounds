import json
from collections import defaultdict
from random import choice

import keyboard
from PySide2 import QtCore, QtGui, QtMultimedia, QtWidgets

from config import config, settings, volume
from gui import Gui
from my_qt.threads import FFmpegThread

CATEGORY_SYMBOLS = {
    2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0', 12: "'?", 13: '¡?'
}


class Controller:
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
        self.talk_key = None
        self.current_top_level_item = None
        self.sounds = defaultdict(dict)
        self.thread = None
        self.movie = None
        self.pool = None

        self._load_system_outputs()
        self._load_settings()
        self._add_hotkeys()

    def _add_hotkeys(self):
        for i in range(10):
            keyboard.on_press_key(str(i), self._pressed_key)
        keyboard.on_press_key("'", self._pressed_key)
        keyboard.on_press_key('¡', self._pressed_key)
        keyboard.on_press_key('decimal', self._pressed_key)
        keyboard.on_press_key('+', self._pressed_key)
        keyboard.on_press_key('-', self._pressed_key)
        keyboard.on_press_key('esc', self._pressed_key)

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
                if self.talk_key:
                    keyboard.release(self.talk_key)
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
        self.talk_key = settings['talk_key']
        self.gui.line_talk_key.setText(self.talk_key)

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

        if self.talk_key:
            keyboard.press(self.talk_key)
        self.gui.set_play_mode()

        selected_output = self._make_output(self.selected_output_info, data, self.selected_output_volume * 0.01)
        self.selected_outputs.add(selected_output)
        self.last_output = selected_output

        speakers_output = self._make_output(self.speakers_output_info,
                                            data,
                                            volume=self.speakers_volume * 0.01 if self.play_on_speakers else 0)
        self.speakers_outputs.add(speakers_output)

    def _pressed_key(self, event):
        if (
                self.gui.spin_volume_selected.hasFocus()
                or
                self.gui.spin_volume_speakers.hasFocus()
                or
                self.gui.line_talk_key.hasFocus()
        ):
            return

        if event.is_keypad:
            if event.name == '+':
                self._volume_up()
            elif event.name == '-':
                self._volume_down()
            elif event.name == '0':
                self.pause()
            elif event.name == 'decimal':
                self.stop()
            elif self.current_top_level_item is not None:
                try:
                    self.gui.tree_sounds.itemActivated.emit(self.current_top_level_item.child(int(event.name) - 1),
                                                            0)
                except ValueError:
                    return
        else:
            if event.name == 'esc':
                self.gui.tree_sounds.setCurrentItem(None)
            else:
                for i, key_code in enumerate(CATEGORY_SYMBOLS):
                    if key_code == event.scan_code:
                        break
                else:
                    i = None
                if i is not None and i < self.gui.tree_sounds.topLevelItemCount():
                    self.gui.tree_sounds.setCurrentItem(self.gui.tree_sounds.topLevelItem(i))

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

    def changed_talk_key(self, talk_key):
        self.talk_key = talk_key
        settings['talk_key'] = self.talk_key
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

    def pause(self):
        if not self.selected_outputs:
            return

        if self.last_output.state() == QtMultimedia.QAudio.State.ActiveState:
            self.gui.set_pause_mode()

            for output in self.selected_outputs.copy():
                output.suspend()
            for output in self.speakers_outputs.copy():
                output.suspend()

            if self.talk_key:
                keyboard.release(self.talk_key)
        else:
            self.gui.set_play_mode()

            if self.talk_key:
                keyboard.press(self.talk_key)

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
        else:2
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

        if self.talk_key:
            keyboard.release(self.talk_key)