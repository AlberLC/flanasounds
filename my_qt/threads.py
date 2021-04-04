import io
import json
from collections import defaultdict
from multiprocessing.pool import Pool, ThreadPool
from pathlib import Path

from PySide2 import QtCore, QtWidgets

from config import settings
from my_qt.tree_widgets import CategoryTreeWidgetItem, SoundTreeWidgetItem
from pydub import AudioSegment, effects

translate = QtWidgets.QApplication.translate


def _load_sound_bytes(sound_path):
    buffer = io.BytesIO()
    try:
        sound = AudioSegment.from_file(sound_path)
    except:
        return

    sound = effects.normalize(sound)
    sound.export(buffer, format='wav', parameters=['-ac', '2', '-ar', '44100'])
    return buffer.getvalue()


def _load_sound_category(args):
    category, new_category_name, folder_path, discarded_extensions = args
    sound_paths = [sound_path for sound_path in folder_path.glob(f'{new_category_name}/*') if
                   sound_path.suffix not in discarded_extensions]

    with ThreadPool(10) as pool:
        res = pool.map(_load_sound_bytes, sound_paths)

    for i, sound_path in enumerate(sound_paths):
        category[sound_path.stem] = res[i]

    return category


class FFmpegThread(QtCore.QThread):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def _add_sorted_tree_items(self):
        categories_to_clean = defaultdict(list)

        i = 0
        categories = self.controller.sounds.items()
        for category_name, sounds in categories:
            top_level_item = CategoryTreeWidgetItem(index=i, name=category_name)

            category_sounds = self.controller.sounds[category_name].items()
            j = 0
            for sound_name, bytes_ in category_sounds:
                if bytes_:
                    top_level_item.addChild(SoundTreeWidgetItem(index=j, name=sound_name))
                else:
                    j -= 1
                    categories_to_clean[category_name].append(sound_name)
                j += 1

            if len(categories_to_clean[category_name]) < len(self.controller.sounds[category_name]):
                self.controller.gui.tree_sounds.addTopLevelItem(top_level_item)
            else:
                i -= 1
            i += 1

        self._clean_old_sounds(categories_to_clean)

    def _clean_old_sounds(self, categories_to_clean):
        for category_name, sound_names in categories_to_clean.items():
            if len(sound_names) == len(self.controller.sounds[category_name]):
                del self.controller.sounds[category_name]
            else:
                for sound_name in sound_names:
                    del self.controller.sounds[category_name][sound_name]

    def _load_sound_bytes(self):
        folder_path = Path(self.controller.folder)
        new_categories = [path.stem for path in folder_path.glob('*')]
        discarded_extensions = json.loads(settings['discarded_extensions'])
        args = [(self.controller.sounds[new_category_name], new_category_name, folder_path, discarded_extensions) for
                new_category_name in new_categories]

        if self.controller.pool:
            self.controller.pool.terminate()

        with Pool(5) as pool:
            self.controller.pool = pool
            res = pool.map(_load_sound_category, args)

        for i, category in enumerate(new_categories):
            self.controller.sounds[category] = res[i]

    def run(self):
        try:
            self.controller.gui.tree_sounds.clear()
            self._load_sound_bytes()
            self._add_sorted_tree_items()
            self.controller.save_sounds()
        except:
            self.controller.gui.tree_sounds.clear()
        finally:
            self.controller.set_loading_gif_visible(False)
