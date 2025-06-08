# Smart Library Environment Monitoring System

An IoT-based intelligent system designed to monitor indoor environmental conditions and regulate fan, lighting, and notification systems to prevent mold formation and maintain a comfortable, quiet, and energy-efficient library atmosphere.

---

## Objective

To monitor indoor environmental conditions and automatically regulate **ventilation**, **lighting**, and **alerts** to prevent **mold formation** and ensure an optimal atmosphere in the library.

---

## Features

- **Smart Lighting**: Adjusts LED brightness based on ambient light.
- **Climate Control**: Activates fan based on indoor temperature and humidity.
- **Noise Monitoring**: Detects noise levels and alerts visually via LED/OLED.
- **Occupancy Detection**: Tracks presence using a PIR sensor.
- **Weather-Based Mold Risk**: Uses Weather API to estimate mold risk and sends notifications.
- **Visualization Dashboard**: View real-time and historical sensor data (coming soon).
- **AI Planning**: Optional future integration to manage device actions based on long-term goals.

---

## Hardware Components

| Component                  | Description                              |
|---------------------------|------------------------------------------|
| Grove Light Sensor        | Detect ambient light for smart lighting  |
| Grove RGB LED             | Adjust brightness based on LDR input     |
| Grove Temperature Sensor  | Measure indoor temperature               |
| Grove Sound Sensor        | Monitor environmental noise              |
| Grove PIR Motion Sensor   | Detect occupancy                         |
| Grove LCD/OLED Display    | Display sound levels, status messages    |
| Fan (via relay module)    | Activated for cooling                    |
| Notification System       | Alerts based on mold risk/weather        |

---

## Software Sensors (Derived)

- **Mold Risk Score** – based on weather + indoor humidity

---

##  External APIs

- **OpenWeatherMap API**  
  Used to fetch external temperature and humidity data for mold risk assessment.


