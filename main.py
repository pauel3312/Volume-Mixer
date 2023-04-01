from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import tkinter as tk

window = tk.Tk()
window.title("Volume mixer")
window.iconbitmap("VMIcon_1.ico")

labels = []
volumes = []
volume_labels = []
volume_label_stringVars = []
sliders = []
saved_sessions = AudioUtilities.GetAllSessions()


def init_lists():
    global labels, volumes, volume_labels, volume_label_stringVars, sliders
    labels = []
    volumes = []
    volume_labels = []
    volume_label_stringVars = []
    sliders = []


def change_volume(volume, volume_label_string, new_volume):
    volume.SetMasterVolume(int(new_volume)/100, None)
    volume_label_string.set(f"volume : {int(volume.GetMasterVolume() * 100)}%")
    window.update()


def add_volume_slider(session):
    if session.Process:
        current_label = tk.Label(window, text=session.Process.name().strip(".exe"))
        current_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume_label_stringVar = tk.StringVar()
        current_volume_label_stringVar.set(f"volume : {int(current_volume.GetMasterVolume() * 100)}%")
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


def init_sliders():
    global saved_sessions
    sessions = AudioUtilities.GetAllSessions()
    saved_sessions = sessions
    init_lists()
    for widget in window.winfo_children():
        widget.destroy()
    for session in sessions:
        add_volume_slider(session)
    window.update()


def check_sessions():
    if saved_sessions != AudioUtilities.GetAllSessions():
        init_sliders()
    window.after(1000, check_sessions)


if __name__ == "__main__":
    check_sessions()
    window.mainloop()
