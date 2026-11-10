import math


def balance_energetico(mh, cp_h, Thi, Tho, mc, cp_c, Tci):
    """
    Calcula la carga térmica y la temperatura de salida fría.
    """
    Q = mh * cp_h * (Thi - Tho)
    Tco = Tci + Q / (mc * cp_c)

    return {
        "Q": Q,
        "Tco": Tco
    }


def diferencia_media_logaritmica(Thi, Tho, Tci, Tco):
    """
    Calcula LMTD para configuración en contracorriente.
    """
    dt1 = Thi - Tco
    dt2 = Tho - Tci

    if dt1 <= 0 or dt2 <= 0:
        raise ValueError("Las diferencias de temperatura deben ser positivas.")

    if math.isclose(dt1, dt2, rel_tol=1e-10):
        return dt1

    return (dt1 - dt2) / math.log(dt1 / dt2)


def geometria_doble_tubo(Di, Do, D2):
    """
    Calcula las áreas de flujo y el diámetro hidráulico anular.
    """
    if not (0 < Di < Do < D2):
        raise ValueError("Debe cumplirse 0 < Di < Do < D2.")

    area_interior = math.pi * Di**2 / 4
    area_anular = math.pi * (D2**2 - Do**2) / 4
    diametro_hidraulico = D2 - Do

    return {
        "area_interior": area_interior,
        "area_anular": area_anular,
        "diametro_hidraulico": diametro_hidraulico
    }


def velocidad_fluido(caudal_masico, densidad, area):
    """
    Calcula velocidad media del fluido.
    """
    if caudal_masico <= 0 or densidad <= 0 or area <= 0:
        raise ValueError("Caudal, densidad y área deben ser positivos.")

    return caudal_masico / (densidad * area)


def numero_reynolds(densidad, velocidad, diametro, viscosidad):
    """
    Calcula el número de Reynolds.
    """
    if min(densidad, velocidad, diametro, viscosidad) <= 0:
        raise ValueError("Las propiedades y dimensiones deben ser positivas.")

    return densidad * velocidad * diametro / viscosidad


def numero_prandtl(cp, viscosidad, conductividad):
    """
    Calcula el número de Prandtl.
    """
    if min(cp, viscosidad, conductividad) <= 0:
        raise ValueError("Las propiedades deben ser positivas.")

    return cp * viscosidad / conductividad


def dittus_boelter(Re, Pr, n):
    """
    Correlación de Dittus-Boelter.
    n = 0.4 para fluido calentado.
    n = 0.3 para fluido enfriado.
    Debe verificarse su intervalo de validez antes de usarla.
    """
    if Re <= 0 or Pr <= 0:
        raise ValueError("Re y Pr deben ser positivos.")

    if Re < 10000:
        raise ValueError("Dittus-Boelter no se recomienda para Re < 10000.")

    return 0.023 * Re**0.8 * Pr**n


def coeficiente_global_exterior(hi, ho, Di, Do, kw):
    """
    Calcula U basado en el área exterior del tubo interior.
    Sin ensuciamiento.
    """
    if min(hi, ho, Di, Do, kw) <= 0:
        raise ValueError("Todos los valores deben ser positivos.")

    resistencia = (
        Do / (Di * hi)
        + Do * math.log(Do / Di) / (2 * kw)
        + 1 / ho
    )

    return 1 / resistencia


def area_transferencia(Q, U, LMTD):
    """
    Calcula el área exterior necesaria.
    """
    if min(Q, U, LMTD) <= 0:
        raise ValueError("Q, U y LMTD deben ser positivos.")

    return Q / (U * LMTD)


def longitud_intercambiador(area, Do):
    """
    Calcula longitud a partir del área exterior del tubo interior.
    """
    if area <= 0 or Do <= 0:
        raise ValueError("Área y diámetro deben ser positivos.")

    return area / (math.pi * Do)


def factor_friccion_blasius(Re):
    """
    Factor de fricción de Darcy para flujo turbulento
    en conductos lisos. Aproximación de Blasius.
    """
    if Re < 4000:
        raise ValueError(
            "Blasius se utiliza aquí para flujo turbulento."
        )

    return 0.3164 / (Re ** 0.25)


def caida_presion(f, longitud, diametro, densidad, velocidad):
    """
    Caída de presión por fricción distribuida.
    Ecuación de Darcy-Weisbach.
    """
    if min(f, longitud, diametro, densidad, velocidad) <= 0:
        raise ValueError("Todos los valores deben ser positivos.")

    return f * (longitud / diametro) * (
        densidad * velocidad**2 / 2
    )


def potencia_hidraulica(caida_p, caudal_masico, densidad):
    """
    Potencia hidráulica ideal requerida por el fluido.
    No incluye eficiencia de la bomba.
    """
    if min(caida_p, caudal_masico, densidad) <= 0:
        raise ValueError("Los valores deben ser positivos.")

    caudal_volumetrico = caudal_masico / densidad

    return caida_p * caudal_volumetrico

