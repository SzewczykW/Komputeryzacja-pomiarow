import csv
import random
import time
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from simple_pid import PID
from threading import Thread, Event
from tkinter import ttk


def read_hall_sensor():
    return random.uniform(0, 5)


def read_voltage():
    return 30


def read_current():
    return random.uniform(0, 2)


class MagneticFieldControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrola pola magnetycznego")
        self.stop_event = Event()

        # Dane do wykresów
        self.time = []
        self.voltage_data = []
        self.current_data = []
        self.field_data = []
        self.start_time = time.time()

        # Kontroler PID
        self.pid = PID(1.0, 0.0, 0.0, setpoint=1.0)  # Początkowe wartości PID
        self.pid.output_limits = (0, 5)  # Ograniczenia wyjścia prądu

        # Konfiguracja PID
        self.create_pid_inputs()

        # Konfiguracja napięcia i prądu
        self.create_voltage_current_inputs()

        # Wyświetlanie bieżących wartości z czujników
        self.create_sensor_labels()

        # Układ wykresów (obok siebie, wypełniający ekran)
        self.create_graph_layout()

        # Przyciski do sterowania start/stop
        self.create_control_buttons()

        # Przyciski do zapisu danych
        self.create_save_button()

    def create_pid_inputs(self):
        frame = ttk.LabelFrame(self.root, text="Konfiguracja PID")
        frame.pack(pady=10)

        ttk.Label(frame, text="Kp:").grid(row=0, column=0, padx=5, pady=5)
        self.kp_entry = ttk.Entry(frame, width=10)
        self.kp_entry.insert(0, "1.0")
        self.kp_entry.grid(row=0, column=1)

        ttk.Label(frame, text="Ki:").grid(row=1, column=0, padx=5, pady=5)
        self.ki_entry = ttk.Entry(frame, width=10)
        self.ki_entry.insert(0, "0.0")
        self.ki_entry.grid(row=1, column=1)

        ttk.Label(frame, text="Kd:").grid(row=2, column=0, padx=5, pady=5)
        self.kd_entry = ttk.Entry(frame, width=10)
        self.kd_entry.insert(0, "0.0")
        self.kd_entry.grid(row=2, column=1)

        ttk.Label(frame, text="Wartość zadana pola magnetycznego (T):").grid(
            row=3, column=0, padx=5, pady=5
        )
        self.setpoint_entry = ttk.Entry(frame, width=10)
        self.setpoint_entry.insert(0, "1.0")
        self.setpoint_entry.grid(row=3, column=1)

        update_btn = ttk.Button(frame, text="Aktualizuj PID", command=self.update_pid)
        update_btn.grid(row=4, column=0, columnspan=2, pady=5)

    def create_voltage_current_inputs(self):
        frame = ttk.LabelFrame(self.root, text="Ustawienia napięcia i prądu")
        frame.pack(pady=10)

        ttk.Label(frame, text="Napięcie (V):").grid(row=0, column=0, padx=5, pady=5)
        self.voltage_entry = ttk.Entry(frame, width=10)
        self.voltage_entry.insert(0, "30.0")
        self.voltage_entry.grid(row=0, column=1)

        ttk.Label(frame, text="Prąd (A):").grid(row=1, column=0, padx=5, pady=5)
        self.current_entry = ttk.Entry(frame, width=10)
        self.current_entry.insert(0, "2.0")
        self.current_entry.grid(row=1, column=1)

    def create_sensor_labels(self):
        self.voltage_label = ttk.Label(
            self.root, text="Napięcie: 0.0 V", font=("Arial", 12)
        )
        self.voltage_label.pack(pady=5)

        self.current_label = ttk.Label(
            self.root, text="Prąd: 0.0 A", font=("Arial", 12)
        )
        self.current_label.pack(pady=5)

        self.field_label = ttk.Label(
            self.root, text="Pole magnetyczne: 0.0 T", font=("Arial", 12)
        )
        self.field_label.pack(pady=5)

    def create_graph_layout(self):
        graph_frame = ttk.Frame(self.root)
        graph_frame.pack(fill="both", expand=True)

        graph_frame.columnconfigure(0, weight=1)
        graph_frame.columnconfigure(1, weight=1)
        graph_frame.columnconfigure(2, weight=1)
        graph_frame.rowconfigure(0, weight=1)

        voltage_fig = Figure(figsize=(4, 3), dpi=100)
        self.ax_voltage = voltage_fig.add_subplot(111)
        self.ax_voltage.set_title("Napięcie (V)")
        self.ax_voltage.set_xlabel("Czas (s)")
        self.ax_voltage.set_ylabel("Napięcie")
        self.ax_voltage.grid(True)
        (self.voltage_line,) = self.ax_voltage.plot(
            [], [], color="blue", label="Napięcie"
        )
        voltage_canvas = FigureCanvasTkAgg(voltage_fig, graph_frame)
        voltage_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        current_fig = Figure(figsize=(4, 3), dpi=100)
        self.ax_current = current_fig.add_subplot(111)
        self.ax_current.set_title("Prąd (A)")
        self.ax_current.set_xlabel("Czas (s)")
        self.ax_current.set_ylabel("Prąd")
        self.ax_current.grid(True)
        (self.current_line,) = self.ax_current.plot([], [], color="green", label="Prąd")
        current_canvas = FigureCanvasTkAgg(current_fig, graph_frame)
        current_canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

        field_fig = Figure(figsize=(4, 3), dpi=100)
        self.ax_field = field_fig.add_subplot(111)
        self.ax_field.set_title("Pole magnetyczne (T)")
        self.ax_field.set_xlabel("Czas (s)")
        self.ax_field.set_ylabel("Pole (T)")
        self.ax_field.grid(True)
        (self.field_line,) = self.ax_field.plot([], [], color="red", label="Pole")
        field_canvas = FigureCanvasTkAgg(field_fig, graph_frame)
        field_canvas.get_tk_widget().grid(row=0, column=2, sticky="nsew")

    def create_control_buttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        self.start_button = ttk.Button(frame, text="Start", command=self.start_loop)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(frame, text="Stop", command=self.stop_loop)
        self.stop_button.grid(row=0, column=1, padx=5)

    def create_save_button(self):
        save_button = ttk.Button(
            self.root, text="Zapisz dane", command=self.save_to_file
        )
        save_button.pack(pady=5)

    def save_to_file(self):
        filename = "dane_pomiarowe.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Czas (s)", "Napięcie (V)", "Prąd (A)", "Pole magnetyczne (T)"]
            )
            for t, v, c, f in zip(
                self.time, self.voltage_data, self.current_data, self.field_data
            ):
                writer.writerow([t, v, c, f])
        print(f"Dane zapisano do pliku {filename}")

    def update_pid(self):
        try:
            kp = float(self.kp_entry.get())
            ki = float(self.ki_entry.get())
            kd = float(self.kd_entry.get())
            setpoint = float(self.setpoint_entry.get())

            self.pid.tunings = (kp, ki, kd)
            self.pid.setpoint = setpoint

        except ValueError:
            print("Nieprawidłowe wartości wejściowe PID.")

    def start_loop(self):
        self.stop_event.clear()
        self.thread = Thread(target=self.run_loop, daemon=True)
        self.thread.start()

    def stop_loop(self):
        self.stop_event.set()

    def run_loop(self):
        while not self.stop_event.is_set():
            current_time = time.time() - self.start_time

            voltage = read_voltage()
            current = read_current()
            magnetic_field = read_hall_sensor()

            control_current = self.pid(magnetic_field)

            self.voltage_label.config(text=f"Napięcie: {voltage:.2f} V")
            self.current_label.config(text=f"Prąd: {control_current:.2f} A")
            self.field_label.config(text=f"Pole magnetyczne: {magnetic_field:.2f} T")

            self.time.append(current_time)
            self.voltage_data.append(voltage)
            self.current_data.append(control_current)
            self.field_data.append(magnetic_field)

            if len(self.time) > 100:
                self.time = self.time[-100:]
                self.voltage_data = self.voltage_data[-100:]
                self.current_data = self.current_data[-100:]
                self.field_data = self.field_data[-100:]

            self.voltage_line.set_data(self.time, self.voltage_data)
            self.ax_voltage.relim()
            self.ax_voltage.autoscale_view()

            self.current_line.set_data(self.time, self.current_data)
            self.ax_current.relim()
            self.ax_current.autoscale_view()

            self.field_line.set_data(self.time, self.field_data)
            self.ax_field.relim()
            self.ax_field.autoscale_view()

            self.ax_voltage.figure.canvas.draw()
            self.ax_current.figure.canvas.draw()
            self.ax_field.figure.canvas.draw()

            time.sleep(0.1)


if __name__ == "__main__":
    root = tk.Tk()
    app = MagneticFieldControlGUI(root)
    root.mainloop()
