import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

import os
import mutagen
import csv

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)

    input_path = os.path.dirname(os.path.realpath(__file__))
    files = []
    filename = 'output'
    extention = 'csv'

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.input_path = path if path != os.sep else os.path.dirname(os.path.realpath(__file__))
        self.dismiss_popup()

    def save(self, path, filename):
        self.files = [(f, os.path.join(self.input_path, f)) for f in os.listdir(self.input_path) if os.path.isfile(os.path.join(self.input_path, f))]
        self.output_path = path if path != os.sep else os.path.dirname(os.path.realpath(__file__))
        self.filename = filename or self.filename

        write_filename = os.path.join(self.output_path, '{}.{}'.format(self.filename, self.extention))
        metadata = []

        for f in self.files:
            try:
                metadata.append({'filename': f[0], 'metadata': mutagen.File(f[1])})
            except mutagen.mp3.HeaderNotFoundError as err:
                print('ERROR: Bad file, ', err)

        metadata = [m for m in metadata if m.get('metadata')]

        with open(write_filename, 'w', encoding='utf-8') as write_file:
            csv_writer = csv.writer(write_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            col_names = ['Имя файла', 'Название', 'Исполнитель', 'Жанр', 'Альбом', 'Композитор', 'Комментарий']
            csv_writer.writerow([i.encode('utf8').decode('utf8') for i in col_names])

            for row in metadata:
                filename = row.get('filename', '')
                meta = row.get('metadata')
                name = meta.get('TIT2', '')
                singer = meta.get('TPE1', '')
                genre = meta.get('TXXX:WM/GenreID ', '')
                album = meta.get('TALB', '')
                composer = meta.get('TCOM', '')
                comment = meta.get('COMM::rus', '')

                csv_writer.writerow([filename, name, singer, genre, album, composer, comment])

        self.dismiss_popup()

class MainApp(App):
    title = 'Информация о музыке'

    def build(self):
        return Root()

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == '__main__':
    MainApp().run()
