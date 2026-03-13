import datetime
from flask import Flask, jsonify, request
from thermal_model import compute_thermal_model

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False  


# Structured response
def build_response(raw: dict, status: str = "success") -> dict:
    """
    Convert flat model output into a clean, nested enterprise-grade response.

    Top-level sections:
      meta               — request metadata (timestamp, version, status)
      inputs             — key input parameters echoed back for traceability
      thermal_resistances — full resistance network breakdown  [degC/W]
      geometry            — fin geometry derived values
      flow                — convective flow characterisation
      results             — primary engineering outputs
    """
    return {
        # 1. Metadata
        "meta": {
            "status":    status,
            "version":   "1.0.0",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "units": {
                "resistance":   "degC/W",
                "temperature":  "degC",
                "area":         "m2",
                "heat_transfer_coefficient": "W/m2.K"
            }
        },

        # 2. Key inputs echoed for traceability
        "inputs": {
            "thermal_design_power_W":  150,
            "ambient_temperature_C":   25,
            "air_velocity_m_per_s":    1.0,
            "n_fins":                  60,
            "fin_height_m":            0.0245,
            "fin_thickness_m":         0.0008,
            "heat_sink_width_m":       0.116,
            "heat_sink_length_m":      0.09,
            "k_aluminum_W_mK":         167.0,
            "k_TIM_W_mK":              4.0,
            "k_air_W_mK":              0.0262,
            "prandtl_number":          0.71,
            "kinematic_viscosity_m2_s": 1.568e-5
        },

        # 3. Thermal resistance network
        "thermal_resistances": {
            "R_jc":   raw["R_jc_C_per_W"],      # Junction-to-case
            "R_TIM":  raw["R_TIM_C_per_W"],      # Thermal Interface Material
            "R_cond": raw["R_cond_C_per_W"],     # Conduction through HS base
            "R_conv": raw["R_conv_C_per_W"],     # Convection over fins
            "R_hs":   raw["R_hs_C_per_W"],       # R_cond + R_conv
            "R_total": raw["R_total_C_per_W"]    # R_jc + R_TIM + R_hs
        },

        # 4. Fin geometry
        "geometry": {
            "fin_spacing_m":      raw["fin_spacing_m"],
            "area_single_fin_m2": raw["area_single_fin_m2"],
            "total_fin_area_m2":  raw["total_fin_area_m2"],
            "base_gap_area_m2":   raw["area_base_m2"],
            "A_total_m2":         raw["A_total_m2"]
        },

        # 5. Flow characterisation
        "flow": {
            "reynolds_number":           raw["reynolds_number"],
            "nusselt_number":            raw["nusselt_number"],
            "heat_transfer_coefficient": raw["h_conv_W_m2K"],
            "regime":                    raw["flow_regime"]
        },

        # 6. Primary results
        "results": {
            "junction_temperature_C": raw["T_junction_C"]
        }
    }


# Routes

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":    "healthy",
        "service":   "expert-thermal-api",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/thermal", methods=["GET"])
def thermal():
    try:
        Q         = float(request.args.get("Q",         150))
        T_ambient = float(request.args.get("T_ambient", 25))
        V         = float(request.args.get("V",         1.0))

        raw      = compute_thermal_model(Q=Q, T_ambient=T_ambient, V=V)
        response = build_response(raw, status="success")
        return jsonify(response), 200

    except (ValueError, TypeError) as exc:
        return jsonify({
            "meta":    {"status": "error", "version": "1.0.0"},
            "error":   "Invalid query parameter",
            "detail":  str(exc)
        }), 400

    except Exception as exc:
        return jsonify({
            "meta":    {"status": "error", "version": "1.0.0"},
            "error":   "Internal server error",
            "detail":  str(exc)
        }), 500


if __name__ == "__main__":
    print("=" * 60)
    print("  Expert Thermal — Heat Sink API  v1.0.0")
    print("  GET http://127.0.0.1:5000/thermal")
    print("  GET http://127.0.0.1:5000/health")
    print("  Optional params: ?Q=150&T_ambient=25&V=1.0")
    print("=" * 60)
    app.run(debug=True, port=5000)