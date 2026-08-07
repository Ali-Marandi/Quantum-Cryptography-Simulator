import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
from ..engine.protocols import BB84Protocol, B92Protocol, E91Protocol, NetworkQKD
from ..engine.post_processing import privacy_amplification, cascade_error_correction, export_results_to_file
from ..engine.quantum_engine import QuantumState, QuantumNetwork
from ..engine.ai_security import AISecurity
from ..engine.database import QCryptoDB

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

        # UX / EdTech
        self.ux_label = ctk.CTkLabel(self.sidebar, text="Learning Mode:")
        self.ux_label.grid(row=18, column=0, padx=20, pady=(10, 0))
        self.tutorial_switch = ctk.CTkSwitch(self.sidebar, text="Interactive Tutorial", command=self.toggle_tutorial)
        self.tutorial_switch.grid(row=19, column=0, padx=20, pady=10)

        # Satellite Mode
        self.sat_label = ctk.CTkLabel(self.sidebar, text="Channel Type:")
        self.sat_label.grid(row=20, column=0, padx=20, pady=(10, 0))
        self.channel_menu = ctk.CTkOptionMenu(self.sidebar, values=["Fiber", "Satellite"])
        self.channel_menu.grid(row=21, column=0, padx=20, pady=(0, 10))

        # Main Content
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.tabview.add("Dashboard")
        self.tabview.add("Network Topology")
        self.tabview.add("Bloch Sphere")
        self.tabview.add("Interactive Lab")
        self.tabview.add("AI Security")
        self.tabview.add("Quantum Messenger")
        self.tabview.add("City Network View")
        self.tabview.add("VR Explorer 3D")
        self.tabview.add("Simulation History")
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
        
        self.ai_engine = AISecurity()
        self.db = QCryptoDB()

        # Interactive Lab Tab
        self.lab_frame = self.tabview.tab("Interactive Lab")
        self.lab_label = ctk.CTkLabel(self.lab_frame, text="Welcome to the Quantum Lab! Enable Tutorial to start.", font=ctk.CTkFont(size=16))
        self.lab_label.pack(pady=20)
        
        self.lab_progress = ctk.CTkProgressBar(self.lab_frame, width=400)
        self.lab_progress.pack(pady=20)
        self.lab_progress.set(0)
        
        self.lab_step_btn = ctk.CTkButton(self.lab_frame, text="Next Step", command=self.next_lab_step, state="disabled")
        self.lab_step_btn.pack(pady=10)
        
        self.lab_step = 0

        # AI Security Tab
        self.ai_frame = self.tabview.tab("AI Security")
        self.ai_label = ctk.CTkLabel(self.ai_frame, text="AI Eavesdropping Detection System", font=ctk.CTkFont(size=18, weight="bold"))
        self.ai_label.pack(pady=20)
        
        self.ai_status_box = ctk.CTkFrame(self.ai_frame, fg_color="#333333")
        self.ai_status_box.pack(padx=20, pady=20, fill="x")
        
        self.ai_status_label = ctk.CTkLabel(self.ai_status_box, text="System Status: MONITORING", font=ctk.CTkFont(size=14))
        self.ai_status_label.pack(pady=10)
        
        self.ai_result_label = ctk.CTkLabel(self.ai_status_box, text="Anomaly Detection: WAITING...", font=ctk.CTkFont(size=20, weight="bold"))
        self.ai_result_label.pack(pady=20)
        
        self.ai_opt_label = ctk.CTkLabel(self.ai_frame, text="AI Optimization Suggestion: -")
        self.ai_opt_label.pack(pady=10)

        # Quantum Messenger Tab
        self.chat_frame = self.tabview.tab("Quantum Messenger")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkTextbox(self.chat_frame, width=800, height=400)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.chat_input_frame = ctk.CTkFrame(self.chat_frame)
        self.chat_input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.chat_entry = ctk.CTkEntry(self.chat_input_frame, placeholder_text="Type your message here...", width=600)
        self.chat_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.send_btn = ctk.CTkButton(self.chat_input_frame, text="Encrypt & Send", command=self.send_message)
        self.send_btn.pack(side="right", padx=10, pady=10)
        
        self.current_key = None

        # City Network View Tab
        self.city_frame = self.tabview.tab("City Network View")
        self.city_frame.grid_columnconfigure(0, weight=1)
        self.city_frame.grid_rowconfigure(0, weight=1)
        
        self.fig_city, self.ax_city = plt.subplots(figsize=(6, 4), dpi=100)
        self.fig_city.patch.set_facecolor('#1a1a1a')
        self.ax_city.set_facecolor('#1a1a1a')
        self.canvas_city = FigureCanvasTkAgg(self.fig_city, master=self.city_frame)
        self.canvas_city.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.draw_city_network()

        # VR Explorer 3D Tab
        self.vr_frame = self.tabview.tab("VR Explorer 3D")
        self.vr_frame.grid_columnconfigure(0, weight=1)
        self.vr_frame.grid_rowconfigure(1, weight=1)
        
        self.vr_ctrl_frame = ctk.CTkFrame(self.vr_frame)
        self.vr_ctrl_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.vr_rand_btn = ctk.CTkButton(self.vr_ctrl_frame, text="Generate Random 3D Universe", command=self.randomize_vr)
        self.vr_rand_btn.pack(side="left", padx=10, pady=10)
        
        self.vr_fly_btn = ctk.CTkButton(self.vr_ctrl_frame, text="Start VR Fly-through", command=self.toggle_vr_fly)
        self.vr_fly_btn.pack(side="left", padx=10, pady=10)
        
        self.vr_label = ctk.CTkLabel(self.vr_ctrl_frame, text="Interactive 3D Mode: Use mouse to rotate and zoom")
        self.vr_label.pack(side="left", padx=20)
        
        self.is_flying = False
        self.fly_angle = 0

        self.fig_vr = plt.subplots(figsize=(8, 6), dpi=100, subplot_kw={'projection': '3d'})[0]
        self.fig_vr.patch.set_facecolor('#0a0a0a')
        self.ax_vr = self.fig_vr.axes[0]
        self.ax_vr.set_facecolor('#0a0a0a')
        self.canvas_vr = FigureCanvasTkAgg(self.fig_vr, master=self.vr_frame)
        self.canvas_vr.get_tk_widget().grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.draw_vr_universe()

        # Simulation History Tab
        self.history_frame = self.tabview.tab("Simulation History")
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(0, weight=1)
        
        self.history_display = ctk.CTkTextbox(self.history_frame, width=800, height=500)
        self.history_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.refresh_history_btn = ctk.CTkButton(self.history_frame, text="Refresh History", command=self.refresh_history)
        self.refresh_history_btn.grid(row=1, column=0, padx=10, pady=10)

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

        channel_type = self.channel_menu.get()

        if len(self.network.nodes) > 2:
            # Network Mode
            net_protocol = NetworkQKD(self.network, "Alice", "Bob", protocol_type=selected_protocol, n_bits=n_bits)
            results = net_protocol.run()
            threshold = 0.20 # Higher threshold for multi-hop
        else:
            # Direct Mode
            if selected_protocol == "BB84":
                protocol = BB84Protocol(n_bits=n_bits, qber=qber, distance=distance, eve_present=eve_present, 
                                        eve_interception_rate=eve_rate, source_type=source_type, 
                                        detector_efficiency=efficiency, channel_type=channel_type)
                threshold = 0.11 + (protocol.qber if channel_type == "Fiber" else 0.05)
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
        
        # Update current key for messenger
        if len(corrected_bits) > 0:
            self.current_key = "".join(map(str, corrected_bits))
            self.chat_display.insert("end", f"--- NEW SECURE KEY GENERATED ({len(corrected_bits)} bits) ---\n")

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
        
        # AI Detection
        key_rate = len(results['alice_sifted']) / n_bits
        variance = np.var(results['alice_sifted']) if results['alice_sifted'] else 0
        ai_anomaly = self.ai_engine.detect_eavesdropping(results['qber'], key_rate, variance)
        
        self.ai_result_label.configure(
            text="ANOMALY DETECTED!" if ai_anomaly else "NORMAL OPERATION",
            text_color="red" if ai_anomaly else "green"
        )
        
        opt_mu = self.ai_engine.optimize_parameters(distance)
        self.ai_opt_label.configure(text=f"AI Optimization Suggestion: Set Mean Photon Number (mu) to {opt_mu}")

        eve_detected = results['qber'] > threshold or ai_anomaly or (attack_type is not None and sec_score < 50)
        self.eve_detect_stat.configure(text="YES" if eve_detected else "No", text_color="red" if eve_detected else "white")
        
        # Save to Database
        self.db.save_simulation(selected_protocol, results['qber'], len(corrected_bits), int(sec_score), eve_detected)

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

    def next_lab_step(self):
        steps = [
            "Step 1: Alice is generating random bits and choosing bases...",
            "Step 2: Qubits are being transmitted through the quantum channel...",
            "Step 3: Bob is measuring the received qubits...",
            "Step 4: Alice and Bob are comparing bases (Sifting)...",
            "Step 5: Error correction and Privacy Amplification complete!"
        ]
        if self.lab_step < len(steps):
            self.lab_label.configure(text=steps[self.lab_step])
            self.lab_progress.set((self.lab_step + 1) / len(steps))
            self.lab_step += 1
        else:
            self.lab_label.configure(text="Experiment Complete! Check Dashboard for results.")
            self.run_simulation()
            self.lab_step = 0

    def toggle_tutorial(self):
        if self.tutorial_switch.get():
            self.lab_step_btn.configure(state="normal")
            self.tabview.set("Interactive Lab")
        else:
            self.lab_step_btn.configure(state="disabled")

    def send_message(self):
        msg = self.chat_entry.get()
        if not msg: return
        if not self.current_key:
            self.chat_display.insert("end", "ERROR: No secure key available. Run simulation first!\n")
            return
            
        # Simplified XOR encryption for demonstration
        encrypted = "".join([chr(ord(c) ^ int(self.current_key[i % len(self.current_key)])) for i, c in enumerate(msg)])
        decrypted = "".join([chr(ord(c) ^ int(self.current_key[i % len(self.current_key)])) for i, c in enumerate(encrypted)])
        
        self.chat_display.insert("end", f"Alice (Original): {msg}\n")
        self.chat_display.insert("end", f"Channel (Encrypted): {encrypted.encode('utf-8').hex()}\n")
        self.chat_display.insert("end", f"Bob (Decrypted): {decrypted}\n\n")
        self.chat_entry.delete(0, "end")
        self.chat_display.see("end")

    def refresh_history(self):
        history = self.db.get_history()
        self.history_display.delete("1.0", "end")
        self.history_display.insert("end", f"{'Date':<20} | {'Proto':<6} | {'QBER':<6} | {'Key':<4} | {'Score':<5} | {'Eve'}\n")
        self.history_display.insert("end", "-"*65 + "\n")
        for row in history:
            ts, proto, qber, klen, score, eve = row[1], row[2], row[3], row[4], row[5], row[6]
            self.history_display.insert("end", f"{ts[:19]:<20} | {proto:<6} | {qber*100:>5.1f}% | {klen:>4} | {score:>4}% | {'YES' if eve else 'No'}\n")

    def draw_city_network(self):
        self.ax_city.clear()
        for i in range(0, 10, 2):
            self.ax_city.axhline(i, color='#333333', lw=1, zorder=1)
            self.ax_city.axvline(i, color='#333333', lw=1, zorder=1)
        locations = {"Data Center (Alice)": (1, 8), "Repeater 1": (5, 5), "Repeater 2": (2, 3), "Government Office (Bob)": (8, 2)}
        for name, pos in locations.items():
            color = '#3a7ebf' if "Alice" in name or "Bob" in name else '#f39c12'
            self.ax_city.scatter(pos[0], pos[1], s=300, c=color, edgecolors='white', zorder=5)
            self.ax_city.text(pos[0], pos[1]+0.3, name, color='white', ha='center', fontsize=8)
        self.ax_city.plot([1, 5], [8, 5], color='#2ecc71', lw=2, alpha=0.6, zorder=2)
        self.ax_city.plot([5, 8], [5, 2], color='#2ecc71', lw=2, alpha=0.6, zorder=2)
        self.ax_city.set_xlim(0, 10); self.ax_city.set_ylim(0, 10)
        self.ax_city.set_title("Metropolitan Quantum Key Distribution Network", color='white', pad=20)
        self.ax_city.set_axis_off()
        self.canvas_city.draw()

    def randomize_vr(self):
        self.network = QuantumNetwork()
        self.network.add_node("Alice", pos=(0, 0, 0))
        self.network.add_node("Bob", pos=(10, 10, 10))
        for i in range(5):
            self.network.add_node(f"Repeater_{i}")
        for i in range(2):
            self.network.add_node(f"Sat_{i}", node_type="Satellite", pos=(np.random.uniform(0, 10), np.random.uniform(0, 10), 20))
        self.draw_vr_universe()

    def draw_vr_universe(self):
        self.ax_vr.clear()
        self.ax_vr.set_facecolor('#0a0a0a')
        self.ax_vr.grid(False)
        self.ax_vr.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        self.ax_vr.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        self.ax_vr.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        self.ax_vr.set_xticks([]); self.ax_vr.set_yticks([]); self.ax_vr.set_zticks([])
        
        for name, node in self.network.nodes.items():
            x, y, z = node.pos
            color = '#00ffff' if node.node_type == "EndNode" else ('#ff00ff' if node.node_type == "Satellite" else '#00ff00')
            self.ax_vr.scatter([x], [y], [z], s=200, c=color, edgecolors='white', depthshade=True)
            self.ax_vr.text(x, y, z+1, name, color='white', fontsize=7, ha='center')
            
        # Draw connections as glowing lines
        nodes = list(self.network.nodes.values())
        for i in range(len(nodes)-1):
            p1, p2 = nodes[i].pos, nodes[i+1].pos
            self.ax_vr.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='#00ffff', alpha=0.3, lw=1)
            
        self.ax_vr.set_title("Quantum VR Universe Explorer", color='white', fontsize=14)
        self.canvas_vr.draw()

    def toggle_vr_fly(self):
        self.is_flying = not self.is_flying
        if self.is_flying:
            self.vr_fly_btn.configure(text="Stop VR Fly-through", fg_color="red")
            self.animate_vr()
        else:
            self.vr_fly_btn.configure(text="Start VR Fly-through", fg_color=["#3a7ebf", "#1f538d"])

    def animate_vr(self):
        if self.is_flying:
            self.fly_angle = (self.fly_angle + 2) % 360
            self.ax_vr.view_init(elev=20, azim=self.fly_angle)
            self.canvas_vr.draw_idle()
            self.after(50, self.animate_vr)

if __name__ == "__main__":
    app = App()
    app.mainloop()
