# Expert Thermal — Heat Sink API v1.0.0

A high-performance, Python API for computing heat sink thermal resistance and semiconductor junction temperatures. This project utilizes established fluid dynamics and heat transfer correlations to provide accurate thermal modeling for electronics cooling applications.

## 🚀 Features

- **Advanced Thermal Modeling**: Built-in calculations for Reynolds number, Nusselt number, and convective heat transfer coefficients.
- **Dual Flow Regimes**: Automatically handles both **Laminar** (Sieder-Tate) and **Turbulent** (Dittus-Boelter) flow conditions.
- **RESTful API**: Clean Flask-based interface providing structured JSON responses.
- **Extensive Model Network**: Computes Junction-to-Case ($R_{jc}$), TIM ($R_{TIM}$), Conduction ($R_{cond}$), and Convection ($R_{conv}$) resistances.
- **Traceability**: All input parameters are echoed back in the API response for full auditability.

---

## 🛠️ Installation

1. **Clone or copy the repository** to your local machine.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏃 How to Run

### 1. Start the API Server
Run the main application to start the Flask development server:
```bash
python app.py
```
The server will start at `http://127.0.0.1:5000`.

### 2. Standalone Model Test
To run a quick validation of the physics model without the API overhead:
```bash
python thermal_model.py
```

---

## 📡 API Documentation

### `GET /thermal`
Computes the full thermal model based on input parameters.

**Query Parameters:**
| Parameter | Description | Default | Unit |
| :--- | :--- | :--- | :--- |
| `Q` | Thermal Design Power (Heat Load) | `150` | Watts (W) |
| `T_ambient` | Ambient Air Temperature | `25` | Celsius (°C) |
| `V` | Inlet Air Velocity | `1.0` | m/s |

**Example Request:**
```bash
GET http://127.0.0.1:5000/thermal?Q=120&T_ambient=30&V=1.5
```

### `GET /health`
Returns the operational status of the service.

---

## 🧪 Technical Overview

The model follows a 10-step analytical process:
1. **Geometry Analysis**: Calculates fin spacing and hydraulic lengths.
2. **Flow Characterization**: Determines the Reynolds number ($Re$).
3. **Nusselt Selection**: 
   - Uses **Sieder-Tate** for Laminar flow ($Re < 2300$).
   - Uses **Dittus-Boelter** for Turbulent flow ($Re \ge 2300$).
4. **Resistance Network**: Aggregates serial resistances to find $R_{total}$.
5. **Junction Prediction**: Applies $T_j = T_a + Q \cdot R_{total}$ to find final die temperature.

## 📂 Project Structure

- `app.py`: Flask entry point and response structuring.
- `thermal_model.py`: Core physics engine and math implementation.
- `requirements.txt`: Minimal dependencies (Flask).

---
