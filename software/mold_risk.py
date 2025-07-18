# mold_risk.py

import math
import csv
import os
from datetime import datetime


CSV_FILE = "mold_log.csv" 

# -------- Dew Point Calculation --------
def dew_point(temp_c, rh):
    a = 17.27
    b = 237.7
    alpha = (a * temp_c) / (b + temp_c) + math.log(rh / 100.0)
    return (b * alpha) / (a - alpha)


# -------- Mold Risk Prediction --------
def check_mold_risk(int_temp, int_rh, ext_temp, ext_rh):
    int_dp = dew_point(int_temp, int_rh)
    ext_dp = dew_point(ext_temp, ext_rh)
    mold_risk_level = {
        "High Humidity (RH > 60%)": int_rh > 75,
        "Dew Point Gap (Indoor DP - Outdoor DP > 3°C)": (int_dp - ext_dp) > 3,
        "Condensation Risk (Indoor Temp ≤ DP)": int_temp <= int_dp
    }

    passed = sum(mold_risk_level.values())

    if passed == 3:
        risk = "HIGH"
    elif passed == 2:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # mqtt_callback(f"[Mold Risk] Level: {risk}")
    return risk, passed


# -------- CSV Logger --------
def log_to_csv(timestamp, data):  # 
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Internal Temp (C)", "Internal RH (%)", "Internal DP (C)",
                "External Temp (C)", "External RH (%)", "External DP (C)", "Mold Risk"
            ])
        writer.writerow([timestamp] + data)

