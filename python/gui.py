from Tkinter import *
import ttk
import tkFont
import time
import Queue
import threading
from tdcs import TDCS_Connection


class MainTDCSWindow:

    def __init__(self):

        # Create tdcs connection
        self.tdcs = TDCS_Connection()

        # Create GUI
        root = Tk()
        root.title('Arduino TDCS')
        self.content = ttk.Frame(root)
        frame = ttk.Frame(self.content, borderwidth=5, relief="sunken", width=500, height=400)

        label_font = tkFont.Font(family="Helvetica", size=13, weight="bold")
        value_font = tkFont.Font(family="Helvetica", size=13, weight="bold")

        status_label = ttk.Label(self.content, text="Status:", font=label_font)
        current_label = ttk.Label(self.content, text="Current:", font=label_font)
        voltage_label = ttk.Label(self.content, text="Voltage:", font=label_font)
        resistance_label = ttk.Label(self.content, text="Resistance:", font=label_font)
        potentiometer_label = ttk.Label(self.content, text="Potentiometer:", font=label_font)
        target_current_label = ttk.Label(self.content, text="Target Current:", font=label_font)
        device_label = ttk.Label(self.content, text="Device:", font=label_font)

        self.status_value_label = ttk.Label(self.content, text="Disconnected!", font=value_font)
        self.current_value_label = ttk.Label(self.content, text="-", font=value_font)
        self.voltage_value_label = ttk.Label(self.content, text="-", font=value_font)
        self.resistance_value_label = ttk.Label(self.content, text="-", font=value_font)
        self.potentiometer_value_label = ttk.Label(self.content, text="-", font=value_font)
        self.target_current_entry = Entry(self.content)
        self.device_path_entry = Entry(self.content)
        self.target_current_entry.insert(0, '1')
        self.device_path_entry.insert(0, '/dev/ttyUSB0')


        self.content.grid(column=0, row=0)
        frame.grid(column=0, row=0, columnspan=3, rowspan=7)

        status_label.grid(column=0, row=0, sticky=(W), padx=10)
        current_label.grid(column=0, row=1, sticky=(W), padx=10)
        voltage_label.grid(column=0, row=2, sticky=(W), padx=10)
        resistance_label.grid(column=0, row=3, sticky=(W), padx=10)
        potentiometer_label.grid(column=0, row=4, sticky=(W), padx=10)
        target_current_label.grid(column=0, row=5, sticky=(W), padx=10)
        device_label.grid(column=0, row=6, sticky=(W), padx=10)

        self.status_value_label.grid(column=1, row=0, sticky=(W,), padx=10)
        self.current_value_label.grid(column=1, row=1, sticky=(W,), padx=10)
        self.voltage_value_label.grid(column=1, row=2, sticky=(W,), padx=10)
        self.resistance_value_label.grid(column=1, row=3, sticky=(W,), padx=10)
        self.potentiometer_value_label.grid(column=1, row=4, sticky=(W,), padx=10)
        self.target_current_entry.grid(column=1, row=5, sticky=(W,), padx=10)
        self.device_path_entry.grid(column=1, row=6, sticky=(W,), padx=10)

        connect = ttk.Button(self.content, text="Connect to device", command=self.connect_callback)
        start = ttk.Button(self.content, text="Start tDCS       ", command=self.start_call_back)
        stop = ttk.Button(self.content, text="Stop tDCS        ", command=self.stop_call_back)
        update = ttk.Button(self.content, text="Update target    ", command=self.target_callback)
        quit = ttk.Button(self.content, text="Exit             ", command=self.exit_callback)

        connect.grid(column=2, row=0, sticky=(W), padx=10)
        start.grid(column=2, row=1, sticky=(W), padx=10)
        stop.grid(column=2, row=2, sticky=(W), padx=10)
        update.grid(column=2, row=3, sticky=(W), padx=10)
        quit.grid(column=2, row=4, sticky=(W), padx=10)

        # Create a queue to run asynchronously the commands (to avoid feezing the gui)
        # TODO: Add connect to queue
        self.queue = Queue.Queue()
        self.updater_task = ThreadedTask(self.queue, self.tdcs).start()
        # Call Threaded task after 250 ms
        self.content.after(250, self.process_queue)

        # Flags that control the arduino
        self.set_current = False
        self.set_start = False
        self.set_stop = False
        self.target_current = 0

        root.mainloop()

    def process_queue(self):
        try:
            data = self.queue.get(0)
            if data['id'] == 0:  # Nothing retrieved:
                ThreadedTask(self.queue, self.tdcs).start()
            elif data['id'] == 1:  # Update
                self.current_value_label['text'] = data['current']
                self.voltage_value_label['text'] = data['voltage']
                self.resistance_value_label['text'] = data['resistance']
                self.potentiometer_value_label['text'] = data['potentiometer']

                # Check for any pending commands
                if self.set_current:
                    self.tdcs.set_target(self.target_current)
                    self.set_current = False
                if self.set_start:
                    self.tdcs.start_tdcs()
                    self.set_start = False
                if self.set_stop:
                    self.tdcs.stop_tdcs()
                    self.set_stop = False

                ThreadedTask(self.queue, self.tdcs).start()
        except Queue.Empty:
            pass
        self.content.after(250, self.process_queue)

    def target_callback(self):
        """
        Read the target current, do range checks and set the target
        :return:
        """
        try:
            self.target_current = float(self.target_current_entry.get())
        except:
            self.target_current_entry.delete(0, END)
            self.target_current_entry.insert(0,'0')
            self.target_current = 0

        if self.target_current > 5:
            self.target_current = 5
            self.target_current_entry.delete(0, END)
            self.target_current_entry.insert(0, '5')
        elif self.target_current <0:
            self.target_current = 0
            self.target_current_entry.delete(0, END)
            self.target_current_entry.insert(0, '0')
        self.set_current = True

    def start_call_back(self):
        self.set_start = True

    def stop_call_back(self):
        self.set_stop = True

    def connect_callback(self):
        port = self.device_path_entry.get()
        #port = '/dev/ttyUSB0'
        status = self.tdcs.connect(port=port)
        if status:
            self.status_value_label['text'] = 'Connected!'
            self.target_callback()
            self.device_path_entry.configure(state='disabled')
        else:
            self.status_value_label['text'] = 'Device not found!'

    def exit_callback(self):
        sys.exit(0)


class ThreadedTask(threading.Thread):
    def __init__(self, queue, tdcs):
        threading.Thread.__init__(self)
        self.queue = queue
        self.tdcs = tdcs

    def run(self):
        if not self.tdcs.is_arduino_available():
            self.queue.put({'id': 0})
        else:
            voltage, current, resistance, potentiometer = self.tdcs.get_status()
            if resistance > 1000:
                if resistance > 5000:
                    resistance = 'Inf'
                else:
                    resistance = str(resistance / 1000) + ' kOhm'
            else:
                resistance = str(resistance) + ' Ohm'

            if potentiometer > 1000:
                potentiometer = str(potentiometer / 1000) + ' kOhm'
            else:
                potentiometer = str(potentiometer) + ' Ohm'

            self.queue.put(
                {'id': 1, 'current': str(1000 * current) + ' mA', 'voltage': str(5-voltage) + ' V', 'resistance':
                    resistance, 'potentiometer': potentiometer})


if __name__ == '__main__':
    main = MainTDCSWindow()
