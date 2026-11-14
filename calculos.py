
import math


# =====================================================
# MATERIALES
# Conductividad termica aproximada (W/m K)
# =====================================================

MATERIALES = {
    "Cobre": 401.0,
    "Aluminio": 237.0,
    "Bronce": 60.0,
    "Hierro fundido": 55.0,
    "Acero al carbono": 54.0,
    "Acero inoxidable": 16.0,
}


def obtener_conductividad_material(nombre):
    if nombre not in MATERIALES:
        raise ValueError(f"Material no reconocido: {nombre}")
    return MATERIALES[nombre]


# =====================================================
# FLUIDOS
# Propiedades aproximadas de referencia
# =====================================================

FLUIDOS = {
    "Agua": {
        "cp": 4180.0,
        "rho": 995.0,
        "mu": 0.0008,
        "k": 0.62,
    },
    "Etilenglicol (50%)": {
        "cp": 3400.0,
        "rho": 1065.0,
        "mu": 0.0060,
        "k": 0.39,
    },
    "Aceite termico": {
        "cp": 2100.0,
        "rho": 850.0,
        "mu": 0.0200,
        "k": 0.13,
    },
}


def obtener_propiedades_fluido(nombre):
    if nombre not in FLUIDOS:
        raise ValueError(f"Fluido no reconocido: {nombre}")
    return FLUIDOS[nombre].copy()


# =====================================================
# BALANCE ENERGETICO
# =====================================================

def balance_energetico(mh, cp_h, Thi, Tho, mc, cp_c, Tci):

    if mh <= 0 or cp_h <= 0 or mc <= 0 or cp_c <= 0:
        raise ValueError("Caudales y calores especificos deben ser positivos.")

    Q = mh * cp_h * (Thi - Tho)

    if Q <= 0:
        raise ValueError("La carga termica debe ser positiva.")

    Tco = Tci + Q / (mc * cp_c)

    return {"Q": Q, "Tco": Tco}


# =====================================================
# DIFERENCIA MEDIA LOGARITMICA
# =====================================================

def diferencia_media_logaritmica(Thi, Tho, Tci, Tco):

    dt1 = Thi - Tco
    dt2 = Tho - Tci

    if dt1 <= 0 or dt2 <= 0:
        raise ValueError(
            "Las diferencias terminales deben ser positivas. "
            "Revisa las temperaturas y los caudales."
        )

    if math.isclose(dt1, dt2, rel_tol=1e-10, abs_tol=1e-12):
        return (dt1 + dt2) / 2.0

    return (dt1 - dt2) / math.log(dt1 / dt2)


# =====================================================
# GEOMETRIA DOBLE TUBO
# =====================================================

def geometria_doble_tubo(Di, Do, D2):

    if not (0 < Di < Do < D2):
        raise ValueError("Debe cumplirse 0 < Di < Do < D2.")

    return {
        "area_interior": math.pi * Di**2 / 4.0,
        "area_anular": math.pi * (D2**2 - Do**2) / 4.0,
        "diametro_hidraulico": D2 - Do,
    }


# =====================================================
# MECANICA DE FLUIDOS
# =====================================================

def velocidad_fluido(caudal_masico, densidad, area):

    if min(caudal_masico, densidad, area) <= 0:
        raise ValueError("Caudal, densidad y area deben ser positivos.")

    return caudal_masico / (densidad * area)


def numero_reynolds(densidad, velocidad, diametro, viscosidad):

    if min(densidad, velocidad, diametro, viscosidad) <= 0:
        raise ValueError("Las propiedades y dimensiones deben ser positivas.")

    return densidad * velocidad * diametro / viscosidad


def numero_prandtl(cp, viscosidad, conductividad):

    if min(cp, viscosidad, conductividad) <= 0:
        raise ValueError("Las propiedades deben ser positivas.")

    return cp * viscosidad / conductividad


# =====================================================
# TRANSFERENCIA DE CALOR
# =====================================================

def dittus_boelter(Re, Pr, n):

    if Re <= 0 or Pr <= 0:
        raise ValueError("Re y Pr deben ser positivos.")

    if Re < 10000:
        raise ValueError(
            "Dittus-Boelter no se recomienda para Re < 10000. "
            "Utiliza numero_nusselt()."
        )

    if not 0.6 <= Pr <= 160:
        raise ValueError("Pr fuera del rango usual de Dittus-Boelter.")

    if n not in (0.3, 0.4):
        raise ValueError("Utiliza n=0.3 o n=0.4.")

    return 0.023 * Re**0.8 * Pr**n


def numero_nusselt(Re, Pr):
    """
    Estimacion por regimen:
    Laminar: Nu = 3.66.
    Transicion: interpolacion orientativa.
    Turbulento: Gnielinski.
    """

    if Re <= 0 or Pr <= 0:
        raise ValueError("Re y Pr deben ser positivos.")

    if Pr < 0.5 or Pr > 2000:
        raise ValueError("Pr fuera del rango orientativo de la correlacion.")

    if Re < 2300:
        return 3.66

    def gnielinski(re):

        f = (0.79 * math.log(re) - 1.64) ** -2

        numerador = (f / 8.0) * (re - 1000.0) * Pr

        denominador = (
            1.0
            + 12.7 * math.sqrt(f / 8.0)
            * (Pr**(2.0 / 3.0) - 1.0)
        )

        if denominador <= 0:
            raise ValueError("No se puede calcular Gnielinski con estos datos.")

        return numerador / denominador

    if Re < 3000:

        nu_laminar = 3.66
        nu_turbulento = gnielinski(3000.0)

        fraccion = (Re - 2300.0) / 700.0

        return nu_laminar + fraccion * (nu_turbulento - nu_laminar)

    return gnielinski(Re)


# =====================================================
# COEFICIENTE GLOBAL DE TRANSFERENCIA
# =====================================================

def coeficiente_global_exterior(hi, ho, Di, Do, kw):

    if min(hi, ho, Di, Do, kw) <= 0 or Do <= Di:
        raise ValueError("Revisa coeficientes, diametros y conductividad.")

    resistencia_interior = Do / (hi * Di)

    resistencia_pared = (
        Do * math.log(Do / Di) / (2.0 * kw)
    )

    resistencia_exterior = 1.0 / ho

    resistencia_total = (
        resistencia_interior
        + resistencia_pared
        + resistencia_exterior
    )

    return 1.0 / resistencia_total


# =====================================================
# AREA Y LONGITUD
# =====================================================

def area_transferencia(Q, U, LMTD):

    if min(Q, U, LMTD) <= 0:
        raise ValueError("Q, U y LMTD deben ser positivos.")

    return Q / (U * LMTD)


def longitud_intercambiador(A, Do):

    if A <= 0 or Do <= 0:
        raise ValueError("Area y diametro deben ser positivos.")

    return A / (math.pi * Do)


# =====================================================
# FACTOR DE FRICCION
# =====================================================

def factor_friccion_blasius(Re):

    if Re <= 0:
        raise ValueError("Reynolds debe ser positivo.")

    if Re < 2300:
        return 64.0 / Re

    f_laminar = 64.0 / 2300.0
    f_turbulento = 0.3164 / (4000.0**0.25)

    if Re < 4000:

        fraccion = (Re - 2300.0) / 1700.0

        return (
            f_laminar
            + fraccion * (f_turbulento - f_laminar)
        )

    return 0.3164 / (Re**0.25)


# =====================================================
# CAIDA DE PRESION
# =====================================================

def caida_presion(f, L, D, densidad, velocidad):

    if min(f, L, D, densidad, velocidad) < 0:
        raise ValueError("Los valores no pueden ser negativos.")

    if D == 0 or densidad == 0:
        raise ValueError("Diametro y densidad deben ser positivos.")

    return f * (L / D) * (densidad * velocidad**2 / 2.0)


# =====================================================
# POTENCIA HIDRAULICA
# =====================================================

def potencia_hidraulica(deltaP, caudal_masico, densidad):

    if deltaP < 0 or caudal_masico < 0 or densidad <= 0:
        raise ValueError("Revisa presion, caudal y densidad.")

    caudal_volumetrico = caudal_masico / densidad

    return deltaP * caudal_volumetrico
