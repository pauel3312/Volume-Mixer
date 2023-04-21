from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from functools import partial
import tkinter as tk

window = tk.Tk()
window.title("Volume mixer")
window.iconbitmap("VMIcon_1.ico")

labels = []
volumes = []
volume_labels = []
volume_label_stringVars = []
sliders = []
saved_sessions = 0


def get_saved_sessions():
    c = 0
    for session in AudioUtilities.GetAllSessions():
        if session.Process:
            c += 1
    return c


def init_lists():
    global labels, volumes, volume_labels, volume_label_stringVars, sliders
    labels = []
    volumes = []
    volume_labels = []
    volume_label_stringVars = []
    sliders = []


def change_volume_with_popup(volume, volume_label_string, volume_slider, *args):
    new_volume = start_popup()
    volume.SetMasterVolume(int(new_volume)/100, None)
    volume_label_string.set(f"volume : {int(volume.GetMasterVolume() * 100)}%")
    volume_slider.set(new_volume)
    window.update()


def change_volume(volume, volume_label_string, new_volume):
    volume.SetMasterVolume(int(new_volume)/100, None)
    volume_label_string.set(f"volume : {int(volume.GetMasterVolume() * 100)}%")
    window.update()


def add_volume_slider(session):
    if session.Process:
        current_label = tk.Label(window, text=session.Process.name().strip(".exe"))
        current_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume_label_stringVar = tk.StringVar()
        current_volume_label_stringVar.set(f"volume :{int(current_volume.GetMasterVolume() * 100)}%")
        current_volume_label = tk.Label(window, textvariable=current_volume_label_stringVar)
        current_volume_function = lambda x: change_volume(current_volume, current_volume_label_stringVar, x)
        current_slider = tk.Scale(window, from_=100, to=0, command=current_volume_function)
        current_slider.set(int(current_volume.GetMasterVolume() * 100))

        labels.append(current_label)
        volumes.append(current_volume)
        volume_labels.append(current_volume_label)
        sliders.append(current_slider)

        current_label.grid(column=labels.index(current_label), row=0)
        current_volume_label.grid(column=volume_labels.index(current_volume_label), row=1)
        current_slider.grid(column=sliders.index(current_slider), row=2)

        current_label.bind("<Button-2>", partial(change_volume_with_popup, current_volume,
                                                 current_volume_label_stringVar, current_slider))
        current_label.bind("<Button-3>", partial(change_volume_with_popup, current_volume,
                                                 current_volume_label_stringVar, current_slider))


def init_sliders():
    sessions = AudioUtilities.GetAllSessions()
    init_lists()
    for widget in window.winfo_children():
        widget.destroy()
    for session in sessions:
        add_volume_slider(session)
    window.update()


def start_popup():
    while True:
        popup = PopupEntry(window)
        window.wait_window(popup.top)
        value = popup.value
        if value.isdigit():
            value = int(value)
            if value in range(0, 101):
                del popup
                return value


class PopupEntry(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.top = tk.Toplevel(master)
        self.top.geometry("+2900+200")
        self.label = tk.Label(self.top, text="enter percentage")
        self.label.pack()
        self.entry = tk.Entry(self.top)
        self.entry.pack()
        self.button = tk.Button(self.top, text='Ok', command=self.cleanup)
        self.button.pack()

    def cleanup(self):
        self.value = self.entry.get()
        self.top.destroy()


def check_sessions():
    global saved_sessions
    if saved_sessions != get_saved_sessions():
        saved_sessions = get_saved_sessions()
        init_sliders()
    window.after(1000, check_sessions)


if __name__ == "__main__":
    check_sessions()
    window.mainloop()
