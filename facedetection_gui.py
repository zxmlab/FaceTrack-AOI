from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
import os
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage

from detect_images import process_images
from detect_videos import process_all_videos
from comparison_fixation_images import process_fixation_image
from comparison_fixation_videos import process_fixation_video
import time
from threading import Thread
from kivy.clock import Clock

import os
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class LoadpathDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(TabbedPanel):     
    
    button_drop = ObjectProperty(None)
    gtposition = ObjectProperty(None)
#    mean = ObjectProperty(None)
#    std = ObjectProperty(None)

    txtplot = ObjectProperty(None)
    txt0 = ObjectProperty(None)

    last_focused = ObjectProperty(None)
    
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    imu_path = ObjectProperty(None)
    radar_odo_path = ObjectProperty(None)
    ground_truth_ext_path = ObjectProperty(None)


    def show_load_1(self):
        content = LoadDialog(load=self.load_1, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    

    def load_1(self, path, filename):
        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()
        self.imu_path.text = os.path.join(path,filename[0])

        self.dismiss_popup()

    def show_load_2(self):
        content = LoadDialog(load=self.load_2, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    

    def load_2(self, path, filename):
        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()
        self.radar_odo_path.text = os.path.join(path,filename[0])
        self.dismiss_popup()

    def show_load_3(self):
        content = LoadDialog(load=self.load_3, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_load_4(self):
        content = LoadpathDialog(load=self.load_4, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load Fusion output path", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()    

    def load_3(self, path, filename):
        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()
        self.ground_truth_ext_path.text = os.path.join(path,filename[0])

        self.dismiss_popup()

    def load_4(self, path):
        # with open(os.path.join(path, filename[0])) as stream:
        #     self.text_input.text = stream.read()
        self.txtMCplot.text = os.path.join(path)

        self.dismiss_popup()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def pressed_tabVideos(self):
#        print(value)
        try:
            self.last_focused.text = 'click, then drag and drop'
            self.last_focused = self.tabVideos_txt_eyemovement_input
            self.last_focused.text = 'drag and drop here'
                
#                print(self.last_focused.text)
        except Exception as e:
            print(e)  


    def tabVideos_on_eyemovement_checkbox(self):
        if self.tabVideos_chbx_eyemovement_enable.active:
             self.tabVideos_txt_eyemovement_input.disabled=False
             print('The checkbox is active')
        else:
            print('The checkbox is inactive')           
            self.tabVideos_txt_eyemovement_input.disabled=True

    def tabVideos_on_focus_txt_eyemovement_input(self):
#        print(value)
        try:
            if self.tabVideos_txt_eyemovement_input.focus:
#                print('Focused GT')
#                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabVideos_txt_eyemovement_input
#                self.last_focused.text = 'drag and drop here'
                
#                print(self.last_focused.text)
        except Exception as e:
            print(e)
            
    def tabVideos_on_video_checkbox(self):
        if self.tabVideos_chbx_video_enable.active:
             self.tabVideos_txt_video_input.disabled=False
             print('The checkbox is active')
        else:
            print('The checkbox is inactive')           
            self.tabVideos_txt_video_input.disabled=True  

    def tabVideos_on_focus_txt_video_input(self):
#        print(value)
        try:
            if self.tabVideos_txt_video_input.focus:
#                print('Focused GT')
#                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabVideos_txt_video_input
#                self.last_focused.text = 'drag and drop here'
                
#                print(self.last_focused.text)
        except Exception as e:
            print(e)

    def tabVideos_on_output_checkbox(self):
        if self.tabVideos_chbx_output_enable.active:
            self.tabVideos_txt_output_path.disabled = False
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')
            self.tabVideos_txt_output_path.disabled = True

    def tabVideos_on_focus_output(self):
        #        print(value)
        try:
            if self.tabVideos_txt_output_path.focus:
                #                print('Focused GT')
                #                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabVideos_txt_output_path
        #                self.last_focused.text = 'drag and drop here'

        #                print(self.last_focused.text)
        except Exception as e:
            print(e)
    def tabVideos_on_save_raw_checkbox(self):
        if self.tabVideos_chbx_save_raw_enable.active:
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')


    def tabVideos_on_save_marked_checkbox(self):
        if self.tabVideos_chbx_save_marked_enable.active:
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')


    def tabVideos_run_Process(self):
        #        print(value)
        self.tabVideos_Button_Process_and_Save.disabled=True
        Thread(target=self.long_task).start()

    def long_task(self):
        # 耗时操作
        try:
            self.tabVideos_label.text="Processing started"
            if self.tabVideos_chbx_eyemovement_enable.active and self.tabVideos_chbx_video_enable.active:
                print("start processing videos")
                self.tabVideos_label.text="Processing video started"
                process_all_videos(self.tabVideos_txt_video_input.text, 
                                self.tabVideos_txt_output_path.text, 
                                "./model/shape_predictor_68_face_landmarks.dat",
                                save_raw=self.tabVideos_chbx_save_raw_enable.active, 
                                save_marked=self.tabVideos_chbx_save_marked_enable.active
                                )
                print("finish processing videos")
                self.tabVideos_label.text="processing"
            ###
            if self.tabVideos_chbx_eyemovement_enable.active and self.tabVideos_chbx_output_enable.active:
                print("start processing eyemovement data")
                self.tabVideos_label.text=" Processing eyemovement data"
                process_fixation_video(self.tabVideos_txt_eyemovement_input.text, 
                                      self.tabVideos_txt_output_path.text, 
                                      video_filter='.mp4', 
                                      output_path=self.tabVideos_txt_output_path.text+"/eyemovement_video_comparison.csv")
                print("finish processing eyemovement data")
                self.tabVideos_label.text="finish processing eyemovement data"
            self.tabVideos_Button_Process_and_Save.disabled=False
            print("Finished!")
            self.tabVideos_label.text="finish processing"
        except Exception as e:
            print(e)
        



    def tabImage_pressed_tabImage(self):
        #        print(value)
        try:
            self.last_focused.text = 'click, then drag and drop'
            self.last_focused = self.tabImage_txt_input_image_path
            self.last_focused.text = 'drag and drop here'

            print(self.last_focused.text)
        except Exception as e:
            print(e)


    def tabImage_on_input_image_checkbox(self):
        if self.tabImage_chbx_input_image_enable.active:
            self.tabImage_txt_input_image_path.disabled = False
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')
            self.tabImage_txt_input_image_path.disabled = True

    def tabImage_on_focus_input_image(self):
        #        print(value)
        try:
            if self.tabImage_txt_input_image_path.focus:
                #                print('Focused GT')
                #                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabImage_txt_input_image_path
        #                self.last_focused.text = 'drag and drop here'

        #                print(self.last_focused.text)
        except Exception as e:
            print(e)

    def tabImage_on_image_column_checkbox(self):
        if self.tabImage_chbx_image_column_enable.active:
            self.tabImage_txt_image_column.disabled = False
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')
            self.tabImage_txt_image_column.disabled = True

    def tabImage_on_focus_image_column(self):
        #        print(value)
        try:
            if self.tabImage_txt_image_column.focus:
                #                print('Focused GT')
                #                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabImage_txt_image_column
        #                self.last_focused.text = 'drag and drop here'

        #                print(self.last_focused.text)
        except Exception as e:
            print(e)

    def tabImage_on_input_fixation_checkbox(self):
        if self.tabImage_chbx_input_fixation_enable.active:
            self.tabImage_txt_input_fixation_path.disabled = False
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')
            self.tabImage_txt_input_fixation_path.disabled = True

    def tabImage_on_focus_input_fixation(self):
        #        print(value)
        try:
            if self.tabImage_txt_input_fixation_path.focus:
                #                print('Focused GT')
                #                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabImage_txt_input_fixation_path
        #                self.last_focused.text = 'drag and drop here'

        #                print(self.last_focused.text)
        except Exception as e:
            print(e)

    def tabImage_on_output_checkbox(self):
        if self.tabImage_chbx_output_enable.active:
            self.tabImage_txt_output_path.disabled = False
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')
            self.tabImage_txt_output_path.disabled = True

    def tabImage_on_focus_output(self):
        #        print(value)
        try:
            if self.tabImage_txt_output_path.focus:
                #                print('Focused GT')
                #                self.last_focused.text = 'click, then drag and drop'
                self.last_focused = self.tabImage_txt_output_path
        #                self.last_focused.text = 'drag and drop here'

        #                print(self.last_focused.text)
        except Exception as e:
            print(e)




    def tabImage_on_save_marked_checkbox(self):
        if self.tabImage_chbx_save_marked_enable.active:
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')

    def tabImage_run_Process(self):
            print("start")
            self.tabImage_label.text="Processing started"
            self.tabImage_Button_Process_and_Save.disabled=True
            Thread(target=self.image_long_task).start()

    def image_long_task(self):
        try:
            if self.tabImage_chbx_input_image_enable.active and self.tabImage_chbx_output_enable.active:
                self.tabImage_label.text="processing image data"
                process_images(self.tabImage_txt_input_image_path.text,
                                self.tabImage_txt_output_path.text,
                                "./model/shape_predictor_68_face_landmarks.dat",
                                save_marked=True)
            
            if self.tabImage_chbx_output_enable.active and self.tabImage_chbx_input_fixation_enable.active:
                self.tabImage_label.text="processing fixation data"
                process_fixation_image(self.tabImage_txt_input_fixation_path.text, 
                                      self.tabImage_txt_output_path.text+"/landmarks.csv", 
                                      self.tabImage_txt_image_column.text, 
                                      output_path=self.tabImage_txt_output_path.text+"/eyemovement_image_comparison.csv")
            self.tabImage_Button_Process_and_Save.disabled=False
            
            
        #     marked_dir = os.path.join(self.tabImage_txt_output_path.text, "Marked")
            
        #     image_files = sorted([
        #     f for f in os.listdir(marked_dir)
        #     if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        # ])
        #     if len(image_files)>0:
        #         self.tabImage_image.source=os.path.join(marked_dir, image_files[0])
           
            print ("Finish!")
            self.tabImage_label.text="Finish!"
        except Exception as e:
            print(e)





    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()


        
    def clkfunc(self):

        App.get_running_app().stop()


            
class DAOI(App):
    image1_path = StringProperty('')
    image2_path = StringProperty('')
    video1_path = StringProperty('')
    video2_path = StringProperty('')
    
    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        self.title = 'FaceTrack-AOI'
        Window.size = (600, 600)
        
        base = os.path.dirname(os.path.abspath(__file__))
        image1 = os.path.join(base, 'gui', 'images', 'M2H_frame65.jpg')
        image2 = os.path.join(base, 'gui', 'images', 'M2H_frame65_output.jpg')
        video1 = os.path.join(base, 'gui', 'videos', 'M2H_1min.mp4')
        video2 = os.path.join(base, 'gui', 'videos', 'M2H_1min_withlandmark.mp4')

        self.image1_path = image1
        self.image2_path = image2
        self.video1_path = video1
        self.video2_path = video2

        return Builder.load_file("daoi.kv")
       
    
    def _on_file_drop(self, window, file_path):
#        print(file_path)
#        Root = Factory.Root()
        
#        print(Root.last_focused.text)
#        self.Root
        try:
#            print(dir(self))
#            print(dir(self.root))
#            print file_path
            # layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
            # img1 = Image(source='/home/midea/Documents/private/copy/Images/M1H_frame1.jpg', allow_stretch=True)
            # tabImage_txt_run_plots.add_widget(img1)
            self.root.last_focused.text = file_path
        except Exception as e:
            print(e)
        return


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
Factory.register('LoadpathDialog', cls=LoadpathDialog)

if __name__ == '__main__':
    DAOI().run()
