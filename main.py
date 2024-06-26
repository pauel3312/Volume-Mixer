from pycaw.pycaw import AudioUtilities, AudioSession
from functools import partial
import tkinter as tk
from typing import Optional, Any, Callable

window: tk.Tk = tk.Tk()
window.title("Volume mixer")
window.iconbitmap("VMIcon_1.ico")

popup_x_offset = 1000
popup_y_offset = 200

labels: list[tk.Label] = []
volumes: list[Any] = []
volume_labels: list[tk.Label] = []
volume_label_stringVars = []
sliders: list[tk.Scale] = []
saved_sessions: int = 0


def get_saved_sessions() -> int:
    c = 0
    for session in AudioUtilities.GetAllSessions():
        if session.Process:
            c += 1
    return c


def init_lists() -> None:
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
    return 'break'


def change_volume(volume, volume_label_string, new_volume):
    volume.SetMasterVolume(int(new_volume)/100, None)
    volume_label_string.set(f"volume : {int(volume.GetMasterVolume() * 100)}%")
    window.update()


def add_volume_slider(session: AudioSession) -> None:
    if session.Process:
        current_label: tk.Label = tk.Label(window, text=session.Process.name().strip(".exe"))
        current_volume = session.SimpleAudioVolume
        current_volume_label_stringVar: tk.StringVar = tk.StringVar()
        current_volume_label_stringVar.set(f"volume :{int(current_volume.GetMasterVolume() * 100)}%")
        current_volume_label: tk.Label = tk.Label(window, textvariable=current_volume_label_stringVar)
        current_volume_function: Callable = lambda x: change_volume(current_volume, current_volume_label_stringVar, x)
        current_slider: tk.Scale = tk.Scale(window, from_=100, to=0, command=current_volume_function)
        current_slider.set(int(current_volume.GetMasterVolume() * 100))

        labels.append(current_label)
        volumes.append(current_volume)
        volume_labels.append(current_volume_label)
        sliders.append(current_slider)

        current_label.grid(column=labels.index(current_label), row=0)
        current_volume_label.grid(column=volume_labels.index(current_volume_label), row=1)
        current_slider.grid(column=sliders.index(current_slider), row=2)

        current_slider.bind("<Button-2>", partial(change_volume_with_popup, current_volume,
                                                  current_volume_label_stringVar, current_slider))
        current_slider.bind("<Button-3>", partial(change_volume_with_popup, current_volume,
                                                  current_volume_label_stringVar, current_slider))


def init_sliders() -> None:
    sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
    init_lists()
    for widget in window.winfo_children():
        widget.destroy()
    for session in sessions:
        add_volume_slider(session)
    window.update()


def start_popup() -> int:
    while True:
        popup: PopupEntry = PopupEntry(window)
        window.wait_window(popup.top)
        value: str | int = popup.value
        if value.isdigit():
            value = int(value)
            if value in range(0, 101):
                del popup
                return value


class PopupEntry(tk.Frame):
    def __init__(self, master: tk.Tk = None):
        super().__init__(master)

        self.top: tk.Toplevel = tk.Toplevel(master)
        self.top.geometry(f"+{popup_x_offset}+{popup_y_offset}")
        self.label: tk.Label = tk.Label(self.top, text="enter percentage")
        self.label.pack()
        self.entry: tk.Entry = tk.Entry(self.top)
        self.entry.pack()
        self.button: tk.Button = tk.Button(self.top, text='Ok', command=self.cleanup)
        self.button.pack()
        self.value: Optional[str] = None

    def cleanup(self):
        self.value = self.entry.get()
        self.top.destroy()


def check_sessions() -> None:
    global saved_sessions
    if saved_sessions != get_saved_sessions():
        saved_sessions = get_saved_sessions()
        init_sliders()
    window.after(1000, check_sessions)


if __name__ == "__main__":
    check_sessions()
    window.mainloop()
