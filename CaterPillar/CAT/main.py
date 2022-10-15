from tkinter import *
from tkinter import ttk
import time
import cv2
import mss
import numpy
import pytesseract
import threading
from PIL import Image, ImageTk
from datetime import datetime
import pyautogui as pt

bucket_value = 0
pass_count = 0
truck_payload = 0
max_so_far = 0
pass_is_updated = False
bucket_lists = []


# To center the tkinter screen
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def store():
    global bucket_value, pass_count, truck_payload, max_so_far, pass_is_updated, bucket_lists
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print('DATE TIME:                ', dt_string)
    print('PAYLOAD TO TRUCK:         ', truck_payload)
    print('PASS COUNT:               ', pass_count)
    print('BUCKET LOAD IN EACH PASS: ', bucket_lists, end='\n\n')
    data = """          DATE TIME:                  {}\n    PAYLOAD TO TRUCK:                   {}\n            PASS COUNT:                           {}\nBUCKET LOAD IN EACH PASS:           {}\n\n""".format(
        dt_string, truck_payload, pass_count, bucket_lists)
    with open('log.txt', 'a') as log:
        log.write(data)
    bucket_value = 0
    pass_count = 0
    truck_payload = 0
    max_so_far = 0
    pass_is_updated = False
    bucket_lists = []

    payload_progress['value'] = 0
    bucket_progress['value'] = 0
    payload.set('Payload\n0')
    pass_count_string.set('Pass\n0')
    bucket_load.set('Tons\n***')


def detect():
    ss_area = {'top': 310, 'left': 680, 'width': 510, 'height': 120}
    # LOCATION OF TESSERACT EXE
    pytesseract.pytesseract.tesseract_cmd = r'F:\Tesseract\tesseract'
    previous_text = 0
    payload_capture, bucket_capture, pass_capture = 0, 0, 0
    with mss.mss() as sct:
        while True:
            im = numpy.asarray(sct.grab(ss_area))
            # TURN THE PICTURE INTO BLACK AND WHITE
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

            curr_text = pytesseract.image_to_string(im)
            # PRINT ONLY IF THE VALUE ON SCREEN CHANGES
            if previous_text != curr_text:
                print(curr_text)

                if len(curr_text.split()) >= 6:
                    try:
                        temp = float(curr_text.split()[-3])
                        temp = int(curr_text.split()[-2])
                    except:
                        continue
                    payload_capture = float(curr_text.split()[-3])
                    pass_capture = int(curr_text.split()[-2])
                    try:
                        bucket_capture = float(curr_text.split()[-1])
                    except:
                        bucket_capture = 0.0

                    #print(payload_capture, bucket_capture, pass_capture)
                previous_text = curr_text

            if payload_capture >= 20 and bucket_capture == 0.0:
                position = pt.locateOnScreen(r'store.png', confidence=0.9)
                if position is None:
                    continue
                x = position[0]
                y = position[1]
                for circle in range(1):
                    for i in range(0, 50, 10):
                        pt.moveTo(x + i, y + 50 - i, 0.15, _pause=False)
                    for i in range(0, 50, 10):
                        pt.moveTo(x + 50 + i, y + i, 0.15, _pause=False)
                    for i in range(0, 50, 10):
                        pt.moveTo(x + 100 - i, y + 50 + i, 0.15, _pause=False)
                    for i in range(0, 50, 10):
                        pt.moveTo(x + 50 - i, y + 100 - i, 0.15, _pause=False)
                    for i in range(0, 50, 10):
                        pt.moveTo(x + i, y + 50 - i, 0.15, _pause=False)
                pt.moveTo(x + 50, y + 50, 0.1)
                # time.sleep(2)
                pt.click()
                print(position)

            cv2.imshow('Image', im)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            time.sleep(1)


def on_mouse_wheel(event):
    global bucket_value, pass_count, truck_payload, var, max_so_far, pass_is_updated
    if event.delta > 0:
        var = 0
        # BAR VALUE INCREMENTS ON MOUSE WHEEL
        bucket_progress['value'] += 0.5
        payload_progress['value'] += 0.5
        # HANDLING UPPER LIMIT
        if bucket_value <= 99.5:
            if pass_is_updated == False and bucket_value == 0.0:
                pass_count += 1
                pass_is_updated = True
            bucket_value += 0.5
            truck_payload += 0.5
            if bucket_value > max_so_far:
                max_so_far = bucket_value

    else:
        bucket_progress['value'] -= 0.5
        if bucket_value == 0.5:
            truck_payload += max_so_far
            payload_progress['value'] += max_so_far
            bucket_lists.append(max_so_far)
            max_so_far = 0
            pass_is_updated = False

        if bucket_value >= 0.5:
            bucket_value -= 0.5
            truck_payload -= 0.5

    if bucket_value == 0:
        temp = "Tons\n***"
    else:
        temp = "Tons\n" + str(bucket_value)
    bucket_load.set(temp)
    temp = "Payload\n" + str(truck_payload)
    payload.set(temp)
    temp = "Pass Count\n" + str(pass_count)
    pass_count_string.set(temp)
    # time.sleep(2)


def panic():
    global pass_count, truck_payload, pass_is_updated
    print('cool')
    if len(bucket_lists) > 0:
        temp = bucket_lists.pop(-1)
        pass_count -= 1
        truck_payload -= temp
        payload_progress['value'] -= temp
        pass_is_updated = False
        bucket_progress['value'] = 0
        payload_temp_string = "Payload\n" + str(truck_payload)
        payload.set(payload_temp_string)
        pass_to_string = "Pass Count\n" + str(pass_count)
        pass_count_string.set(pass_to_string)
        bucket_load.set('Tons\n***')


# THREAD TO DETECT VALUES USING OCR
t1 = threading.Thread(target=detect)

root = Tk()
root.title('CATERPILLAR')
root.grid_columnconfigure(8, weight=1)
root.minsize(width=820, height=490)
root.geometry("820x490")
center(root)

app_icon = Image.open('icon.png')
photo = ImageTk.PhotoImage(app_icon)
root.wm_iconphoto(False, photo)

root.bind_all("<MouseWheel>", on_mouse_wheel)
root.configure(background="black")

image = Image.open("1_1.jpg")
button_1_1_image = ImageTk.PhotoImage(image)
l1 = Button(root, image=button_1_1_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("1_2.png")
button_1_2_image = ImageTk.PhotoImage(image)
l2 = Button(root, image=button_1_2_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("1_3.png")
button_1_3_image = ImageTk.PhotoImage(image)
l3 = Button(root, image=button_1_3_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("1_4.png")
button_1_4_image = ImageTk.PhotoImage(image)
l4 = Button(root, image=button_1_4_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("1_5.png")
button_1_5_image = ImageTk.PhotoImage(image)
l5 = Button(root, image=button_1_5_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

l1.grid(row=0, column=0, pady=1, padx=2)
l2.grid(row=1, column=0, pady=1, padx=2)
l3.grid(row=2, column=0, pady=1, padx=2)
l4.grid(row=3, column=0, pady=1, padx=2)
l5.grid(row=4, column=0, pady=1, padx=2)

# TRUCK LOGO
image = Image.open("payload.png")
image = image.resize((130, 50), Image.ANTIALIAS)
truck_logo = ImageTk.PhotoImage(image)
Label(root, image=truck_logo, width=130, height=75, background="black", activebackground="black").grid(row=1, column=2)

# BUCKET LOGO
image = Image.open("bucket.png")
image = image.resize((130, 50), Image.ANTIALIAS)
bucket_logo = ImageTk.PhotoImage(image)
Label(root, image=bucket_logo, width=130, height=75, background="black", activebackground="black").grid(row=1, column=5)

# PAYLOAD PROGESS
payload_progress = ttk.Progressbar(root, orient=VERTICAL, length=300, mode='determinate', max=400.0)
payload_progress.grid(row=0, rowspan=4, column=1, padx=5)

# BUCKET PROGRESS
var = IntVar()
bucket_progress = ttk.Progressbar(root, orient=VERTICAL, length=300, mode='determinate', variable=var)
bucket_progress.grid(row=0, rowspan=4, column=6, padx=5)

Label(root, text='Payload Control System', font=("Arial", 17), height=2, width=29, background="#CFCFCF").grid(row=4,
                                                                                                              column=1,
                                                                                                              columnspan=6)

# TRUCK PAYLOAD
payload = StringVar()
payload.set('Payload\n0')
my_button = Label(root, textvariable=payload, width=5, font=("Arial", 15), foreground="white", background="black")
my_button.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5)

# BUCKET WEIGHT
bucket_load = StringVar()
bucket_load.set('Tons\n***')
my_button = Label(root, textvariable=bucket_load, width=5, font=("Arial", 15), foreground="white", background="black")
my_button.grid(row=0, column=5, padx=5, pady=5, ipadx=5, ipady=5)

# PANIC BUTTON
image = Image.open("tare.png")
panic_button_image = ImageTk.PhotoImage(image)
panic_button = Button(root, image=panic_button_image, width=130, height=75, background="#BABABA",
                      activebackground="#BABABA", command=panic)
panic_button.grid(row=2, column=2, padx=10)

# POWER BUTTON
image = Image.open("power.png")
power_button_image = ImageTk.PhotoImage(image)
power_button = Button(root, image=power_button_image, width=130, height=75, background="#BABABA",
                      activebackground="#BABABA")
power_button.grid(row=3, column=2, padx=10)

# PASS COUNT
pass_count_string = StringVar()
pass_count_string.set('Pass Count\n 0')
Label(root, textvariable=pass_count_string, font=("Arial", 15), background="black", foreground="white").grid(row=0,
                                                                                                             column=3,
                                                                                                             columnspan=2)

# YELLOW TRUCK
image = Image.open("yellow_truck.png")
yellow_truck_image = ImageTk.PhotoImage(image)
yellow_truck_button = Button(root, image=yellow_truck_image, width=100, height=75, background="#BABABA",
                             activebackground="#BABABA")
yellow_truck_button.grid(row=3, column=3, padx=2)

# STOCK PILE
image = Image.open("stockpile.png")
stockpile_image = ImageTk.PhotoImage(image)
stockpile_button = Button(root, image=stockpile_image, width=100, height=75, background="#BABABA",
                          activebackground="#BABABA")
stockpile_button.grid(row=3, column=4, padx=2)

# ZERO
image = Image.open("zero.png")
zero_image = ImageTk.PhotoImage(image)
zero_button = Button(root, image=zero_image, width=130, height=75, background="#BABABA", activebackground="#BABABA")
zero_button.grid(row=2, column=5, padx=10)

# WEIGH
image = Image.open("weigh.png")
weigh_image = ImageTk.PhotoImage(image)
weigh_button = Button(root, image=weigh_image, width=130, height=75, background="#BABABA", activebackground="#BABABA")
weigh_button.grid(row=3, column=5, padx=10)

# image = Image.open("1_5.png")
# button_2_1_image = ImageTk.PhotoImage(image)
l1 = Button(root, text="Store", width=7, height=3, background="#BABABA", activebackground="#BABABA",
            font=("Arial", 11, 'bold'), command=store)

image = Image.open("1_5.png")
button_2_2_image = ImageTk.PhotoImage(image)
l2 = Button(root, image=button_2_2_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("1_5.png")
button_2_3_image = ImageTk.PhotoImage(image)
l3 = Button(root, image=button_2_3_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("2_4.png")
button_2_4_image = ImageTk.PhotoImage(image)
l4 = Button(root, image=button_2_4_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

image = Image.open("2_5.png")
button_2_5_image = ImageTk.PhotoImage(image)
l5 = Button(root, image=button_2_5_image, width=100, height=75, background="#BABABA", activebackground="#BABABA")

l1.grid(row=0, column=7, pady=5, padx=2)
l2.grid(row=1, column=7, pady=5, padx=2)
l3.grid(row=2, column=7, pady=5, padx=2)
l4.grid(row=3, column=7, pady=5, padx=2)
l5.grid(row=4, column=7, pady=5, padx=2)

t1.start()
root.mainloop()
