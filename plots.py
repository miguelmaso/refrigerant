import numpy as np
import matplotlib.pyplot as plt


def add_label(x, y, index, text, offset_y=0, **kwargs):
    """
    Agrega una etiqueta tangente a la curva en el punto x[index], y[index].
    
    Parameters:
    x, y: Array of data.
    text: string of the label.
    index: Índice del array donde quieres poner la etiqueta.
    offset_y: Desplazamiento vertical en puntos (opcional) para separar el texto de la línea.
    """
    ax = plt.gca()
    
    # 1. Obtenemos dos puntos muy cercanos (el punto deseado y el siguiente)
    # Si es el último punto, tomamos el anterior para calcular la pendiente hacia atrás
    if index < 0:
        idx1, idx2 = index, index - 1
    else:
        idx1, idx2 = index, index + 1

    x1, y1 = x[idx1], y[idx1]
    x2, y2 = x[idx2], y[idx2]

    dx = x2 - x1
    dy = y2 - y1
    
    # arctan2 devuelve radianes, convertimos a grados
    angle = np.degrees(np.arctan2(dy, dx))

    # 4. Añadimos el texto
    # Usamos transform_rotates_text=True para que el texto rote correctamente con el sistema
    t = ax.text(x1, y1, text, 
                rotation=angle,
                rotation_mode='anchor', **kwargs)

    # (Opcional) Ajuste fino para separar el texto de la línea sin perder la rotación
    if offset_y != 0:
        # Usamos una transformación compuesta para mover el texto en "puntos" relativos a su posición
        from matplotlib.transforms import ScaledTranslation
        dx, dy = 0, offset_y / 72. # Convertir puntos a pulgadas aprox
        offset = ScaledTranslation(0, offset_y/72, ax.figure.dpi_scale_trans)
        t.set_transform(t.get_transform() + offset)
