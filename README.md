# 🕵️‍♂️ CyberCop OSINT Framework

A powerful, multi-threaded Open Source Intelligence (OSINT) tool written in Python. It enumerates a given Indian mobile number across various platforms to extract digital footprints, real names, network locations, and active social profiles.

## 🔥 Features
* **Multi-Threaded Execution**: Scans multiple platforms simultaneously for blazing-fast results.
* **WAF Evasion**: Uses Playwright (Headless Chrome) & Custom Headers to bypass strict Web Application Firewalls (e.g., AWS WAF, Cloudflare).
* **Platform Support**:
    * 🛍️ **Flipkart**: Checks active shopping accounts.
    * 🍔 **Swiggy**: Validates active food delivery accounts via JS injection.
    * 🐦 **Twitter (X)**: Validates account existence via CSRF token manipulation.
    * 📱 **Telegram**: Extracts True Name, Username, ID, and Last Seen status using Telethon.
    * 📶 **Cellular Intelligence**: Offline resolution of Telecom Operator and State/Circle (No APIs required).
* **Hacker-Style CLI**: Beautiful, color-coded terminal tree-output.

## 🛠️ Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/CyberCop.git](https://github.com/YOUR_USERNAME/CyberCop.git)
cd CyberCop

Requirements - Telegram Developer API_ID API_HASH (Add in CYBERCOP_OSINT.py Line no. 145-146)
