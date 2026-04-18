# SensiFoot

![Application Overview](https://github.com/user-attachments/assets/22327372-9a6a-437f-8c81-19b6faab3a6c)

## Overview

SensiFoot is a high-fidelity biomedical diagnostic interface and hardware simulator designed to process mathematically accurate Force Sensing Resistor (FSR) telemetry. Moving beyond a basic algorithmic prototype, it simulates complex plantar pressure arrays to provide real-time biomechanical diagnostics. 

The application evaluates critical clinical metrics including Center of Pressure (CoP) tracking, dynamic Gait Phase analysis, and Localized Ulcer Risk alarms. Wrapped in a commercial-grade, human-factors-compliant "Clinical Dark Mode" UI, it serves as a robust platform for testing and visualizing prosthetic alignments and podiatric data before physical hardware integration.

---

## Key Features

### Interactive Anatomical Mesh (The 6-Array)

![Choose Sensor View](https://github.com/user-attachments/assets/5c9dec33-f72e-4f79-a02a-02136446c74f)

* **Precise Zoning**: The foot widget utilizes geometrically precise, irregular polygon tessellations mapped to six distinct anatomical zones: Heel, Midfoot Lateral, Metatarsals I/III/V, and the Hallux (Big Toe).
* **Tiered Interaction**: Features a strict Z-index hierarchy preventing visual clipping, allowing users to select and isolate specific anatomical nodes for detailed analysis. 

### Physics & Telemetry Simulation

![Manual Value Setting](https://github.com/user-attachments/assets/00102f40-f05c-4d1e-8aad-77dce7784d04)

* **Real-Time FSR Pipeline**: Simulates raw hardware input (0.00V to 3.30V) via a master control slider. The backend dynamically calculates the entire physical pipeline: Voltage Output $\rightarrow$ Sensor Resistance $\rightarrow$ Conductance $\rightarrow$ Applied Force (Newtons).
* **Dynamic Magnitude Scaling**: Automatically handles engineering SI prefixes (e.g., kΩ, MΩ, µS, kN) for highly readable, 2-decimal precision metrics in the telemetry HUD.

### Clinical Diagnostic Scenarios

![Heel Strike Scenario](https://github.com/user-attachments/assets/ba7b6ff4-00d8-4cb5-92f0-d6521ecbbf85)
![Mid-Stance Scenario](https://github.com/user-attachments/assets/9082a87c-9bca-422b-82cc-1d0e7b1eb040)
![Heel-Off Scenario](https://github.com/user-attachments/assets/6d79e7a5-51e5-4477-a962-c89fdea86009)

* **Biomechanical Gait Phase HUD**: Evaluates force distribution across the foot to dynamically output current gait states in real-time, including `HEEL STRIKE`, `MID-STANCE`, and `TOE-OFF` (which can be tested via the automated Scenario buttons).
* **Center of Pressure (CoP) Tracker**: Visually tracks the exact focal point of patient balance via a mathematically calculated weighted average of force across the active spatial centroids.
* **Localized Ulcer Risk Alarm**: Continuously listens for critical pressure thresholds (>85N). If exceeded, the system triggers a flashing red visual alert and warning banner to indicate necessary prosthetic adjustment.

---

## System Architecture

* **Framework**: Built on a strict Python backend utilizing `PyQt5` for the cross-platform commercial-grade UI.
* **Backend Core**: 
  * `state.py`: Handles the purely mathematical FSR pipeline and sensor state.
  * `clinical.py` & `diagnostics.py`: Drives the algorithmic evaluation for gait phases and lean diagnostics.
* **Frontend UI**: Modular widget architecture featuring custom painting (`QPainter`) for complex polygon rendering and telemetry layouts aligned with Gestalt principles.
* **Dependencies**: Relies on `numpy` for data handling and `opencv-python` for legacy heatmap integrations.

---

## Installation & Setup Guide

**Prerequisites**

* Python 3.8 or higher
* Git

**Steps**

1. **Clone the Repository**

    ```bash
    git clone [https://github.com/YourUsername/SensiFoot.git](https://github.com/YourUsername/SensiFoot.git)
    cd SensiFoot
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure you have `PyQt5>=5.15`, `numpy>=1.24`, and `opencv-python>=4.8` installed).*

3. **Run the Application**

    ```bash
    python main.py
    ```
    *(Note: The application is configured to launch in Full Screen mode. Exiting via the in-app "Exit" button will automatically run a teardown script to clean up `__pycache__` directories).*

---

## Usage Guide

1. **Manual Testing**: Launch the application. Click on any anatomical zone on the central foot wireframe (e.g., the Heel). Use the bottom master slider to simulate applied voltage and watch the Real-Time FSR telemetry translate this into applied Force.
2. **Scenario Simulation**: Use the right-side Action Menu to toggle between pre-configured clinical states: `Scenario: Heel Strike`, `Scenario: Mid-Stance`, and `Scenario: Heel-Off` to observe how the Gait Phase HUD and CoP tracker respond automatically.
3. **Safety Monitoring**: Manually slide a single sensor's input to its maximum threshold to trigger and observe the Localized Ulcer Risk Alarm.
4. **Display Toggles**: Click "Show Sensors" in the Action Menu to overlay the specific mathematical centroid coordinates used for CoP calculations.

---

## Contributors

<div>
    <table align="center">
        <tr>
            <td align="center">
                <a href="https://github.com/YassienTawfikk" target="_blank">
                    <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="150px;"
                         alt="Yassien Tawfik"/>
                    <br/>
                    <sub><b>Yassien Tawfik</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/Seiftaha" target="_blank">
                    <img src="https://avatars.githubusercontent.com/u/127027353?v=4" width="150px;" alt="Seif Taha"/>
                    <br/>
                    <sub><b>Seif Taha</b></sub>
                </a>
            </td>         
            <td align="center">
                <a href="https://github.com/Mazenmarwan023" target="_blank">
                    <img src="https://avatars.githubusercontent.com/u/127551364?v=4" width="150px;" alt="Mazen Marwan"/>
                    <br/>
                    <sub><b>Mazen Marwan</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/mohamedddyasserr" target="_blank">
                    <img src="https://avatars.githubusercontent.com/u/126451832?v=4" width="150px;"
                         alt="Mohamed Yasser"/>
                    <br/>
                    <sub><b>Mohamed Yasser</b></sub>
                </a>
            </td>
              </td>
           <td align="center">
              <a href="https://github.com/yousseftaha167" target="_blank">
                <img src="https://avatars.githubusercontent.com/u/128304243?v=4" width="150px;" alt="Youssef Taha"/>
                <br/>
                <sub><b>Youssef Taha</b></sub>
              </a>
            </td>
        </tr>
    </table>
</div>
