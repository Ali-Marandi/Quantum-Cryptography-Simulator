import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
from ..engine.protocols import BB84Protocol, B92Protocol, E91Protocol, NetworkQKD
from ..engine.post_processing import privacy_amplification, cascade_error_correction, export_results_to_file
from ..engine.quantum_engine import QuantumState, QuantumNetwork

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quantum Cryptography Simulator v1.2.0 - Professional Edition")
        self.geometry("1200x800")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(15, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Q-Crypto Pro", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Protocol Selection
        self.protocol_label = ctk.CTkLabel(self.sidebar, text="Protocol:")
        self.protocol_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.protocol_menu = ctk.CTkOptionMenu(self.sidebar, values=["BB84", "B92", "E91"])
        self.protocol_menu.grid(row=2, column=0, padx=20, pady=(0, 10))

        # Parameters
        self.bits_label = ctk.CTkLabel(self.sidebar, text="Number of Bits: 100")
        self.bits_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.bits_slider = ctk.CTkSlider(self.sidebar, from_=50, to=1000, number_of_steps=19, command=self.update_bits_label)
        self.bits_slider.grid(row=4, column=0, padx=20, pady=(0, 10))
        self.bits_slider.set(100)

        self.distance_label = ctk.CTkLabel(self.sidebar, text="Fiber Distance: 0 km")
        self.distance_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.distance_slider = ctk.CTkSlider(self.sidebar, from_=0, to=100, command=self.update_distance_label)
        self.distance_slider.grid(row=6, column=0, padx=20, pady=(0, 10))
        self.distance_slider.set(0)

        self.noise_label = ctk.CTkLabel(self.sidebar, text="Base Noise (QBER): 0%")
        self.noise_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.noise_slider = ctk.CTkSlider(self.sidebar, from_=0, to=0.5, command=self.update_noise_label)
        self.noise_slider.grid(row=8, column=0, padx=20, pady=(0, 10))
        self.noise_slider.set(0)

        self.eve_switch = ctk.CTkSwitch(self.sidebar, text="Enable Eve")
        self.eve_switch.grid(row=9, column=0, padx=20, pady=10)

        self.eve_rate_label = ctk.CTkLabel(self.sidebar, text="Eve Interception: 50%")
        self.eve_rate_label.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.eve_rate_slider = ctk.CTkSlider(self.sidebar, from_=0, to=1, command=self.update_eve_label)
        self.eve_rate_slider.grid(row=11, column=0, padx=20, pady=(0, 10))
        self.eve_rate_slider.set(0.5)

        self.run_button = ctk.CTkButton(self.sidebar, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=12, column=0, padx=20, pady=10)

        self.export_button = ctk.CTkButton(self.sidebar, text="Export Results (CSV)", command=self.export_data, fg_color="green", hover_color="darkgreen")
        self.export_button.grid(row=13, column=0, padx=20, pady=10)

        # Hardware Emulation
        self.hw_label = ctk.CTkLabel(self.sidebar, text="Hardware Profile:")
        self.hw_label.grid(row=14, column=0, padx=20, pady=(10, 0))
        self.hw_menu = ctk.CTkOptionMenu(self.sidebar, values=["Standard", "ID Quantique Clavis3", "Toshiba QKD"])
        self.hw_menu.grid(row=15, column=0, padx=20, pady=(0, 10))

        # Attack Suite
        self.attack_label = ctk.CTkLabel(self.sidebar, text="Active Attack:")
        self.attack_label.grid(row=16, column=0, padx=20, pady=(10, 0))
        self.attack_menu = ctk.CTkOptionMenu(self.sidebar, values=["None", "PNS Attack", "Detector Blinding"])
        self.attack_menu.grid(row=17, column=0, padx=20, pady=(0, 10))

        # Main Content
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.tabview.add("Dashboard")
        self.tabview.add("Network Topology")
        self.tabview.add("Bloch Sphere")
        self.tabview.add("Detailed Log")
        self.tabview.add("Security Analysis")

        # Dashboard Tab
        self.dashboard_frame = self.tabview.tab("Dashboard")
        self.dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.stat_frame = ctk.CTkFrame(self.dashboard_frame)
        self.stat_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        self.qber_stat = self.create_stat_widget(self.stat_frame, "Total QBER", "0%", 0)
        self.key_len_stat = self.create_stat_widget(self.stat_frame, "Sifted Key", "0", 1)
        self.corrected_stat = self.create_stat_widget(self.stat_frame, "Corrected Key", "0", 2)
        self.sec_score_stat = self.create_stat_widget(self.stat_frame, "Security Score", "100%", 3)
        self.eve_detect_stat = self.create_stat_widget(self.stat_frame, "Eve Detected", "No", 4)

        self.chart_frame = ctk.CTkFrame(self.dashboard_frame)
        self.chart_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.dashboard_frame.grid_rowconfigure(1, weight=1)

        # Bloch Sphere Tab
        self.bloch_frame = self.tabview.tab("Bloch Sphere")
        self.fig_bloch = plt.figure(figsize=(6, 6), dpi=100)
        self.fig_bloch.patch.set_facecolor('#2b2b2b')
        self.ax_bloch = self.fig_bloch.add_subplot(111, projection='3d')
        self.canvas_bloch = FigureCanvasTkAgg(self.fig_bloch, master=self.bloch_frame)
        self.canvas_bloch.get_tk_widget().pack(fill="both", expand=True)
        self.draw_empty_bloch()

        # Network Topology Tab
        self.network_frame = self.tabview.tab("Network Topology")
        self.network_frame.grid_columnconfigure(0, weight=1)
        self.network_frame.grid_rowconfigure(1, weight=1)
        
        self.net_ctrl_frame = ctk.CTkFrame(self.network_frame)
        self.net_ctrl_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.add_node_btn = ctk.CTkButton(self.net_ctrl_frame, text="Add Repeater Node", command=self.add_repeater)
        self.add_node_btn.pack(side="left", padx=10, pady=10)
        
        self.net_info_label = ctk.CTkLabel(self.net_ctrl_frame, text="Current Nodes: Alice, Bob")
        self.net_info_label.pack(side="left", padx=20)

        self.fig_net, self.ax_net = plt.subplots(figsize=(6, 4), dpi=100)
        self.fig_net.patch.set_facecolor('#2b2b2b')
        self.ax_net.set_facecolor('#2b2b2b')
        self.canvas_net = FigureCanvasTkAgg(self.fig_net, master=self.network_frame)
        self.canvas_net.get_tk_widget().grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.network = QuantumNetwork()
        self.network.add_node("Alice")
        self.network.add_node("Bob")
        self.draw_network()

        # Detailed Log Tab
        self.log_text = ctk.CTkTextbox(self.tabview.tab("Detailed Log"), width=800, height=500)
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Security Analysis Tab
        self.security_frame = self.tabview.tab("Security Analysis")
        self.final_key_label = ctk.CTkLabel(self.security_frame, text="Final Secure Key (Hashed):", font=ctk.CTkFont(weight="bold"))
        self.final_key_label.pack(pady=(20, 0))
        self.final_key_display = ctk.CTkTextbox(self.security_frame, height=100)
        self.final_key_display.pack(padx=20, pady=10, fill="x")

        self.etsi_btn = ctk.CTkButton(self.security_frame, text="Generate ETSI GS QKD 014 Report", command=self.generate_etsi)
        self.etsi_btn.pack(pady=20)

        # Main Chart
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.last_results = None

    def create_stat_widget(self, parent, label, value, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=15, pady=10)
        l = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12))
        l.pack()
        v = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        v.pack()
        return v

    def update_bits_label(self, value):
        self.bits_label.configure(text=f"Number of Bits: {int(value)}")

    def update_distance_label(self, value):
        self.distance_label.configure(text=f"Fiber Distance: {int(value)} km")

    def update_noise_label(self, value):
        self.noise_label.configure(text=f"Base Noise (QBER): {int(value*100)}%")

    def update_eve_label(self, value):
        self.eve_rate_label.configure(text=f"Eve Interception: {int(value*100)}%")

    def add_repeater(self):
        name = f"Repeater_{len(self.network.nodes)-1}"
        self.network.add_node(name, node_type="Repeater")
        self.net_info_label.configure(text=f"Current Nodes: {', '.join(self.network.nodes.keys())}")
        self.draw_network()

    def draw_network(self):
        self.ax_net.clear()
        names = list(self.network.nodes.keys())
        x = np.linspace(0, 10, len(names))
        y = np.zeros(len(names))
        
        for i, name in enumerate(names):
            color = 'blue' if name in ['Alice', 'Bob'] else 'orange'
            self.ax_net.scatter(x[i], y[i], s=500, c=color, zorder=5)
            self.ax_net.text(x[i], y[i]+0.2, name, color='white', ha='center', fontweight='bold')
            
        if len(x) > 1:
            self.ax_net.plot(x, y, color='white', linestyle='--', alpha=0.5, zorder=1)
            
        self.ax_net.set_ylim(-1, 1)
        self.ax_net.set_axis_off()
        self.canvas_net.draw()

    def draw_empty_bloch(self):
        self.ax_bloch.clear()
        self.ax_bloch.set_facecolor('#2b2b2b')
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = np.cos(u)*np.sin(v)
        y = np.sin(u)*np.sin(v)
        z = np.cos(v)
        self.ax_bloch.plot_wireframe(x, y, z, color="white", alpha=0.1)
        self.ax_bloch.plot([0, 0], [0, 0], [-1, 1], color="white", alpha=0.5)
        self.ax_bloch.plot([0, 0], [-1, 1], [0, 0], color="white", alpha=0.5)
        self.ax_bloch.plot([-1, 1], [0, 0], [0, 0], color="white", alpha=0.5)
        self.ax_bloch.set_axis_off()
        self.canvas_bloch.draw()

    def run_simulation(self):
        n_bits = int(self.bits_slider.get())
        qber = self.noise_slider.get()
        distance = self.distance_slider.get()
        eve_present = self.eve_switch.get()
        eve_rate = self.eve_rate_slider.get()
        selected_protocol = self.protocol_menu.get()
        attack_type = self.attack_menu.get().replace(" Attack", "").replace(" ", "")
        if attack_type == "None": attack_type = None

        hw_profile = self.hw_menu.get()
        source_type = "WCP" if hw_profile != "Standard" else "SinglePhoton"
        efficiency = 0.25 if hw_profile == "ID Quantique Clavis3" else (0.35 if hw_profile == "Toshiba QKD" else 1.0)

        if len(self.network.nodes) > 2:
            # Network Mode
            net_protocol = NetworkQKD(self.network, "Alice", "Bob", protocol_type=selected_protocol, n_bits=n_bits)
            results = net_protocol.run()
            threshold = 0.20 # Higher threshold for multi-hop
        else:
            # Direct Mode
            if selected_protocol == "BB84":
                protocol = BB84Protocol(n_bits=n_bits, qber=qber, distance=distance, eve_present=eve_present, 
                                        eve_interception_rate=eve_rate, source_type=source_type, detector_efficiency=efficiency)
                threshold = 0.11 + (protocol.channel.qber - qber)
            elif selected_protocol == "B92":
                protocol = B92Protocol(n_bits=n_bits, qber=qber, distance=distance, eve_present=eve_present, eve_interception_rate=eve_rate)
                threshold = 0.05 + (protocol.channel.qber - qber)
            else:
                protocol = E91Protocol(n_bits=n_bits, qber=qber, distance=distance, eve_present=eve_present, eve_interception_rate=eve_rate)
                threshold = 0.15 + (protocol.channel.qber - qber)
            
            results = protocol.run(attack_type=attack_type)
        
        # Error Correction
        corrected_bits, final_errors = cascade_error_correction(results['alice_sifted'], results['bob_sifted'])
        results['corrected_bits'] = corrected_bits
        results['final_errors'] = final_errors
        
        self.last_results = results

        # Security Score Calculation
        sec_score = 100
        if results['qber'] > 0: sec_score -= (results['qber'] * 200)
        if attack_type == "PNS" and results['eve_info'].get('pns_leaks', 0) > 0: sec_score -= 40
        if attack_type == "DetectorBlinding": sec_score -= 60
        sec_score = max(0, min(100, sec_score))

        # Update Stats
        self.qber_stat.configure(text=f"{results['qber']*100:.1f}%")
        self.key_len_stat.configure(text=str(len(results['alice_sifted'])))
        self.corrected_stat.configure(text=str(len(corrected_bits)))
        self.sec_score_stat.configure(text=f"{int(sec_score)}%", text_color="green" if sec_score > 70 else ("orange" if sec_score > 30 else "red"))
        
        eve_detected = results['qber'] > threshold or (attack_type is not None and sec_score < 50)
        self.eve_detect_stat.configure(text="YES" if eve_detected else "No", text_color="red" if eve_detected else "white")

        # Update Log
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", f"--- {selected_protocol} v1.2.0 Simulation ---\n")
        self.log_text.insert("end", f"Channel Distance: {distance} km\n")
        self.log_text.insert("end", f"Effective QBER: {results['qber']*100:.2f}%\n")
        self.log_text.insert("end", f"Errors after Cascade: {final_errors}\n")
        self.log_text.insert("end", f"Final Key (first 20 bits): {corrected_bits[:20]}...\n")

        # Update Bloch Sphere (showing last state)
        self.draw_empty_bloch()
        # Visualize |0>, |1>, |+>, |->
        states = [QuantumState.zero(), QuantumState.one(), QuantumState.plus(), QuantumState.minus()]
        colors = ['red', 'blue', 'green', 'yellow']
        for s, c in zip(states, colors):
            x, y, z = s.get_bloch_coordinates()
            self.ax_bloch.quiver(0, 0, 0, x, y, z, color=c, length=1.0, arrow_length_ratio=0.1)

        # Final Key
        if len(corrected_bits) > 0:
            final_key = privacy_amplification(corrected_bits)
            self.final_key_display.delete("1.0", "end")
            self.final_key_display.insert("end", final_key)
        
        # Update Chart
        self.ax.clear()
        labels = ['Sifted', 'Corrected', 'Errors']
        values = [len(results['alice_sifted']), len(corrected_bits), final_errors]
        self.ax.bar(labels, values, color=['#3a7ebf', '#2ecc71', '#e74c3c'])
        self.ax.set_title(f"{selected_protocol} Performance Analysis", color='white')
        self.canvas.draw()

    def export_data(self):
        if self.last_results:
            filename = export_results_to_file(self.last_results)
            # Use simple print as CTKMessagebox might not be available in all envs
            print(f"Results exported to {filename}")
        else:
            print("Run simulation first!")

    def generate_etsi(self):
        if self.last_results:
            from ..engine.sdk import QCryptoSDK
            sdk = QCryptoSDK()
            report = sdk.generate_etsi_report(self.last_results)
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "--- ETSI GS QKD 014 COMPLIANT REPORT ---\n")
            for k, v in report.items():
                self.log_text.insert("end", f"{k.upper()}: {v}\n")
            self.tabview.set("Detailed Log")
        else:
            print("Run simulation first!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
