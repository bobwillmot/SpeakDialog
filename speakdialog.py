'''Speech Synthesis sample program'''
from Tkinter import Tk, Frame, Button, Text, END, INSERT
import sys

#sys.path.append('/Users/bobwillmot/Downloads')
import macspeechx

class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def say_it(self):
        to_say = self.text.get(1.0, END)
        v = macspeechx.GetIndVoice(3)
        while macspeechx.Busy():
            pass
        ch = v.NewChannel()
        ch.SpeakText(to_say)
        while macspeechx.Busy():
            pass

    def cleartext(self):
        self.text.delete(1.0, END)

    def createWidgets(self):
        self.text = Text(self)
        self.text.pack({"side": "top"})

        self.talk = Button(self)
        self.talk["text"] = "Speak"
        self.talk["command"] = self.say_it
        self.talk.pack({"side": "left"})

        self.clear = Button(self)
        self.clear["text"] = "Clear"
        self.clear["command"] = self.cleartext
        self.clear.pack({"side": "left"})

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "left"})

        self.text.insert(END, "enter what you want me to say here")



if __name__ == "__main__":
    root = Tk()
    root.title('Robot Voice')
    app = Application(master=root)
    app.mainloop()
    root.destroy()