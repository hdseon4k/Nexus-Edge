# 📊 Project Status: Nexus-Edge (Feasibility Study Phase)

Current Project Phase: **Feasibility Study (타당성 검토)**
Last Updated: 2026-10-20

## 🎯 Current Objectives
- **Technology Evaluation:** Verify if YOLOv11 + OpenCV/ZBar ensemble provides the required 99.9% reliability.
- **Integration Feasibility:** Test if Godot 3D (Simulation) can be synchronized with real-world ESP32 (PLC) data and Vision AI results.
- **ERP Connectivity:** Confirm seamless data flow to Odoo ERP via XML-RPC.
- **Edge Node Migration:** Transition from Termux prototype to high-performance Android Native (NDK/C++20/OpenCV) daemon on S24 Ultra.

## 🛠 Technology Stack Under Review
- **AI Core:** YOLOv11 (Ultralytics), OpenCV, ZBar, ZXing.
- **Simulation/Digital Twin:** Godot Engine (3D Forklift project).
- **Edge Control:** ESP32 (N16R8), OpenPLC.
- **Edge Node (S24 Ultra):** Android Native (Kotlin + C++20 NDK, OpenCV 4.14.0, Camera2 Zero-Copy).
- **ERP Integration:** Odoo XML-RPC.

## 📝 Recent Progress & Findings
- **Vision:** Successfully implemented a 2-stage pipeline (Detection -> Ensemble Decoding).
- **Visual SLAM (Feasibility):** Created `src/inference/localization.py` for ArUco-based 6DoF pose estimation.
- **Native Transition Plan:** Created `android_native_app_transition_plan.md` & `ADR_006_android_native_app_transition.md`.
- **Native Environment Setup:** D-drive development layout and toolchain finalized in `Android_Native_Environment_Setup_Guide.md` (Android Studio Rabbit 1, OpenCV 4.14.0, API 37.2, NDK 27.3, CMake 3.31.6).

## 🚀 Next Steps (for Feasibility Verification)
1. **Device Verification:** Connect S24 Ultra with USB Debugging enabled, verify `adb devices` and NDK/CMake/OpenCV paths.
2. **Phase 1 Implementation:** Create Android Studio NDK base project with C++20 CMake configuration.
3. **Zero-Copy Camera Pipeline:** Implement Camera2 API + NDK AImageReader JNI zero-copy bridge.
4. **C++ AprilTag & PnP Porting:** Port `src/app.py` vision algorithms into native C++ `libnexusedge.so`.

---
*This document serves as a persistent record of the project's current state and goals.*

## Connections
- **ADRs**:
  - [[ADR_002_inventory_mapping_feasibility]]
  - [[ADR_003_phase1_data_collection]]
  - [[ADR_004_phase2_live_poc]]
  - [[ADR_005_phase2_pick_and_place_logic]]
  - [[ADR_006_android_native_app_transition]]
- **Guides**:
  - [[Android_Native_Environment_Setup_Guide]]
  - [[Termux_Environment_Setup_Guide]]
- **Session Summaries**:
  - [[Session_Summary_2026-07-16]]
  - [[Session_Summary_20260716]]
  - [[Session_Summary_20261019_2]]
  - [[Session_Summary_20261020]]

**Tags**: #Hub #Overview
