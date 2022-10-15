from tkinter import *
from tkinter import ttk
import time
import cv2
import mss
import numpy
import pytesseract
import threading

value=0
def step(event):
    global value
    if event.delta>0:
        my_progress['value'] += 10
        if value<=90: value+=10
    else:
        my_progress['value'] -= 10
        if value>=10: value-=10
    text.set(value)

def tes():
    mon = {'top': 500, 'left': 100, 'width': 150, 'height': 130}
    pytesseract.pytesseract.tesseract_cmd = r'F:\Tesseract\tesseract'
    changed_value=0
    with mss.mss() as sct:
        while True:
            im = numpy.asarray(sct.grab(mon))
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

            text = pytesseract.image_to_string(im)
            #changed_value = text
            if changed_value != text:
                print(text)
                changed_value=text

            cv2.imshow('Image', im)

            # Press "q" to quit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

            # One screenshot per second
            time.sleep(1)

t1 = threading.Thread(target=tes)
t1.start()
root=Tk()
root.title('Progress bar')

w = 400 # width for the Tk root
h = 650 # height for the Tk root
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))


c = Canvas(root)
c.bind_all("<MouseWheel>",step)

my_progress  = ttk.Progressbar(c,orient=VERTICAL,length=400,mode='determinate')
my_progress.pack(padx=20,pady=20)

text = StringVar()
text.set('NULL')
my_button=Label(c,textvariable=text,width=5,font=("Arial", 25))
my_button.pack(pady=20)

c.pack()
root.mainloop()
t1.join()

