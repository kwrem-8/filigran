import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os


CANVAS_W = 700
CANVAS_H = 500


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Filigran")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        self.base_image = None
        self.wm_image = None
        self.preview = None

        self.wm_x = 50
        self.wm_y = 50
        self.drag_offset = (0, 0)
        self.dragging = False

        self.opacity_var = tk.IntVar(value=50)
        self.text_var = tk.StringVar()
        self.text_opacity_var = tk.IntVar(value=50)
        self.text_size_var = tk.IntVar(value=36)

        self._build_ui()

    def _build_ui(self):
        left = tk.Frame(self, bg="#1e1e1e", width=220)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(16, 0), pady=16)
        left.pack_propagate(False)

        right = tk.Frame(self, bg="#1e1e1e")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=16)

        label_style = {"bg": "#1e1e1e", "fg": "#aaaaaa", "font": ("Segoe UI", 9)}
        btn_style = {
            "bg": "#2d2d2d", "fg": "#ffffff", "relief": tk.FLAT,
            "font": ("Segoe UI", 9), "cursor": "hand2",
            "activebackground": "#3a3a3a", "activeforeground": "#ffffff",
            "padx": 10, "pady": 6
        }

        tk.Label(left, text="ANA GÖRSEL", **label_style).pack(anchor="w", pady=(0, 4))
        tk.Button(left, text="Görsel Seç", command=self.load_base, **btn_style).pack(fill=tk.X)

        tk.Frame(left, bg="#333333", height=1).pack(fill=tk.X, pady=12)

        tk.Label(left, text="FİLİGRAN GÖRSELİ", **label_style).pack(anchor="w", pady=(0, 4))
        tk.Button(left, text="Filigran Seç", command=self.load_watermark, **btn_style).pack(fill=tk.X)

        tk.Label(left, text="Saydamlık", **label_style).pack(anchor="w", pady=(10, 2))
        tk.Scale(
            left, from_=0, to=100, orient=tk.HORIZONTAL,
            variable=self.opacity_var, command=self._on_change,
            bg="#1e1e1e", fg="#ffffff", troughcolor="#333333",
            highlightthickness=0, sliderrelief=tk.FLAT
        ).pack(fill=tk.X)

        tk.Frame(left, bg="#333333", height=1).pack(fill=tk.X, pady=12)

        tk.Label(left, text="METİN FİLİGRANI", **label_style).pack(anchor="w", pady=(0, 4))
        entry = tk.Entry(
            left, textvariable=self.text_var,
            bg="#2d2d2d", fg="#ffffff", insertbackground="#ffffff",
            relief=tk.FLAT, font=("Segoe UI", 10)
        )
        entry.pack(fill=tk.X, ipady=5)
        entry.bind("<KeyRelease>", self._on_change)

        tk.Label(left, text="Yazı Saydamlığı", **label_style).pack(anchor="w", pady=(10, 2))
        tk.Scale(
            left, from_=0, to=100, orient=tk.HORIZONTAL,
            variable=self.text_opacity_var, command=self._on_change,
            bg="#1e1e1e", fg="#ffffff", troughcolor="#333333",
            highlightthickness=0, sliderrelief=tk.FLAT
        ).pack(fill=tk.X)

        tk.Label(left, text="Yazı Boyutu", **label_style).pack(anchor="w", pady=(10, 2))
        tk.Scale(
            left, from_=12, to=120, orient=tk.HORIZONTAL,
            variable=self.text_size_var, command=self._on_change,
            bg="#1e1e1e", fg="#ffffff", troughcolor="#333333",
            highlightthickness=0, sliderrelief=tk.FLAT
        ).pack(fill=tk.X)

        tk.Frame(left, bg="#333333", height=1).pack(fill=tk.X, pady=12)

        tk.Button(
            left, text="Kaydet", command=self.save,
            bg="#4a90d9", fg="#ffffff", relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"), cursor="hand2",
            activebackground="#357abd", activeforeground="#ffffff",
            padx=10, pady=8
        ).pack(fill=tk.X)

        self.canvas = tk.Canvas(
            right, width=CANVAS_W, height=CANVAS_H,
            bg="#2a2a2a", highlightthickness=1,
            highlightbackground="#444444", cursor="crosshair"
        )
        self.canvas.pack()

        self.hint = self.canvas.create_text(
            CANVAS_W // 2, CANVAS_H // 2,
            text="Önce bir görsel seçin",
            fill="#555555", font=("Segoe UI", 13)
        )

        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        self.canvas.bind("<ButtonRelease-1>", self._drag_end)

    def load_base(self):
        path = filedialog.askopenfilename(
            filetypes=[("Görseller", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.gif")]
        )
        if not path:
            return
        self.base_image = Image.open(path).convert("RGBA")
        self.canvas.delete(self.hint)
        self._render()

    def load_watermark(self):
        path = filedialog.askopenfilename(
            filetypes=[("Görseller", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not path:
            return
        self.wm_image = Image.open(path).convert("RGBA")
        self._render()

    def _scaled_base(self):
        img = self.base_image.copy()
        img.thumbnail((CANVAS_W, CANVAS_H), Image.LANCZOS)
        return img

    def _render(self, *_):
        if self.base_image is None:
            return

        base = self._scaled_base()
        canvas_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (42, 42, 42, 255))
        ox = (CANVAS_W - base.width) // 2
        oy = (CANVAS_H - base.height) // 2
        canvas_img.paste(base, (ox, oy))

        if self.wm_image is not None:
            wm = self.wm_image.copy()
            alpha = int(self.opacity_var.get() / 100 * 255)
            r, g, b, a = wm.split()
            a = a.point(lambda v: int(v * alpha / 255))
            wm.putalpha(a)
            canvas_img.paste(wm, (self.wm_x, self.wm_y), wm)

        text = self.text_var.get().strip()
        if text:
            draw = ImageDraw.Draw(canvas_img)
            size = self.text_size_var.get()
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except Exception:
                font = ImageFont.load_default()
            alpha = int(self.text_opacity_var.get() / 100 * 255)
            draw.text((self.wm_x, self.wm_y + (self.wm_image.height + 8 if self.wm_image else 0)),
                      text, font=font, fill=(255, 255, 255, alpha))

        self.preview = ImageTk.PhotoImage(canvas_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.preview)

    def _on_change(self, *_):
        self._render()

    def _drag_start(self, event):
        if self.wm_image is None and not self.text_var.get().strip():
            return
        self.dragging = True
        self.drag_offset = (event.x - self.wm_x, event.y - self.wm_y)

    def _drag_move(self, event):
        if not self.dragging:
            return
        self.wm_x = event.x - self.drag_offset[0]
        self.wm_y = event.y - self.drag_offset[1]
        self._render()

    def _drag_end(self, event):
        self.dragging = False

    def save(self):
        if self.base_image is None:
            messagebox.showwarning("Uyarı", "Önce bir görsel seçmelisiniz.")
            return

        base = self.base_image.copy()
        scale_x = base.width / min(CANVAS_W, base.width)
        scale_y = base.height / min(CANVAS_H, base.height)

        thumb_w = min(CANVAS_W, base.width)
        thumb_h = min(CANVAS_H, base.height)
        ox = (CANVAS_W - thumb_w) // 2
        oy = (CANVAS_H - thumb_h) // 2

        real_x = int((self.wm_x - ox) * scale_x)
        real_y = int((self.wm_y - oy) * scale_y)

        if self.wm_image is not None:
            wm = self.wm_image.copy()
            alpha = int(self.opacity_var.get() / 100 * 255)
            r, g, b, a = wm.split()
            a = a.point(lambda v: int(v * alpha / 255))
            wm.putalpha(a)
            base.paste(wm, (real_x, real_y), wm)

        text = self.text_var.get().strip()
        if text:
            draw = ImageDraw.Draw(base)
            size = int(self.text_size_var.get() * scale_x)
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except Exception:
                font = ImageFont.load_default()
            alpha = int(self.text_opacity_var.get() / 100 * 255)
            ty = real_y + (self.wm_image.height + 8 if self.wm_image else 0)
            draw.text((real_x, ty), text, font=font, fill=(255, 255, 255, alpha))

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("WebP", "*.webp")]
        )
        if not path:
            return

        out = base.convert("RGB") if path.lower().endswith((".jpg", ".jpeg")) else base
        out.save(path)
        messagebox.showinfo("Kaydedildi", f"Görsel kaydedildi:\n{path}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
