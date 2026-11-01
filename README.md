# Digital Stockman: Llama Server as an Autonomous Assistant for Livestock Farming

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![llama.cpp](https://img.shields.io/badge/Inference-llama.cpp-orange.svg)](https://github.com/ggerganov/llama.cpp)
[![Hardware](https://img.shields.io/badge/Hardware-NVIDIA%20DGX%20Spark-76B900.svg)](https://www.nvidia.com)

The **Digital Stockman** is an asymmetric client-server agentic architecture that deploys a quantised Large Language Model (LLM) via `llama.cpp` to function as an autonomous assistant for Precision Livestock Farming (PLF). It provides a natural language interface that bridges complex agricultural datasets—such as livestock growth records and health metrics—with everyday farmers, veterinarians, and agricultural consultants without requiring deep data-science expertise.

---

## Table of Contents
- [Overview](#overview)
- [Key Features & Benefits](#key-features--benefits)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Integrated Tool Utilities](#integrated-tool-utilities)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [License](#license)

---

## Overview

Modern Precision Livestock Farming produces vast amounts of data, yet translating raw numbers into actionable management decisions often requires specialized software skills. **Digital Stockman** addresses this gap by combining state-of-the-art quantized LLM inference, native tool/function calling, and tailored agricultural analytics scripts. Farmers interact with their data using natural language, enabling automated data cleaning, predictive herd growth modeling, and interactive visual dashboards.

---

## Key Features & Benefits

* **Intuitive Natural Language Interface:** Interact with complex farm records using plain conversational commands (e.g., *"Clean the uploaded weight logs and run the growth prediction model to forecast next month's weights"*).
* **Automated Data Cleansing:** Automatically handles missing values (such as standardising text `NA` vs. floating-point `NaN` values), detects data schemas, fixes messy column headers, and normalises datasets.
* **Herd Benchmarking & Qualitative Insights:** Synthesises actionable herd management reports—calculating average weekly gains, identifying top performers, and flagging laggards for early veterinary intervention.
* **Instant Visual Dashboards:** Generates interactive HTML visual dashboards containing numerical distribution histograms and categorical analyses in seconds.
* **Growth & Weight Forecasting:** Automatically fits regression models to historical weight data to project future growth trajectories (e.g., 30-day predicted weights and total weight gains).
* **Hardware Efficiency & Low-Cost Access:** Offloads computationally demanding AI inference to a high-performance central server while enabling low-power client terminals (such as standard Windows desktop PCs) to securely access the assistant over a mesh VPN.

---

## System Architecture

```
+-------------------------------------------------------------+
|                     Client Terminal                         |
|  - Standard Windows PC / Tablet / Mobile Device              |
|  - Natural Language Query Interface                         |
+------------------------------+------------------------------+
                               |
                   Encrypted Tailscale VPN
                               |
+------------------------------v------------------------------+
|                   Inference Server (DGX)                    |
|  - NVIDIA DGX Spark (Blackwell GPU + LPDDR5x Memory)        |
|  - llama.cpp Inference Engine                               |
|  - Quantised Model: Qwen3.6-35B-A3B-Uncensored (GGUF)       |
|                                                             |
|   +-----------------------------------------------------+   |
|   |             Tool-Augmented Modules                  |   |
|   |  - data_cleaner.py      - growth_predictor.py     |   |
|   |  - dashboard_creator.py - web_fetch.py             |   |
|   |  - Native C++ File & System Commands                |   |
|   +-----------------------------------------------------+   |
+-------------------------------------------------------------+
```

---

## Technologies Used

* **Large Language Model (LLM):** `Qwen3.6-35B-A3B-Uncensored` in GGUF format, optimised for multi-step reasoning and function calling.
* **Inference Engine:** [`llama.cpp`](https://github.com/ggerganov/llama.cpp) offering high-performance, lightweight native C++ HTTP server endpoints.
* **Hardware Infrastructure:**
  * **Inference Server:** NVIDIA DGX Spark featuring the GB10 Grace Blackwell Superchip (20-core Arm CPU, Blackwell GPU with 5th-gen Tensor Cores, and 128 GB coherent unified LPDDR5x memory) running Ubuntu Linux.
  * **Client Terminal:** Standard dual-core client PC (AMD A6 APU, 12 GB RAM) or mobile client.
* **Networking:** Secure, zero-config mesh VPN powered by [Tailscale](https://tailscale.com/).
* **Language & Execution Runtime:** Python 3.10+, C++17.

---

## Integrated Tool Utilities

The LLM agent is equipped with specialised agricultural tools that it can call dynamically based on user prompt context:

1. `data_cleaner.py`: Inspects, describes, previews, handles null values, and standardises column headers in CSV and Excel files.
2. `growth_predictor.py`: Fits linear regression models onto historical animal weight records to project target weights and calculate daily/weekly weight gains.
3. `dashboard_creator.py`: Generates standalone interactive HTML visual dashboards with customizable charts (scatter, bar, line, histograms).
4. `web_fetch.py`: Fetches and extracts clean text content from external web URLs for live referencing.
5. **Native C++ Tools:** File operations (`read_file`, `write_file`, `edit_file`), pattern matching (`grep`), directory globbing, and controlled execution.

---

## Getting Started

### Prerequisites

* Python 3.10+
* CMake & C++ Compiler (GCC/Clang/MSVC)
* `llama.cpp` built with CUDA or appropriate acceleration backend
* [Tailscale](https://tailscale.com/) installed on both server and client machines

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-org/digital-stockman.git
   cd digital-stockman
   ```

2. **Set Up the Python Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Build `llama.cpp` Server:**
   ```bash
   mkdir build && cd build
   cmake .. -DLLAMA_CUDA=ON
   cmake --build . --config Release
   ```

4. **Download Model Weights:**
   Place your quantized GGUF model (e.g., `qwen3.6-35b-a3b-uncensored.gguf`) into the `models/` directory.

---

## Usage Examples

### Starting the Server
```bash
./llama-server \
  --model models/qwen3.6-35b-a3b-uncensored.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n-gpu-layers 99
```

### Example Natural Language Queries

* **Data Cleaning:**
  > *"Please clean the uploaded file `north_wyke_weights_2026.csv`. Fix any missing values and give me a quick summary of the data."*

* **Growth Prediction:**
  > *"Run the growth prediction model on the herd dataset to estimate animal weights 30 days from now. Highlight any cattle falling below expected weight targets."*

* **Dashboard Generation:**
  > *"Create an interactive HTML dashboard showing the weight distribution and weekly gains across all paddocks."*

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
