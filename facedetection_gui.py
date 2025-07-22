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
from comparision_fixation_images import process_fixation_image
from detect_videos import process_all_videos
from comparision_fixation_videos import process_fixation_video
import time


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
        try:
            print("start processing")
            self.progress_bar.value=0
            if self.tabVideos_chbx_eyemovement_enable.active and self.tabVideos_chbx_video_enable.active:
                print("start processing videos")
                process_all_videos(self.tabVideos_txt_video_input.text, 
                                self.tabVideos_txt_output_path.text, 
                                "./model/shape_predictor_68_face_landmarks.dat",
                                save_raw=self.tabVideos_chbx_save_raw_enable.active, 
                                save_marked=self.tabVideos_chbx_save_marked_enable.active, 
                                max_workers=8)
                print("finish processing videos")
            ###
            self.progress_bar.value=50
            if self.tabVideos_chbx_eyemovement_enable.active and self.tabVideos_chbx_output_enable.active:
                print("start processing eyemovement data")
                process_fixation_video(self.tabVideos_txt_eyemovement_input.text, 
                                      self.tabVideos_txt_output_path.text, 
                                      videofilter='.mp4', 
                                      output_csv_path=self.tabVideos_txt_output_path.text+"/eyemovement_video_comparison.csv")
                print("finish processing eyemovement data")
            self.progress_bar.value=100
            print("finish processing")
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

    def tabImage_on_save_raw_checkbox(self):
        if self.tabImage_chbx_save_raw_enable.active:
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')


    def tabImage_on_save_marked_checkbox(self):
        if self.tabImage_chbx_save_marked_enable.active:
            print('The checkbox is active')
        else:
            print('The checkbox is inactive')

    def tabImage_run_Process(self):
        
        try:
            print("start")
            if self.tabImage_chbx_input_image_enable.active and self.tabImage_chbx_output_enable.active:
                process_images(self.tabImage_txt_input_path.text,
                                self.tabImage_txt_output_path.text,
                                "./model/shape_predictor_68_face_landmarks.dat",
                                save_marked=True)
            if self.tabImage_chbx_output_enable.active and self.tabImage_chbx_input_fixation_enable.active:
                process_fixation_image(self.tabImage_txt_input_fixation_path.text, 
                                      self.tabImage_txt_output_path.text+"/all_landmarks.csv", 
                                      'right', 
                                      output_path=self.tabImage_txt_output_path.text+"/eyemovement_image_comparison.csv")
            
            
            
        #     marked_dir = os.path.join(self.tabImage_txt_output_path.text, "Marked")
            
        #     image_files = sorted([
        #     f for f in os.listdir(marked_dir)
        #     if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        # ])
        #     if len(image_files)>0:
        #         self.tabImage_image.source=os.path.join(marked_dir, image_files[0])
           
            print ("finish")
        except Exception as e:
            print(e)








    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()


        
    def clkfunc(self):

        App.get_running_app().stop()


            
class DAOI(App):
    
    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        self.title = 'FaceTrack-AOI'
        Window.size = (1000,1000)
       
    
    def _on_file_drop(self, window, file_path):
#        print(file_path)
#        Root = Factory.Root()
        
#        print(Root.last_focused.text)
##        self.Root
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