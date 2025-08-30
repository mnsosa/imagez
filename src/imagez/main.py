import os
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm as CM
import typer

app = typer.Typer(help="Create a target-size image with padding and center it on A4.")


def cm_to_px(value_cm: float, dpi: int) -> int:
    return int(round(value_cm * dpi / 2.54))


def parse_rgb(color: str) -> tuple:
    color = color.strip()
    if color.startswith("#") and len(color) == 7:
        return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
    parts = [p.strip() for p in color.split(",")]
    if len(parts) == 3:
        return tuple(max(0, min(255, int(p))) for p in parts)
    raise typer.BadParameter("Use '#RRGGBB' or 'R,G,B'.")


def ensure_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB") if img.mode != "RGB" else img


def fit_into_box_with_padding(
    src: Image.Image, target_w_px: int, target_h_px: int, pad_rgb: tuple[int, int, int]
) -> Image.Image:
    sw, sh = src.size
    scale = min(target_w_px / sw, target_h_px / sh)
    new_w = max(1, int(round(sw * scale)))
    new_h = max(1, int(round(sh * scale)))
    resized = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_w_px, target_h_px), pad_rgb)
    off_x = (target_w_px - new_w) // 2
    off_y = (target_h_px - new_h) // 2
    canvas.paste(resized, (off_x, off_y))
    return canvas


def save_png_with_dpi(img: Image.Image, path: str, dpi: int) -> str:
    img.save(path, dpi=(dpi, dpi))
    return path


def export_pdf_a4(
    place_img_path: str, out_pdf_path: str, w_cm: float, h_cm: float
) -> str | None:
    try:
        c = rl_canvas.Canvas(out_pdf_path, pagesize=A4)
        page_w, page_h = A4
        iw, ih = w_cm * CM, h_cm * CM
        x = (page_w - iw) / 2
        y = (page_h - ih) / 2
        c.drawImage(place_img_path, x, y, width=iw, height=ih)
        c.showPage()
        c.save()
        return out_pdf_path
    except Exception:
        return None


def process_image(
    input_path: str,
    out_dir: str,
    w_cm: float,
    h_cm: float,
    pad_rgb: tuple[int, int, int],
    dpi: int,
    mode: str = "todo",
) -> tuple[str | None, str | None, str | None]:
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(input_path))[0]
    src = Image.open(input_path)
    src = ensure_rgb(ImageOps.exif_transpose(src))
    target_w = cm_to_px(w_cm, dpi)
    target_h = cm_to_px(h_cm, dpi)
    boxed = fit_into_box_with_padding(src, target_w, target_h, pad_rgb)
    out_target_png: str | None = None
    out_a4_png: str | None = None
    pdf_path: str | None = None
    if mode in ("todo", "image"):
        out_target_png = os.path.join(out_dir, f"{base}_{int(w_cm)}x{int(h_cm)}cm.png")
        save_png_with_dpi(boxed, out_target_png, dpi)
    if mode in ("todo", "image_a4"):
        a4_w = cm_to_px(21.0, dpi)
        a4_h = cm_to_px(29.7, dpi)
        a4_canvas = Image.new("RGB", (a4_w, a4_h), (255, 255, 255))
        ax = (a4_w - target_w) // 2
        ay = (a4_h - target_h) // 2
        a4_canvas.paste(boxed, (ax, ay))
        out_a4_png = os.path.join(
            out_dir, f"{base}_A4_with_{int(w_cm)}x{int(h_cm)}.png"
        )
        save_png_with_dpi(a4_canvas, out_a4_png, dpi)
    if mode in ("todo", "pdf"):
        tmp_jpg = os.path.join(out_dir, f"{base}_place_tmp.jpg")
        boxed.save(tmp_jpg, "JPEG", quality=95, subsampling=0)
        out_pdf = os.path.join(out_dir, f"{base}_A4_with_{int(w_cm)}x{int(h_cm)}.pdf")
        pdf_path = export_pdf_a4(tmp_jpg, out_pdf, w_cm, h_cm)
        try:
            os.remove(tmp_jpg)
        except Exception:
            pass
    return out_target_png, out_a4_png, pdf_path


@app.command()
def main(
    path: str = typer.Argument(..., help="Input image path"),
    width_cm: float = typer.Option(20.0, "--width-cm", "-w", help="Target width in cm"),
    height_cm: float = typer.Option(
        25.0, "--height-cm", "-h", help="Target height in cm"
    ),
    padding: str = typer.Option(
        "#000000", "--padding", "-p", help="Padding color '#RRGGBB' or 'R,G,B'"
    ),
    dpi: int = typer.Option(300, "--dpi", help="Output DPI"),
    out_dir: str = typer.Option(".", "--out-dir", help="Output directory"),
    mode: str = typer.Option(
        "todo", "--mode", "-m", help="todo | pdf | image | image_a4"
    ),
):
    """Generate a target-sized image with padding and an A4 PDF/PNG with the image centered."""
    mode = mode.lower().strip()
    if mode not in {"todo", "pdf", "image", "image_a4"}:
        raise typer.BadParameter("mode must be one of: todo, pdf, image, image_a4")
    rgb = parse_rgb(padding)
    target_png, a4_png, pdf_path = process_image(
        path, out_dir, width_cm, height_cm, rgb, dpi, mode
    )
    if target_png:
        typer.echo(target_png)
    if a4_png:
        typer.echo(a4_png)
    if pdf_path:
        typer.echo(pdf_path)


if __name__ == "__main__":
    app()
