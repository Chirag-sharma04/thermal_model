def compute_thermal_model(
    # Power and environment
    Q=150,              # Thermal Design Power [W]
    T_ambient=25,       # Ambient temperature [deg C]

    # Die / processor
    A_die=0.00236,    # Die area [m^2]  (52.5mm x 45mm)
    R_jc=0.2,           # Junction-to-case resistance [deg C/W] 

    # TIM (Thermal Interface Material -- thermal grease)
    t_TIM=0.0001,       # TIM thickness [m]
    k_TIM=4.0,          # TIM thermal conductivity [W/m.K]

    # Heat sink base (Aluminum Al 6061-T6)
    k_Al=167.0,         # Aluminum thermal conductivity [W/m.K]
    t_base=0.0025,      # Base thickness [m]

    # Air properties at 25 deg C
    k_air=0.0262,       # Air thermal conductivity [W/m.K]
    Pr=0.71,            # Prandtl number
    nu=1.568e-5,        # Kinematic viscosity [m^2/s]
    V=1.0,              # Air velocity [m/s]

    # Heat sink fin geometry
    hs_width=0.116,     # Heat sink width [m]
    hs_length=0.09,     # Heat sink length [m] (= characteristic length L)
    N_fins=60,          # Number of fins
    fin_thickness=0.0008,  # Fin thickness [m]
    fin_height=0.0245,  # Fin height [m]
):
    """
    Compute the thermal resistance network and return all results as a dict.
    """

    results = {}

    # ----------------------------------------------------------------
    # Step 1: Fin spacing
    # S_f = (hs_width - N_fins * fin_thickness) / (N_fins - 1)
    # ----------------------------------------------------------------
    S_f = (hs_width - N_fins * fin_thickness) / (N_fins - 1)
    results["fin_spacing_m"] = round(S_f, 7)
    print(f"Step 1 | Fin Spacing S_f = {S_f*1000:.4f} mm")

    # ----------------------------------------------------------------
    # Step 2: Reynolds number (fin spacing used as hydraulic length)
    # Re = (V * S_f) / nu
    # ----------------------------------------------------------------
    Re = (V * S_f) / nu
    results["reynolds_number"] = round(Re, 4)
    print(f"Step 2 | Reynolds Number Re = {Re:.4f}  (Laminar if Re < 2300)")

    # ----------------------------------------------------------------
    # Step 3: Nusselt number
    # Laminar  (Re < 2300): Sieder-Tate  Nu = 1.86*(Re*Pr*2*S_f/L)^(1/3)
    # Turbulent(Re >= 2300): Dittus-Boelter Nu = 0.023*Re^0.8*Pr^0.3
    # ----------------------------------------------------------------
    L = hs_length
    if Re < 2300:
        Nu = 1.86 * (Re * Pr * (2 * S_f / L)) ** (1.0 / 3.0)
        flow_regime = "Laminar"
    else:
        Nu = 0.023 * (Re ** 0.8) * (Pr ** 0.3)
        flow_regime = "Turbulent"
    results["nusselt_number"] = round(Nu, 6)
    results["flow_regime"] = flow_regime
    print(f"Step 3 | Flow: {flow_regime} | Nu = {Nu:.6f}")

    # ----------------------------------------------------------------
    # Step 4: Convective heat transfer coefficient
    # h = (Nu * k_air) / (2 * S_f)
    # ----------------------------------------------------------------
    h = (Nu * k_air) / (2 * S_f)
    results["h_conv_W_m2K"] = round(h, 4)
    print(f"Step 4 | h = {h:.4f} W/m^2.K")

    # ----------------------------------------------------------------
    # Step 5: Total convection area
    #   Single fin area = 2 * fin_height * hs_length  (both faces)
    #                   + fin_thickness * hs_length    (fin tip)
    #   Total fin area  = N_fins * single_fin_area
    #   Base gap area   = (N_fins - 1) * S_f * hs_length
    #   A_total         = total_fin_area + base_gap_area
    # ----------------------------------------------------------------
    area_single_fin = (2 * fin_height + fin_thickness) * hs_length
    total_fin_area  = N_fins * area_single_fin
    area_base       = (N_fins - 1) * S_f * hs_length
    A_total         = total_fin_area + area_base
    results["area_single_fin_m2"] = round(area_single_fin, 6)
    results["total_fin_area_m2"]  = round(total_fin_area, 5)
    results["area_base_m2"]       = round(area_base, 5)
    results["A_total_m2"]         = round(A_total, 6)
    print(f"Step 5 | Single fin = {area_single_fin:.6f} m^2 | Total fin = {total_fin_area:.5f} m^2")
    print(f"         Base gaps  = {area_base:.6f} m^2 | A_total = {A_total:.6f} m^2")

    # ----------------------------------------------------------------
    # Step 6: Convection resistance
    # R_conv = 1 / (h * A_total)
    # ----------------------------------------------------------------
    R_conv = 1.0 / (h * A_total)
    results["R_conv_C_per_W"] = round(R_conv, 8)
    print(f"Step 6 | R_conv = {R_conv:.6f} degC/W")

    # ----------------------------------------------------------------
    # Step 7: Conduction resistance through heat sink base
    # R_cond = t_base / (k_Al * A_die)
    # ----------------------------------------------------------------
    R_cond = t_base / (k_Al * A_die)
    results["R_cond_C_per_W"] = round(R_cond, 8)
    print(f"Step 7 | R_cond = {R_cond:.6f} degC/W")

    # ----------------------------------------------------------------
    # Step 8: Total heat sink resistance
    # R_hs = R_cond + R_conv
    # ----------------------------------------------------------------
    R_hs = R_cond + R_conv
    results["R_hs_C_per_W"] = round(R_hs, 6)
    print(f"Step 8 | R_hs = {R_hs:.6f} degC/W")

    # ----------------------------------------------------------------
    # Step 9: TIM resistance
    # R_TIM = t_TIM / (k_TIM * A_die)
    # ----------------------------------------------------------------
    R_TIM = t_TIM / (k_TIM * A_die)
    results["R_TIM_C_per_W"] = round(R_TIM, 8)
    print(f"Step 9 | R_TIM = {R_TIM:.6f} degC/W")

    # ----------------------------------------------------------------
    # Step 9b: Total thermal resistance
    # R_total = R_jc + R_TIM + R_hs
    # ----------------------------------------------------------------
    R_total = R_jc + R_TIM + R_hs
    results["R_jc_C_per_W"]    = R_jc
    results["R_total_C_per_W"] = round(R_total, 6)
    print(f"Step 9b| R_jc={R_jc:.4f}  R_TIM={R_TIM:.6f}  R_hs={R_hs:.6f}")
    print(f"         R_total = {R_total:.6f} degC/W")

    # ----------------------------------------------------------------
    # Step 10: Junction temperature
    # T_junction = T_ambient + Q * R_total
    # ----------------------------------------------------------------
    T_junction = T_ambient + Q * R_total
    results["T_junction_C"] = round(T_junction, 4)
    print(f"Step 10| T_junction = {T_junction:.4f} degC")

    return results


# Run standalone
if __name__ == "__main__":
    print("=" * 65)
    print("       HEAT SINK THERMAL RESISTANCE MODEL -- Expert Thermal")
    print("=" * 65)
    out = compute_thermal_model()
    print("=" * 65)
    print(f"  RESULT  Heat Sink Resistance : {out['R_hs_C_per_W']:.6f}  degC/W")
    print(f"  RESULT  Junction Temperature : {out['T_junction_C']:.4f}   degC")
    print("-" * 65)
    print(f"  REF     Heat Sink Resistance : 0.373043  degC/W")
    print(f"  REF     Junction Temperature : 80.9565   degC")
    print("=" * 65)