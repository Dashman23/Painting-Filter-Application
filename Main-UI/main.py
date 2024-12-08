import sys
sys.path.insert(1, 'Back-End')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import Dithering

# Load the UI.kv file
Builder.load_file('UI.kv')

curr_img = r'IMG_1415.png'
init_img = r'IMG_1415.png'

class CustomSlider(Slider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_release')

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_release')
        return super().on_touch_up(touch)

    def on_release(self):
        pass

class MainScreen(Screen):
    image_display = ObjectProperty(None)
    slider1 = ObjectProperty(None)
    slider2 = ObjectProperty(None)

    def on_button_click(self, instance):
        print(f"{instance.text} button clicked!")

    def on_slider1_release(self, instance):
        global curr_img
        if curr_img != -1 and isinstance(curr_img, str):
            try:
                print(f"Dithering Range value: {int(instance.value)}")
                Dithering.dither_blur(curr_img, r'Temp-Pictures\dithered_and_blurred_image.png')
                self.image_display.source = r'Temp-Pictures\dithered_and_blurred_image.png'
                self.image_display.reload()
                print("Dithering complete!")
            except Exception as e:
                print(f"Error during dithering: {e}")
        else:
            print("No valid image selected.")

    def update_slider1_value(self, text):
        global curr_img
        try:
            value = int(text)
            if self.slider1.min <= value <= self.slider1.max:
                self.slider1.value = value
                if curr_img != -1 and isinstance(curr_img, str):
                    try:
                        print(f"Dithering Range value: {value}")
                        Dithering.dither_blur(curr_img, r'Temp-Pictures\dithered_and_blurred_image.png')
                        self.image_display.source = r'Temp-Pictures\dithered_and_blurred_image.png'
                        self.image_display.reload()
                        print("Dithering complete!")
                    except Exception as e:
                        print(f"Error during dithering: {e}")
            else:
                print(f"Value {value} is out of slider range.")
        except ValueError:
            print("Invalid input for slider 1")

    def on_slider2_release(self, instance):
        print(f"Color Blend Strength value: {int(instance.value)}")

    def update_slider2_value(self, text):
        try:
            value = int(text)
            if self.slider2.min <= value <= self.slider2.max:
                self.slider2.value = value
                print(f"Slider 2 updated to: {value}")
            else:
                print("Value out of range")
        except ValueError:
            print("Invalid input for slider 2")

    def open_filechooser(self):
        layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])
        select_button = Button(text="Select Image", size_hint_y=None, height=40)
        layout.add_widget(filechooser)
        layout.add_widget(select_button)
        popup = Popup(title="Choose Image", content=layout, size_hint=(0.9, 0.9))

        def on_select(instance):
            if filechooser.selection:
                self.load_image(filechooser.selection, popup)

        select_button.bind(on_press=on_select)
        popup.open()

    def load_image(self, selection, popup):
        global curr_img, init_img
        if selection:
            curr_img = selection[0]
            init_img = selection[0]
            self.ids.image_display.source = curr_img
            self.ids.initial_image_display.source = init_img
            self.ids.image_display.reload()
            self.ids.initial_image_display.reload()
            popup.dismiss()

    def save_image(self):
        layout = BoxLayout(orientation='vertical', spacing=10)
        filechooser = FileChooserIconView()
        filename_input = TextInput(hint_text="Enter file name", size_hint_y=None, height=40)
        save_button = Button(text="Save", size_hint_y=None, height=40)

        layout.add_widget(filechooser)
        layout.add_widget(filename_input)
        layout.add_widget(save_button)
        popup = Popup(title="Save Image As", content=layout, size_hint=(0.9, 0.9))

        def on_save(instance):
            if filechooser.path and filename_input.text:
                filepath = f"{filechooser.path}/{filename_input.text}"
                self.perform_save(filepath)
                popup.dismiss()

        save_button.bind(on_press=on_save)
        popup.open()

    def perform_save(self, filepath):
        try:
            if self.image_display.source:
                from shutil import copyfile
                copyfile(self.image_display.source, filepath + '.png')
                print(f"Image saved successfully to {filepath}")
            else:
                print("No image to save!")
        except Exception as e:
            print(f"Error saving image: {e}")

class MyScreenManager(ScreenManager):
    pass

class Watercolor_Filter(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#568cbaff')
        return MyScreenManager()

if __name__ == '__main__':
    Watercolor_Filter().run()
