from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.slider import Slider
from kivy.core.window import Window  # Import Window to change background color
from kivy.utils import get_color_from_hex  # Import utility to convert hex to RGBA

# Load the UI.kv file
Builder.load_file('UI.kv')

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
    color_picker = ObjectProperty(None)

    def on_button_click(self, instance):
        print(f"{instance.text} button clicked!")

    def on_slider1_release(self, instance):
        print(f"Range value: {int(instance.value)}")

    def on_slider2_release(self, instance):
        print(f"Color Blend Strength value: {int(instance.value)}")

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
        if selection:
            self.image_display.source = selection[0]
            self.image_display.reload()
            popup.dismiss()

    def on_color(self, instance, value):
        print(f"Selected color (RGBA): {value}")
        # Implement any additional functionality with the selected color here

class MyScreenManager(ScreenManager):
    pass

class Watercolor_Filter(App):
    def build(self):
        # Set the initial background color to #568cbaff
        Window.clearcolor = get_color_from_hex('#568cbaff')
        return MyScreenManager()

if __name__ == '__main__':
    Watercolor_Filter().run()
