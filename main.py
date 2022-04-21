from tkinter import *
window=Tk()
btn=Button(window, text="Form", fg='blue')
btn.place(x=80, y=100)
lbl=Label(window, text="Tennant Form", fg='red', font=("Helvetica", 16))
lbl.place(x=60, y=50)
txtfld=Entry(window, text="", bd=5)
txtfld.place(x=80, y=150)
window.title('Tennant Bill Pay')
window.geometry("300x200+10+10")
window.mainloop()
# Button Widget
button_submit = tkinter.Button(main_window, text="Submit", command=on_click())
button_submit.config(width=20, height=2)

button_submit.pack()
main_window.mainloop()

# /Users/zorajohnson/Gui/main.py
