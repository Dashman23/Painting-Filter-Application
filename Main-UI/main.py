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
import PaintingLogic

# Load the UI.kv file
Builder.load_file('UI.kv')

curr_img = r'Default.JPG'
init_img = r'Default.JPG'

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

    def on_button_click(self, instance):
        print(f"{instance.text} button clicked!")

    def update_slider_min_length(self, text):
        try:
            value = int(text)
            if 1 <= value <= 5:
                self.ids.slider_min_length.value = value
                print(f"Minimum line length set to {value} (waiting for Apply Filter)")
            else:
                print(f"Value {value} is out of range (1-5).")
        except ValueError:
            print("Invalid input for minimum line length")

    def update_slider_max_length(self, text):
        try:
            value = int(text)
            if 1 <= value <= 5:
                self.ids.slider_max_length.value = value
                print(f"Maximum line length set to {value} (waiting for Apply Filter)")
            else:
                print(f"Value {value} is out of range (1-5).")
        except ValueError:
            print("Invalid input for maximum line length")

    def update_slider_allowed_error(self, text):
        try:
            value = int(text)
            if 1 <= value <= 75:
                self.ids.slider_allowed_error.value = value
                print(f"Allowed error set to {value} (waiting for Apply Filter)")
            else:
                print(f"Value {value} is out of range (1-75).")
        except ValueError:
            print("Invalid input for allowed error")

    def update_slider_opacity(self, text):
        try:
            value = float(text)
            if 0.5 <= value <= 1.0:
                # Snap to nearest 0.1
                rounded_value = round(value * 10) / 10.0
                self.ids.slider_opacity.value = rounded_value
                self.ids.slider_opacity_input.text = "{:.1f}".format(rounded_value)
                print(f"Brushstroke opacity set to {rounded_value} (waiting for Apply Filter)")
            else:
                print("Value out of range (0.5-1.0)")
        except ValueError:
            print("Invalid input for brushstroke opacity")

    def apply_filter(self):
        global init_img
        if init_img != -1 and isinstance(init_img, str):
            try:
                min_length = int(self.ids.slider_min_length.value)
                max_length = int(self.ids.slider_max_length.value)
                allowed_error = int(self.ids.slider_allowed_error.value)
                opacity = float(self.ids.slider_opacity.value)
                output_path = r'Temp-Pictures\FinalImage.png'

                print(f"Applying filter with parameters:")
                print(f"  Minimum line length: {min_length}")
                print(f"  Maximum line length: {max_length}")
                print(f"  Allowed Error: {allowed_error}")
                print(f"  Brushstroke opacity: {opacity}")

                # Run your dithering logic here, for example:
                PaintingLogic.apply_filter(init_img, output_path, min_length, max_length, allowed_error, opacity)
                self.image_display.source = output_path
                self.image_display.reload()
                print("Filter applied successfully!")
            except Exception as e:
                print(f"Error applying filter: {e}")
        else:
            print("No valid image selected.")
       # init_img = output_path
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

class Painting_Filter(App):
    def build(self):
        Window.size = (1200, 800)
        Window.clearcolor = get_color_from_hex('#568cbaff')
        return MyScreenManager()

if __name__ == '__main__':
    Painting_Filter().run()