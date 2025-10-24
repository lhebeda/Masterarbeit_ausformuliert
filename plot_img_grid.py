from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PIL import Image
import os

# ============ KONFIGURATION ============

# Ordner mit Bildern (kann absolut oder relativ sein)
IMAGE_DIR = "Editing/output_frames/Paper/Keypoints"

#Liste der PNG-Dateinamen (max. 8)
# IMAGE_FILES = [
#     "img_single.png",
#     "depth_single.png",
#     "bbox_single.png",
#     "overlay_single.png",
#     "img_multiple.png",
#     "depth_multiple.png",
#     "bbox_multiple.png",
#     "overlay_multiple.png"
# ]

# IMAGE_FILES = [
#     "00000.png",
#     "00000_overlay.png"
# ]

IMAGE_FILES = [
    "00000.png",
    "00015.png",
    "00037.png",
    "00055.png",
    "00000_keypoints.png",
    "00015_keypoints.png",
    "00037_keypoints.png",
    "00055_keypoints.png"
]


# Ausgabe-PDF
OUTPUT_PDF = "ausgabe.pdf"

# Layout-Parameter (A4, sehr eng)
PAGE_SIZE = A4
COLS = 4
LEFT_MARGIN = 1 * mm
RIGHT_MARGIN = 1 * mm
TOP_MARGIN = 1 * mm
BOTTOM_MARGIN = 1 * mm
H_GAP = 1 * mm
V_GAP = 1 * mm

# ======================================

def make_grid_pdf(output_pdf, image_paths):
    page_w, page_h = PAGE_SIZE
    c = canvas.Canvas(output_pdf, pagesize=PAGE_SIZE)

    # Zellenbreite berechnen (horizontal bleibt gleich)
    cell_w = (page_w - LEFT_MARGIN - RIGHT_MARGIN - (COLS - 1) * H_GAP) / COLS

    # Bilder prüfen & laden
    images = []
    for path in image_paths[:COLS*8]:  # Max 8, aber flexibel
        if not os.path.exists(path):
            print(f"⚠️  WARNUNG: Datei nicht gefunden – {path}")
            continue
        im = Image.open(path)
        images.append((path, im.width, im.height))

    if not images:
        print("❌ Keine Bilder gefunden. PDF wird leer.")
        c.showPage()
        c.save()
        return

    # In Reihen gruppieren
    num_images = len(images)
    num_rows = (num_images + COLS - 1) // COLS
    row_groups = [images[i*COLS:(i+1)*COLS] for i in range(num_rows)]

    # Höhe pro Reihe berechnen (basierend auf max Aspect Ratio in der Reihe)
    row_hs = []
    for group in row_groups:
        max_aspect = max(ih / iw for _, iw, ih in group)
        row_h = cell_w * max_aspect
        row_hs.append(row_h)

    # Gesamthöhe des Inhalts berechnen
    total_content_h = sum(row_hs) + (len(row_hs) - 1) * V_GAP

    # Verfügbare Höhe
    available_h = page_h - TOP_MARGIN - BOTTOM_MARGIN

    # Start-Y für Zentrierung (falls Inhalt kleiner als verfügbar)
    if total_content_h < available_h:
        start_y = page_h - TOP_MARGIN - (available_h - total_content_h) / 2
    else:
        start_y = page_h - TOP_MARGIN  # Oder anpassen, falls Überlauf

    # Aktuelle Y-Position (Top der ersten Reihe)
    current_y = start_y

    # Reihen zeichnen
    for r in range(len(row_hs)):
        row_h = row_hs[r]
        group = row_groups[r]

        cell_top = current_y
        cell_bottom = current_y - row_h

        # Bilder in der Reihe zeichnen
        for c_idx in range(len(group)):
            path, iw, ih = group[c_idx]

            # Seitenverhältnis
            aspect = ih / iw

            # Zielgröße (primär an Breite anpassen)
            target_w = cell_w
            target_h = cell_w * aspect

            # Falls Aspect größer (sollte nicht, da row_h = max), aber sicherheitshalber
            if target_h > row_h:
                target_h = row_h
                target_w = row_h * (iw / ih)

            # Position: X zentriert
            cell_left = LEFT_MARGIN + c_idx * (cell_w + H_GAP)
            x = cell_left + (cell_w - target_w) / 2

            # Y zentriert in der Reihe
            y = cell_bottom + (row_h - target_h) / 2

            c.drawImage(path, x, y, width=target_w, height=target_h, mask='auto')

        # Nächste Reihe: Unterhalb mit V_GAP
        current_y = cell_bottom - V_GAP

    c.showPage()
    c.save()
    print(f"✅ PDF gespeichert: {output_pdf}")

if __name__ == "__main__":
    # Pfade zusammensetzen
    full_paths = [os.path.join(IMAGE_DIR, fname) for fname in IMAGE_FILES]
    make_grid_pdf(OUTPUT_PDF, full_paths)