__author__ = 'pavan'

from Tkinter import *

#blank window
root = Tk()

#modify root window
root.title("Sentiment Analysis")
root.geometry("600x400")

#frame
topFrame = Frame(root)
midFrame = Frame(root)
botFrame = Frame(root)
topFrame.grid(row=0)
midFrame.grid(row=1)
botFrame.grid(row=2)

#label
label1 = Label(topFrame, text = "Sentiment Analysis\nGroup 7")
label1.grid(row=0, column=0)
label2 = Label(topFrame, text = "Enter your text below")
label2.grid(row=0, column=1)

#textfield
textfield = Text(midFrame, height=10)
textfield.grid(row=0, columnspan=2)

#button
button = Button(midFrame, text = "Submit")
button.grid(row=1, columnspan=2)

#sentiment output
label3 = Label(botFrame, text = "tolo")
label3.grid(row=0, columnspan=2)
root.mainloop()