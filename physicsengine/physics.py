#* Imports de libraires

from math import sqrt, atan2, pi, cos, sin, isclose, radians
from physicsengine.constants import *

#* Définitions des fonctions

def limit_speed(vx: float, vy: float, max_speed: float) -> tuple[float, float]:
    """Limite la norme du vecteur vitesse à max_speed."""
    v_norm = sqrt(vx**2 + vy**2)
    if v_norm <= max_speed:
        return vx,vy
    else:
        return (max_speed/v_norm)*vx, (max_speed/v_norm)*vy

def angle_from_velocity(vx: float, vy: float) -> float:
    """Retourne l'angle correspondant au vecteur vitesse."""
    return atan2(vy, vx)

def lerp_angle(a: float, b: float, t: float) -> float:
    """Interpolation angulaire entre a et b par le plus court chemin."""
    raw_delta = b - a
    delta = (raw_delta + pi)%(2*pi) - pi
    return a + t*delta

#* Fonction de modèle pour mettre un sujet à jour dans main.py

def update_physics(
    x: float, y: float,                 # position (pixels)
    vx: float, vy: float,               # vitesse (px/s)
    angle_control: float,               # angle "commandé" (radians)
    go_up: bool,                        # l'objet accélère-t-il ?
    dt: float                           # pas de temps (s)
) -> tuple[float, float, float, float, float]:
    """
    Met à jour le modèle cinématique sur un pas de temps DT (en secondes).

    Équations appliquées :
        v(t+dt) = v(t) + a * dt
        p(t+dt) = p(t) + v * dt
        v       = FRICTION * v
        theta_v = atan2(vy, vx)

    Paramètres
    ----------
    x, y : float
        Position (pixels).
    vx, vy : float
        Vitesse (pixels/seconde).
    angle_control : float
        Direction désirée (radians).
    go_up : bool
        True si l'objet accélère.
    dt: float
        Pas de temps (s)

    Constantes utilisées (globales)
    -------------------------------
    ACCEL : float
    FRICTION : float
    MAX_SPEED : float

    Retour
    ------
    (x, y, vx, vy, angle_velocity)
        x, y : nouvelle position
        vx, vy : nouvelle vitesse
        angle_velocity : direction réelle du mouvement
    """
    # On vérifie que l'objet accélère bien
    if go_up:
        ax, ay = ACCEL*cos(angle_control), ACCEL*sin(angle_control)
    else:
        ax, ay = 0, 0

    # Calculs de la nouvelle vitesse
    # Multiplication dt > on limite la vitesse > on applique la friction
    new_vx, new_vy = vx + ax*dt, vy + ay*dt
    new_vx, new_vy = limit_speed(new_vx, new_vy, MAX_SPEED)
    new_vx, new_vy = new_vx*FRICTION, new_vy*FRICTION

    # Calculs de la nouvelle position
    new_x = x + vx*dt
    new_y = y + vy*dt

    # Calcul de la direction réelle du mouvement
    angle_velocity = angle_from_velocity(vx, vy)

    return new_x, new_y, new_vx, new_vy, angle_velocity

# Tests
if __name__ == "__main__":
    print("=== TESTS limit_speed ===")
    assert limit_speed(100, 0, 50) == (50.0, 0.0)
    assert limit_speed(0, 0, 50) == (0.0, 0.0)
    assert limit_speed(30, 40, 50) == (30.0, 40.0)  # norme = 50, rien ne change

    print("\n=== TESTS angle_from_velocity ===")
    assert angle_from_velocity(1, 0) == 0.0
    assert isclose(angle_from_velocity(0, 1), pi/2)
    assert isclose(angle_from_velocity(-1, 0), pi)
    assert angle_from_velocity(0, 0) == 0.0
    
    print("\n=== TESTS lerp_angle ===")
    a_test = radians(179)
    b_test = radians(-179)
    res = lerp_angle(a_test, b_test, 0.5)
    assert abs(res - radians(180)) < 1e-3  # interpolation du petit arc

    print("\n=== TESTS update_physics ===")
    # État initial
    x_test, y_test = 0.0, 0.0
    vx_test, vy_test = 0.0, 0.0
    # "Haut-gauche" maintenu (UP+LEFT) = -135° = -3π/4
    angle_control = -3 * pi / 4
    # Une itération de mise à jour : nouvelles position et vitesse
    x_test, y_test, vx_test, vy_test, ang_v = update_physics(
        x_test, y_test, vx_test, vy_test, angle_control, True, 0.02
    )



