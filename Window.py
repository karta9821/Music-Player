import tkinter as tk
from pygame import mixer
from mutagen.mp3 import MP3
from tkinter import filedialog
from tkinter import messagebox
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Window(tk.Frame):

    def __init__(self, master):
        super(Window, self).__init__(master)
        self.master = master
        self.master.title('Music Player')
        self.master.geometry('800x400')
        self.master.resizable(width=False, height=False)
        self.master.configure(bg='#fff5eb')  # (255, 245, 235)
        self.master.iconphoto(False, tk.PhotoImage(file='images/icon.png'))

        self.list_box = ListBox(self.master)
        self.menu = Menu(self.master, self.list_box)

        self.total_time = Label(self.master, relx=0.7, rely=0.25)
        self.set_volume = Label(self.master, relx=0.74, rely=0.75)
        self.actual_playing = Label(self.master, relx=0.7, rely=0.15)

        self.total_time.set_text('Total Time :  --=--')
        self.set_volume.set_text('Set Volume')
        self.actual_playing.set_text('Actual playing: -------')

        self.music = Music()

        self.add_button = Buttons(self.master, text='+ Add', relax=0.12, rely=0.6, command=self.list_box.add_song)
        self.remove_button = Buttons(self.master, text='- Del', relax=0.22, rely=0.6,
                                     command=lambda: self.list_box.delete_song(self.music, self.total_time,
                                                                               self.actual_playing))
        self.set_queue = Buttons(self.master, text='Save queue!', relax=0.35, rely=0.22, command=self.list_box.save)
        self.read = Buttons(self.master, text='Read from txt', relax=0.35, rely=0.32, command=self.list_box.read)
        self.rewind_button = Buttons(self.master, image='images/rewind_button.png',
                                     command=self.music.rewind, relax=0.7, rely=0.55)
        self.mute_button = Buttons(self.master, image='images/mute_button.png', relax=0.8, rely=0.55,
                                   command=lambda: self.scale.mute(self.mute_button, self.music))
        self.play_button = Buttons(self.master, image='images/play_button.png', relax=0.7,
                                   rely=0.45, command=lambda: self.music.play(self.list_box, self.total_time,
                                                                              self.actual_playing))
        self.stop_button = Buttons(self.master, image='images/pause_button.png', relax=0.8,
                                   rely=0.45, command=self.music.stop)

        self.scale = Scale(self.master, relx=0.71, rely=0.65, command=self.music.update)


class Buttons(tk.Button):
    def __init__(self, master, relax, rely, text=None, image=None, command=None):
        if image:
            self.photo = tk.PhotoImage(file=image)
            super(Buttons, self).__init__(master, image=self.photo, bd=0, command=command)
        else:
            super(Buttons, self).__init__(master, text=text, command=command)
        self.place(relx=relax, rely=rely)
        self.state = True
        self.last_lvl = 0


class ListBox(tk.Listbox):
    def __init__(self, master):
        super(ListBox, self).__init__(master)
        self.place(relx=0.07, rely=0.1, relwidth=0.25)
        self.bind('<<ListboxSelect>>', self.selected_song)
        self.song_dic = {}

    def add_song(self):
        ftypes = [('MP3 songs', '*.mp3'), ('WAV songs', '*.wav')]
        song_path = tk.filedialog.askopenfilename(initialdir=ROOT_DIR+'/musics',
                                                  title='Select a song', filetypes=ftypes)
        song_name = song_path.split('/')[-1]
        if song_name not in self.song_dic:
            self.insert('end', song_name)
            self.song_dic[song_name] = song_path
        else:
            tk.messagebox.showinfo('Info', 'This song is in list')

    def delete_song(self, music, label_time, label_act):
        try:
            if self.get(self.curselection()) == music.file_name:
                music.file_name = ''
                music.last_song_name = ''
                mixer.music.stop()
                label_act.set_text('Actual playing :  --=--')
                label_time.set_text('Total Time :  --=--')

            self.song_dic.pop(self.get(self.curselection()))
            self.delete(self.curselection())
            self.re_update()

        except Exception:
            pass

    def selected_song(self, event):
        try:
            return self.get(self.curselection()), self.song_dic[self.get(self.curselection())]
        except Exception:
            pass

    def save(self):
        f = open('songs.txt', 'w')
        for song_name, song_path in self.song_dic.items():
            f.writelines(song_name+":-:"+song_path+'\n')
        f.close()

    def read(self):
        f = open('songs.txt', 'r')
        for line in f.readlines():
            song_name, song_path = line.split(':-:')
            if song_name not in self.song_dic:
                self.insert('end', song_name)
                self.song_dic[song_name] = song_path.replace('\n', '')
        self.re_update()
        f.close()

    def re_update(self):
        self.delete(0, 'end')
        for k in self.song_dic.keys():
            self.insert('end', k)


class Menu(tk.Menu):
    def __init__(self, master, listbox):
        super(Menu, self).__init__(master, tearoff=0)
        self.add_command(label='Add', command=listbox.add_song)
        self.add_command(label='Save', command=listbox.save)
        self.add_command(label='Help', command=lambda: tk.messagebox.showinfo('Help',
                             'Here you can listen your favorite music and save that for later :)'))
        self.add_command(label='Info', command=lambda: tk.messagebox.showinfo('Info', "It's music player :)"))
        self.master = master
        self.master.config(menu=self)


class Label(tk.Label):
    def __init__(self, master, relx, rely):
        self.text = tk.StringVar()
        super(Label, self).__init__(master, textvariable=self.text, bg='#fff5eb')
        self.place(relx=relx, rely=rely)

    def set_text(self, text):
        self.text.set(text)


class Scale(tk.Scale):
    def __init__(self, master, relx, rely, command):
        self.var = tk.IntVar()
        super(Scale, self).__init__(master, variable=self.var, command=command, orient='horizontal', bg='#fff5eb', bd=0)
        self.place(relx=relx, rely=rely)
        self.set(50)

    def mute(self, button, music):
        if button.state:
            button.last_lvl = self.get()
            self.set(0)
            button.state = False
            music.mute_()

        else:
            self.set(button.last_lvl)
            button.state = True
            music.unmute(button.last_lvl)
            mixer.music.set_volume(button.last_lvl / 100)


class Music(object):
    def __init__(self):
        mixer.init()
        self.is_paused = False
        self.path = ''
        self.file_name = '',
        self.length = 0
        self.last_song_name = ''

    def get_length(self):
        if self.file_name.endswith('mp3'):
            self.length = int(MP3(self.path).info.length)
        else:
            self.length = int(mixer.Sound(self.path).get_length())

    def set_length(self, label):
        m, s = divmod(self.length, 60)
        label.set_text('Total Time :  {:02d}:{:02d}'.format(m, s))

    def play(self, listbox, label_time, label_actual):
        try:
            self.file_name, self.path = listbox.selected_song(0)
            if self.is_paused and self.file_name == self.last_song_name:
                    mixer.music.unpause()
                    self.is_paused = False
            else:
                if not self.last_song_name == self.file_name:
                    self.get_length()
                    self.set_length(label_time)
                    label_actual.set_text(f'Actual playing: {self.file_name}')
                    self.last_song_name = self.file_name
                    mixer.music.load(self.path)
                    mixer.music.play()
                    self.is_paused = False
        except Exception:
            tk.messagebox.showinfo(title='Info', message='Choose a song to play')

    def stop(self):
        mixer.music.pause()
        self.is_paused = True

    @staticmethod
    def mute_():
        mixer.music.set_volume(0)

    @staticmethod
    def unmute(value):
        mixer.music.set_volume(value / 100)

    @staticmethod
    def update(val):
        mixer.music.set_volume(int(val)/100)

    @staticmethod
    def rewind():
        mixer.music.rewind()


