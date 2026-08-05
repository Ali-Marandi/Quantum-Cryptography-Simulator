import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from ..engine.protocols import BB84Protocol
from ..engine.post_processing import privacy_amplification

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quantum Cryptography Simulator - Commercial Edition")
        self.geometry("1100x700")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Q-Crypto Sim", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Protocol Selection
        self.protocol_label = ctk.CTkLabel(self.sidebar, text="Protocol:")
        self.protocol_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.protocol_menu = ctk.CTkOptionMenu(self.sidebar, values=["BB84", "B92 (Soon)", "E91 (Soon)"])
        self.protocol_menu.grid(row=2, column=0, padx=20, pady=(0, 10))

        # Parameters
        self.bits_label = ctk.CTkLabel(self.sidebar, text="Number of Bits: 100")
        self.bits_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.bits_slider = ctk.CTkSlider(self.sidebar, from_=50, to=1000, number_of_steps=19, command=self.update_bits_label)
        self.bits_slider.grid(row=4, column=0, padx=20, pady=(0, 10))
        self.bits_slider.set(100)

        self.noise_label = ctk.CTkLabel(self.sidebar, text="Channel Noise (QBER): 0%")
        self.noise_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.noise_slider = ctk.CTkSlider(self.sidebar, from_=0, to=0.5, command=self.update_noise_label)
        self.noise_slider.grid(row=6, column=0, padx=20, pady=(0, 10))
        self.noise_slider.set(0)

        self.eve_switch = ctk.CTkSwitch(self.sidebar, text="Enable Eavesdropper (Eve)")
        self.eve_switch.grid(row=7, column=0, padx=20, pady=10)

        self.eve_rate_label = ctk.CTkLabel(self.sidebar, text="Eve Interception: 50%")
        self.eve_rate_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.eve_rate_slider = ctk.CTkSlider(self.sidebar, from_=0, to=1, command=self.update_eve_label)
        self.eve_rate_slider.grid(row=9, column=0, padx=20, pady=(0, 10))
        self.eve_rate_slider.set(0.5)

        self.run_button = ctk.CTkButton(self.sidebar, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=11, column=0, padx=20, pady=20)

        # Main Content
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.tabview.add("Dashboard")
        self.tabview.add("Detailed Log")
        self.tabview.add("Security Analysis")

        # Dashboard Tab
        self.dashboard_frame = self.tabview.tab("Dashboard")
        self.dashboard_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.stat_frame = ctk.CTkFrame(self.dashboard_frame)
        self.stat_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.qber_stat = self.create_stat_widget(self.stat_frame, "Calculated QBER", "0%", 0)
        self.key_len_stat = self.create_stat_widget(self.stat_frame, "Sifted Key Length", "0", 1)
        self.eve_detect_stat = self.create_stat_widget(self.stat_frame, "Eve Detected", "No", 2)

        self.chart_frame = ctk.CTkFrame(self.dashboard_frame)
        self.chart_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.dashboard_frame.grid_rowconfigure(1, weight=1)

        # Detailed Log Tab
        self.log_text = ctk.CTkTextbox(self.tabview.tab("Detailed Log"), width=800, height=500)
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Security Analysis Tab
        self.security_frame = self.tabview.tab("Security Analysis")
        self.final_key_label = ctk.CTkLabel(self.security_frame, text="Final Secure Key (Hashed):", font=ctk.CTkFont(weight="bold"))
        self.final_key_label.pack(pady=(20, 0))
        self.final_key_display = ctk.CTkTextbox(self.security_frame, height=100)
        self.final_key_display.pack(padx=20, pady=10, fill="x")

        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_stat_widget(self, parent, label, value, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=20, pady=10)
        l = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12))
        l.pack()
        v = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        v.pack()
        return v

    def update_bits_label(self, value):
        self.bits_label.configure(text=f"Number of Bits: {int(value)}")

    def update_noise_label(self, value):
        self.noise_label.configure(text=f"Channel Noise (QBER): {int(value*100)}%")

    def update_eve_label(self, value):
        self.eve_rate_label.configure(text=f"Eve Interception: {int(value*100)}%")

    def run_simulation(self):
        n_bits = int(self.bits_slider.get())
        qber = self.noise_slider.get()
        eve_present = self.eve_switch.get()
        eve_rate = self.eve_rate_slider.get()

        protocol = BB84Protocol(n_bits=n_bits, qber=qber, eve_present=eve_present, eve_interception_rate=eve_rate)
        results = protocol.run()

        # Update Stats
        self.qber_stat.configure(text=f"{results['qber']*100:.1f}%")
        self.key_len_stat.configure(text=str(len(results['alice_sifted'])))
        
        # Eve detection logic: if QBER > threshold (e.g. 11% for BB84)
        threshold = 0.11 + qber
        eve_detected = results['qber'] > threshold
        self.eve_detect_stat.configure(text="YES" if eve_detected else "No", text_color="red" if eve_detected else "white")

        # Update Log
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", f"--- BB84 Protocol Simulation ---\n")
        self.log_text.insert("end", f"Alice's bits: {results['alice_bits'][:50]}...\n")
        self.log_text.insert("end", f"Alice's bases: {results['alice_bases'][:50]}...\n")
        self.log_text.insert("end", f"Bob's bases: {results['bob_bases'][:50]}...\n")
        self.log_text.insert("end", f"Sifted key length: {len(results['alice_sifted'])}\n")
        if eve_present:
            self.log_text.insert("end", f"Eve intercepted {results['eve_info']['interceptions']} qubits.\n")

        # Final Key
        if len(results['alice_sifted']) > 0:
            final_key = privacy_amplification(results['alice_sifted'])
            self.final_key_display.delete("1.0", "end")
            self.final_key_display.insert("end", final_key)
        else:
            self.final_key_display.delete("1.0", "end")
            self.final_key_display.insert("end", "Error: No sifted key generated.")

        # Update Chart
        self.ax.clear()
        labels = ['Alice Bits', 'Sifted Key', 'Errors']
        values = [n_bits, len(results['alice_sifted']), int(results['qber'] * len(results['sifted_indices']))]
        self.ax.bar(labels, values, color=['#3a7ebf', '#1f538d', '#e74c3c'])
        self.ax.set_title("Key Distribution Summary", color='white')
        self.canvas.draw()

if __name__ == "__main__":
    app = App()
    app.mainloop()
