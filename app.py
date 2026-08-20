"""Bible Widget Desktop — premium transparent Verse of the Day for Windows."""

from __future__ import annotations

import json
import sys
import threading
import webbrowser
from ctypes import windll
from pathlib import Path

try:
    from pythonnet import load as load_runtime

    load_runtime("netfx")
except Exception:
    pass

import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Drawing import (
    Bitmap,
    Color,
    ContentAlignment,
    Font,
    FontStyle,
    Graphics,
    GraphicsUnit,
    Point,
    Rectangle,
    Region,
    Size,
    SolidBrush,
    StringFormat,
    StringAlignment,
    Pen,
)
from System.Drawing.Drawing2D import (
    GraphicsPath,
    InterpolationMode,
    LineCap,
    LinearGradientBrush,
    SmoothingMode,
)
from System.Drawing.Imaging import ColorMatrix, ImageAttributes
from System.Windows.Forms import (
    Application,
    Button,
    ControlStyles,
    Cursors,
    DockStyle,
    FlatStyle,
    Form,
    FormBorderStyle,
    FormStartPosition,
    Label,
    MouseButtons,
    Padding,
    Panel,
    PictureBox,
    PictureBoxSizeMode,
    Screen,
    TextFormatFlags,
    TextRenderer,
    Timer,
    ToolTip,
)

from verse import cached_verse, fetch_verse, ms_until_dubai_930

APP_NAME = "Bible Widget — Verse of the Day"
SITE_URL = "https://www.wordonair.com"
CONFIG_FILE = Path.home() / ".bible-widget-desktop" / "config.json"
DISCLAIMER = (
    "Scripture quotations are from the ESV® Bible "
    "(The Holy Bible, English Standard Version®), copyright © Crossway."
)

# Premium WordOnAir palette
NAVY = Color.FromArgb(28, 58, 110)
NAVY_DEEP = Color.FromArgb(18, 38, 72)
WHITE = Color.FromArgb(250, 252, 255)
GOLD = Color.FromArgb(212, 168, 83)
GOLD_SOFT = Color.FromArgb(180, 212, 168, 83)
TEAL = Color.FromArgb(94, 196, 207)
MUTED = Color.FromArgb(200, 214, 230)
SURFACE = Color.FromArgb(42, 62, 98)
BORDER = Color.FromArgb(120, 190, 210, 235)

WM_NCLBUTTONDOWN = 0xA1
HTCAPTION = 0x2
WIDGET_OPACITY = 0.88
RESIZE_BORDER = 8


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


MARK_PATH = app_dir() / "widget" / "assets" / "wordonair-mark.png"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(data: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def rounded_region(width: int, height: int, radius: int = 18) -> Region:
    path = GraphicsPath()
    d = radius * 2
    path.AddArc(0, 0, d, d, 180, 90)
    path.AddArc(width - d, 0, d, d, 270, 90)
    path.AddArc(width - d, height - d, d, d, 0, 90)
    path.AddArc(0, height - d, d, d, 90, 90)
    path.CloseFigure()
    return Region(path)


def ui_font(name: str, size: float, style=FontStyle.Regular) -> Font:
    try:
        return Font(name, size, style)
    except Exception:
        fallback = "Georgia" if name in ("Palatino Linotype", "Georgia", "Constantia") else "Segoe UI"
        try:
            return Font(fallback, size, style)
        except Exception:
            return Font("Segoe UI", size)


def load_mark_image():
    if not MARK_PATH.exists():
        return None
    src = Bitmap(str(MARK_PATH))
    src.MakeTransparent(Color.White)
    for x in range(src.Width):
        for y in range(src.Height):
            pixel = src.GetPixel(x, y)
            if pixel.A > 0 and pixel.R > 235 and pixel.G > 235 and pixel.B > 228:
                src.SetPixel(x, y, Color.FromArgb(0, pixel.R, pixel.G, pixel.B))
    return src


def make_premium_cross(size: int = 30) -> Bitmap:
    """Sharp gold Latin cross with soft glow — not a chunky rectangle."""
    bmp = Bitmap(size, size)
    gfx = Graphics.FromImage(bmp)
    gfx.SmoothingMode = SmoothingMode.AntiAlias
    gfx.Clear(Color.Transparent)

    cx = size / 2.0
    # Soft glow behind the cross
    glow = SolidBrush(Color.FromArgb(55, GOLD))
    gfx.FillEllipse(glow, 2, 2, size - 4, size - 4)

    thickness = max(size * 0.16, 3.2)
    pen = Pen(GOLD, thickness)
    pen.StartCap = LineCap.Round
    pen.EndCap = LineCap.Round
    gfx.DrawLine(pen, cx, size * 0.08, cx, size * 0.92)
    gfx.DrawLine(pen, size * 0.14, size * 0.34, size * 0.86, size * 0.34)

    # Subtle highlight on the gold
    hi = Pen(Color.FromArgb(160, 255, 230, 170), thickness * 0.35)
    hi.StartCap = LineCap.Round
    hi.EndCap = LineCap.Round
    gfx.DrawLine(hi, cx - 0.5, size * 0.12, cx - 0.5, size * 0.88)

    pen.Dispose()
    hi.Dispose()
    glow.Dispose()
    gfx.Dispose()
    return bmp


class GlassPanel(Panel):
    def __init__(self) -> None:
        Panel.__init__(self)
        self.SetStyle(
            ControlStyles.AllPaintingInWmPaint
            | ControlStyles.OptimizedDoubleBuffer
            | ControlStyles.UserPaint
            | ControlStyles.ResizeRedraw
            | ControlStyles.SupportsTransparentBackColor,
            True,
        )
        self.UpdateStyles()


class VerseForm(Form):
    def __init__(self) -> None:
        Form.__init__(self)
        self.Text = APP_NAME
        self.FormBorderStyle = getattr(FormBorderStyle, "None")
        self.StartPosition = FormStartPosition.Manual
        self.TopMost = True
        self.ShowInTaskbar = True
        self.BackColor = NAVY_DEEP
        self.ForeColor = WHITE
        self.Opacity = WIDGET_OPACITY
        self.MinimumSize = Size(320, 360)
        self.Size = Size(390, 540)
        self.DoubleBuffered = True
        self._on_top = True
        self._current = None
        self._poll_ticks = 0
        self._pending = None
        self._fetching = False
        self._fitting = False
        self._mark = load_mark_image()
        self._tips = ToolTip()
        self._tips.ShowAlways = True
        self._resize_dir = None
        self._resize_start = None
        self._resize_bounds = None

        config = load_config()
        if config.get("width") and config.get("height"):
            self.Size = Size(int(config["width"]), int(config["height"]))
        if config.get("x") is not None and config.get("y") is not None:
            self.Location = Point(int(config["x"]), int(config["y"]))
        else:
            self.StartPosition = FormStartPosition.CenterScreen
        if "on_top" in config:
            self._on_top = bool(config["on_top"])
            self.TopMost = self._on_top

        self._build_ui()
        self.Resize += self._on_resize
        self.FormClosing += self._on_closing
        self.MouseMove += self._on_mouse_move
        self.MouseUp += self._on_mouse_up
        self._apply_round_region()
        self._show_cached_then_fetch()
        self._start_timer()

    def _build_ui(self) -> None:
        self._root = GlassPanel()
        self._root.Dock = DockStyle.Fill
        self._root.BackColor = NAVY
        self._root.Padding = Padding(18)
        self._root.MouseDown += self._start_drag
        self._root.Paint += self._paint_chrome
        self.Controls.Add(self._root)

        self._cross = PictureBox()
        self._cross.Size = Size(30, 30)
        self._cross.SizeMode = PictureBoxSizeMode.Zoom
        self._cross.BackColor = Color.Transparent
        self._cross.Image = make_premium_cross(30)
        self._cross.MouseDown += self._start_drag
        self._root.Controls.Add(self._cross)

        self._title = Label()
        self._title.Text = "VERSE OF THE DAY"
        self._title.ForeColor = WHITE
        self._title.Font = ui_font("Segoe UI Semibold", 10.5, FontStyle.Bold)
        self._title.AutoSize = False
        self._title.AutoEllipsis = True
        self._title.TextAlign = ContentAlignment.MiddleLeft
        self._title.BackColor = Color.Transparent
        self._title.MouseDown += self._start_drag
        self._root.Controls.Add(self._title)

        # Clear controls: Refresh · Keep on top · Close
        self._btn_refresh = self._make_button("↻", "Refresh verse", width=34)
        self._btn_pin = self._make_button("Top", "Keep widget on top of other windows", width=42)
        self._btn_close = self._make_button("✕", "Close", width=34)
        self._btn_refresh.Click += lambda *_: self._fetch()
        self._btn_pin.Click += lambda *_: self._toggle_pin()
        self._btn_close.Click += lambda *_: self.Close()
        self._root.Controls.Add(self._btn_refresh)
        self._root.Controls.Add(self._btn_pin)
        self._root.Controls.Add(self._btn_close)

        self._verse = Label()
        self._verse.Text = "Fetching today's verse..."
        self._verse.ForeColor = WHITE
        self._verse.Font = ui_font("Palatino Linotype", 13.5, FontStyle.Italic)
        self._verse.TextAlign = ContentAlignment.MiddleCenter
        self._verse.BackColor = Color.Transparent
        self._verse.MouseDown += self._start_drag
        self._root.Controls.Add(self._verse)

        self._reference = Label()
        self._reference.ForeColor = GOLD
        self._reference.Font = ui_font("Calibri", 12.5, FontStyle.Bold)
        self._reference.TextAlign = ContentAlignment.MiddleCenter
        self._reference.BackColor = Color.Transparent
        self._reference.MouseDown += self._start_drag
        self._root.Controls.Add(self._reference)

        self._message = Label()
        self._message.ForeColor = TEAL
        self._message.Font = ui_font("Segoe UI Semibold", 9, FontStyle.Bold)
        self._message.TextAlign = ContentAlignment.MiddleCenter
        self._message.BackColor = Color.Transparent
        self._message.MouseDown += self._start_drag
        self._root.Controls.Add(self._message)

        self._meaning_panel = GlassPanel()
        self._meaning_panel.BackColor = SURFACE
        self._meaning_panel.Padding = Padding(14, 10, 12, 10)
        self._meaning_panel.MouseDown += self._start_drag
        self._meaning_panel.Paint += self._paint_meaning_frame
        self._root.Controls.Add(self._meaning_panel)

        self._meaning = Label()
        self._meaning.ForeColor = MUTED
        self._meaning.Font = ui_font("Georgia", 10.5)
        self._meaning.Dock = DockStyle.Fill
        self._meaning.BackColor = Color.Transparent
        self._meaning.MouseDown += self._start_drag
        self._meaning_panel.Controls.Add(self._meaning)

        self._brand = Label()
        self._brand.Text = "WORDONAIR LABS"
        self._brand.ForeColor = GOLD
        self._brand.Font = ui_font("Segoe UI Semibold", 9, FontStyle.Bold)
        self._brand.TextAlign = ContentAlignment.MiddleCenter
        self._brand.BackColor = Color.Transparent
        self._brand.Cursor = Cursors.Hand
        self._brand.Click += self._open_website
        self._tips.SetToolTip(self._brand, SITE_URL)
        self._root.Controls.Add(self._brand)

        self._disclaimer = Label()
        self._disclaimer.Text = DISCLAIMER
        self._disclaimer.ForeColor = MUTED
        self._disclaimer.Font = ui_font("Georgia", 7.5)
        self._disclaimer.TextAlign = ContentAlignment.MiddleCenter
        self._disclaimer.BackColor = Color.Transparent
        self._disclaimer.MouseDown += self._start_drag
        self._root.Controls.Add(self._disclaimer)

        self._status = Label()
        self._status.ForeColor = MUTED
        self._status.Font = ui_font("Segoe UI", 8)
        self._status.TextAlign = ContentAlignment.MiddleCenter
        self._status.BackColor = Color.Transparent
        self._status.MouseDown += self._start_drag
        self._root.Controls.Add(self._status)

        # Visible resize handle (bottom-right)
        self._grip = Label()
        self._grip.Text = "◢"
        self._grip.Size = Size(16, 16)
        self._grip.ForeColor = GOLD
        self._grip.BackColor = Color.Transparent
        self._grip.Font = ui_font("Segoe UI", 9)
        self._grip.Cursor = Cursors.SizeNWSE
        self._grip.TextAlign = ContentAlignment.MiddleCenter
        self._grip.MouseDown += self._start_grip_resize
        self._tips.SetToolTip(self._grip, "Drag to resize")
        self._root.Controls.Add(self._grip)

        self._root.MouseMove += self._on_mouse_move
        self._root.MouseUp += self._on_mouse_up

        self._layout_controls()
        self._sync_pin_button()
        self._btn_refresh.BringToFront()
        self._btn_pin.BringToFront()
        self._btn_close.BringToFront()
        self._grip.BringToFront()

    def _make_button(self, text: str, tip: str, width: int = 34) -> Button:
        btn = Button()
        btn.Text = text
        btn.Size = Size(width, 30)
        btn.FlatStyle = FlatStyle.Flat
        btn.FlatAppearance.BorderSize = 1
        btn.FlatAppearance.BorderColor = BORDER
        btn.FlatAppearance.MouseOverBackColor = Color.FromArgb(70, 100, 150)
        btn.BackColor = Color.FromArgb(45, 75, 125)
        btn.ForeColor = WHITE
        btn.Font = ui_font("Segoe UI Semibold", 9, FontStyle.Bold)
        btn.Cursor = Cursors.Hand
        btn.TabStop = False
        self._tips.SetToolTip(btn, tip)
        return btn

    def _measure_text(self, text: str, font: Font, width: int) -> int:
        if not text:
            return 0
        measured = TextRenderer.MeasureText(
            text,
            font,
            Size(max(width, 40), 4000),
            TextFormatFlags.WordBreak | TextFormatFlags.TextBoxControl,
        )
        return measured.Height

    def _fit_height(self) -> None:
        if self._fitting or self._resize_dir:
            return
        pad = 18
        inner_w = max(self.ClientSize.Width - pad * 2, 140)
        verse_h = max(self._measure_text(self._verse.Text, self._verse.Font, inner_w) + 16, 72)
        msg_h = 26 if self._message.Visible else 0
        meaning_h = 0
        if self._meaning_panel.Visible:
            meaning_h = max(
                self._measure_text(self._meaning.Text, self._meaning.Font, inner_w - 28) + 28,
                52,
            )
        needed = 66 + verse_h + 8 + 24 + 6 + msg_h + (meaning_h + 8 if meaning_h else 0) + 8 + 78 + 18
        screen = Screen.FromControl(self).WorkingArea
        max_h = max(self.MinimumSize.Height, screen.Height - 40)
        new_h = min(max(int(needed), self.MinimumSize.Height), max_h)
        if abs(new_h - self.Height) <= 4:
            return
        self._fitting = True
        try:
            self.Height = new_h
        finally:
            self._fitting = False

    def _layout_controls(self) -> None:
        pad = 18
        w = self.ClientSize.Width
        h = self.ClientSize.Height
        inner_w = max(w - pad * 2, 140)

        self._cross.Location = Point(pad, pad + 1)
        self._btn_close.Location = Point(w - pad - 34, pad)
        self._btn_pin.Location = Point(w - pad - 80, pad)
        self._btn_refresh.Location = Point(w - pad - 118, pad)

        title_left = pad + 38
        title_right = self._btn_refresh.Left - 12
        self._title.Location = Point(title_left, pad + 4)
        self._title.Size = Size(max(title_right - title_left, 48), 26)

        body_top = pad + 48
        verse_h = max(self._measure_text(self._verse.Text, self._verse.Font, inner_w) + 16, 72)
        self._verse.Location = Point(pad, body_top)
        self._verse.Size = Size(inner_w, verse_h)

        y = self._verse.Bottom + 8
        self._reference.Location = Point(pad, y)
        self._reference.Size = Size(inner_w, 24)
        y = self._reference.Bottom + 6

        if self._message.Visible:
            self._message.Location = Point(pad, y)
            self._message.Size = Size(inner_w, 18)
            y = self._message.Bottom + 8

        if self._meaning_panel.Visible:
            meaning_h = max(
                self._measure_text(self._meaning.Text, self._meaning.Font, inner_w - 28) + 28,
                52,
            )
            self._meaning_panel.Location = Point(pad, y)
            self._meaning_panel.Size = Size(inner_w, meaning_h)

        self._brand.Location = Point(pad, h - pad - 56)
        self._brand.Size = Size(inner_w, 18)
        self._disclaimer.Location = Point(pad, h - pad - 36)
        self._disclaimer.Size = Size(inner_w, 36)
        self._status.Location = Point(pad, self._meaning_panel.Bottom + 2)
        self._status.Size = Size(inner_w, 14)
        self._grip.Location = Point(w - 20, h - 20)
        self._root.Invalidate()
        self._btn_refresh.BringToFront()
        self._btn_pin.BringToFront()
        self._btn_close.BringToFront()
        self._grip.BringToFront()

    def _paint_chrome(self, sender, args) -> None:
        gfx = args.Graphics
        gfx.SmoothingMode = SmoothingMode.AntiAlias
        gfx.InterpolationMode = InterpolationMode.HighQualityBicubic

        # Soft vertical navy gradient (premium depth, not flat grey)
        bounds = sender.ClientRectangle
        with LinearGradientBrush(
            bounds,
            Color.FromArgb(38, 72, 128),
            Color.FromArgb(22, 48, 92),
            90.0,
        ) as brush:
            gfx.FillRectangle(brush, bounds)

        # Centered WordOnAir mark — sharp, subtle
        if self._mark is not None:
            size = min(int(sender.Width * 0.42), 180)
            x = (sender.Width - size) // 2
            y = (sender.Height - size) // 2 + 10
            matrix = ColorMatrix()
            matrix.Matrix33 = 0.14
            attrs = ImageAttributes()
            attrs.SetColorMatrix(matrix)
            gfx.DrawImage(
                self._mark,
                Rectangle(x, y, size, size),
                0,
                0,
                self._mark.Width,
                self._mark.Height,
                GraphicsUnit.Pixel,
                attrs,
            )

        # Gold accent line under header
        with Pen(GOLD_SOFT, 1.2) as pen:
            gfx.DrawLine(pen, 18, 52, sender.Width - 18, 52)

        # Thin gold outer rim hint
        with Pen(Color.FromArgb(70, GOLD), 1.0) as rim:
            gfx.DrawRectangle(rim, 1, 1, sender.Width - 3, sender.Height - 3)

    def _paint_meaning_frame(self, sender, args) -> None:
        gfx = args.Graphics
        gfx.SmoothingMode = SmoothingMode.AntiAlias
        rect = sender.ClientRectangle
        with SolidBrush(SURFACE) as fill:
            gfx.FillRectangle(fill, rect)
        with Pen(GOLD, 3.0) as accent:
            gfx.DrawLine(accent, 1, 4, 1, rect.Height - 4)
        with Pen(Color.FromArgb(50, WHITE), 1.0) as edge:
            gfx.DrawRectangle(edge, 0, 0, rect.Width - 1, rect.Height - 1)

    def _apply_round_region(self) -> None:
        self.Region = rounded_region(self.Width, self.Height, 18)

    def _on_resize(self, *_args) -> None:
        self._layout_controls()
        if not self._fitting and not self._resize_dir:
            self._fit_height()
            self._layout_controls()
        self._apply_round_region()

    def _edge_hit(self, client: Point) -> str | None:
        w = self.ClientSize.Width
        h = self.ClientSize.Height
        left = client.X <= RESIZE_BORDER
        right = client.X >= w - RESIZE_BORDER
        top = client.Y <= RESIZE_BORDER
        bottom = client.Y >= h - RESIZE_BORDER
        if top and left:
            return "nw"
        if top and right:
            return "ne"
        if bottom and left:
            return "sw"
        if bottom and right:
            return "se"
        if left:
            return "w"
        if right:
            return "e"
        if top:
            return "n"
        if bottom:
            return "s"
        return None

    def _cursor_for_edge(self, hit: str | None):
        return {
            "n": Cursors.SizeNS,
            "s": Cursors.SizeNS,
            "e": Cursors.SizeWE,
            "w": Cursors.SizeWE,
            "nw": Cursors.SizeNWSE,
            "se": Cursors.SizeNWSE,
            "ne": Cursors.SizeNESW,
            "sw": Cursors.SizeNESW,
        }.get(hit, Cursors.Default)

    def _to_form_client(self, sender, location: Point) -> Point:
        if sender is self:
            return location
        return self.PointToClient(sender.PointToScreen(location))

    def _begin_resize(self, direction: str, client: Point) -> None:
        self._resize_dir = direction
        self._resize_start = self.PointToScreen(client)
        self._resize_bounds = Rectangle(self.Left, self.Top, self.Width, self.Height)
        self.Capture = True
        self.Cursor = self._cursor_for_edge(direction)

    def _apply_resize(self, client: Point) -> None:
        if not self._resize_dir or self._resize_start is None or self._resize_bounds is None:
            return
        screen = self.PointToScreen(client)
        dx = screen.X - self._resize_start.X
        dy = screen.Y - self._resize_start.Y
        box = self._resize_bounds
        left, top, width, height = box.X, box.Y, box.Width, box.Height
        direction = self._resize_dir

        if "e" in direction:
            width = max(self.MinimumSize.Width, box.Width + dx)
        if "s" in direction:
            height = max(self.MinimumSize.Height, box.Height + dy)
        if "w" in direction:
            width = max(self.MinimumSize.Width, box.Width - dx)
            left = box.Right - width
        if "n" in direction:
            height = max(self.MinimumSize.Height, box.Height - dy)
            top = box.Bottom - height

        self.SetBounds(left, top, width, height)

    def _on_mouse_move(self, sender, args) -> None:
        client = self._to_form_client(sender, args.Location)
        if self._resize_dir:
            self._apply_resize(client)
            return
        hit = self._edge_hit(client)
        if hit:
            self.Cursor = self._cursor_for_edge(hit)
        elif sender is self or sender is self._root:
            self.Cursor = Cursors.Default

    def _on_mouse_up(self, sender, args) -> None:
        if self._resize_dir:
            self._resize_dir = None
            self._resize_start = None
            self._resize_bounds = None
            self.Capture = False
            self.Cursor = Cursors.Default
            self._fit_height()
            self._layout_controls()
            self._apply_round_region()

    def _start_grip_resize(self, sender, args) -> None:
        if args.Button == MouseButtons.Left:
            client = self._to_form_client(sender, args.Location)
            self._begin_resize("se", client)

    def _start_drag(self, sender, args) -> None:
        if args.Button != MouseButtons.Left:
            return
        client = self._to_form_client(sender, args.Location)
        hit = self._edge_hit(client)
        if hit:
            self._begin_resize(hit, client)
            return
        windll.user32.ReleaseCapture()
        windll.user32.SendMessageW(self.Handle.ToInt32(), WM_NCLBUTTONDOWN, HTCAPTION, 0)

    def _open_website(self, *_args) -> None:
        webbrowser.open(SITE_URL)

    def _toggle_pin(self) -> None:
        self._on_top = not self._on_top
        self.TopMost = self._on_top
        self._sync_pin_button()

    def _sync_pin_button(self) -> None:
        self._btn_pin.ForeColor = GOLD if self._on_top else WHITE
        self._btn_pin.FlatAppearance.BorderColor = GOLD if self._on_top else BORDER
        tip = "Pinned — stays on top (click to unpin)" if self._on_top else "Keep widget on top of other windows"
        self._tips.SetToolTip(self._btn_pin, tip)

    def _show_cached_then_fetch(self) -> None:
        cached = cached_verse()
        if cached:
            self._render(cached)
        self._fetch()

    def _fetch(self, *_args) -> None:
        if self._fetching:
            return
        self._fetching = True

        def worker() -> None:
            try:
                self._pending = (fetch_verse(), False)
            except Exception:
                self._pending = (
                    {
                        "text": "Waiting for connection...",
                        "reference": "Bible Widget",
                        "message": "",
                        "meaning": "",
                    },
                    True,
                )
            finally:
                self._fetching = False

        threading.Thread(target=worker, daemon=True).start()

    def _apply_pending(self, *_args) -> None:
        pending = self._pending
        if pending is None:
            return
        self._pending = None
        verse, offline = pending
        if offline and self._current:
            self._status.Text = "Will update when you are back online"
            return
        self._render(verse, offline=offline)

    def _render(self, verse: dict, offline: bool = False) -> None:
        self._current = verse
        text = (verse.get("text") or "").strip()
        if text and not text.startswith("“") and not text.startswith('"'):
            text = f"“{text}”"
        self._verse.Text = text
        self._reference.Text = verse.get("reference") or ""
        message = (verse.get("message") or "").strip()
        self._message.Text = message.upper()
        self._message.Visible = bool(message)
        meaning = (verse.get("meaning") or "").strip()
        self._meaning.Text = meaning
        self._meaning_panel.Visible = bool(meaning)
        self._status.Text = "Will update when you are back online" if offline else ""
        self._layout_controls()
        self._fit_height()
        self._layout_controls()
        self._apply_round_region()

    def _start_timer(self) -> None:
        self._apply_timer = Timer()
        self._apply_timer.Interval = 250
        self._apply_timer.Tick += self._apply_pending
        self._apply_timer.Start()

        self._timer = Timer()
        self._timer.Interval = 60_000
        self._timer.Tick += self._on_tick
        self._timer.Start()

    def _on_tick(self, *_args) -> None:
        self._poll_ticks += 1
        if self._poll_ticks % 15 == 0:
            self._fetch()
        if ms_until_dubai_930() <= 60_000:
            self._fetch()

    def _on_closing(self, *_args) -> None:
        save_config(
            {
                "x": self.Left,
                "y": self.Top,
                "width": self.Width,
                "height": self.Height,
                "on_top": self._on_top,
            }
        )


def main() -> int:
    Application.EnableVisualStyles()
    Application.SetCompatibleTextRenderingDefault(False)
    Application.Run(VerseForm())
    return 0


if __name__ == "__main__":
    sys.exit(main())
