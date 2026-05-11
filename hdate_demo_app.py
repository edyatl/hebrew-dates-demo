import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import date
import os
import sys

from hdate import HDateInfo, HebrewDate, Location, Zmanim

# (lat, lon, timezone, altitude_m, diaspora)
LOCATIONS: dict[str, tuple[float, float, str, int, bool]] = {
    "Jerusalem": (31.778, 35.236, "Asia/Jerusalem", 750, False),
    "Tel Aviv": (32.085, 34.781, "Asia/Jerusalem", 20, False),
    "New York": (40.713, -74.006, "America/New_York", 10, True),
    "London": (51.507, -0.128, "Europe/London", 35, True),
    # Russia
    "Moscow": (55.7558, 37.6176, "Europe/Moscow", 156, True),
    "Saint Petersburg": (59.9343, 30.3351, "Europe/Moscow", 3, True),
    "Novosibirsk": (55.0084, 82.9357, "Asia/Novosibirsk", 151, True),
    "Yekaterinburg": (56.8389, 60.6057, "Asia/Yekaterinburg", 237, True),
    "Kazan": (55.7963, 49.1088, "Europe/Moscow", 116, True),
    "Nizhny Novgorod": (56.3269, 44.0059, "Europe/Moscow", 151, True),
    "Chelyabinsk": (55.1644, 61.4368, "Asia/Yekaterinburg", 220, True),
    "Samara": (53.1959, 50.1008, "Europe/Samara", 100, True),
    "Omsk": (54.9885, 73.3242, "Asia/Omsk", 87, True),
    "Rostov-on-Don": (47.2357, 39.7015, "Europe/Moscow", 70, True),
}

_FALLBACK = LOCATIONS["Jerusalem"]


class HebrewDemo(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.set_window_icon()
        self.title("Hebrew Dates Demo - Powered by hdate")
        self.geometry("820x680")
        self.configure(background="#2d2d2d")
        self._setup_dark_mode()
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def set_window_icon(self):
            """Set application icon with fallback"""
            try:
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                icon_path = os.path.join(base_path, "assets", "icon.png")
                
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.iconphoto(False, icon)          # Modern & cross-platform
                else:
                    # Fallback to .ico on Windows
                    ico_path = os.path.join(base_path, "assets", "icon.ico")
                    if os.path.exists(ico_path):
                        self.iconbitmap(ico_path)
            except Exception:
                pass  # Fail silently if icon is missing

    def _setup_dark_mode(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", foreground="#e0e0e0", background="#2d2d2d")
        style.configure("TButton", foreground="#e0e0e0", background="#4a90e2")
        style.map("TButton", background=[("active", "#3a7ab5")])
        style.configure("TCombobox", foreground="#e0e0e0", background="#2d2d2d", fieldbackground="#2d2d2d")
        style.map("TCombobox", 
            fieldbackground=[("readonly", "#2d2d2d")],
            foreground=[("readonly", "#e0e0e0")],
            background=[("readonly", "#2d2d2d")]
        )

    def _build_ui(self) -> None:
        ttk.Label(self, text="Gregorian Date:").pack(pady=5)
        self.date_entry = DateEntry(
            self, 
            width=12, 
            bg="#2d2d2d",
            fg="#e0e0e0",
            borderwidth=2, 
            date_pattern="yyyy-MM-dd", 
            headersbackground="#1e1e1e",
            headersforeground="#ffffff",
            selectbackground="#4a90e2",
            selectforeground="#ffffff",
            normalbackground="#2d2d2d",
            normalforeground="#e0e0e0",
            weekendbackground="#2d2d2d",
            weekendforeground="#e0e0e0",
            othermonthbackground="#252525",
            othermonthforeground="#808080"
        )
        self.date_entry.set_date(date.today())
        self.date_entry.pack()

        ttk.Label(self, text="Location:").pack(pady=5)
        self.loc_var = tk.StringVar(value="New York")
        ttk.Combobox(
            self,
            textvariable=self.loc_var,
            values=list(LOCATIONS),
            state="readonly",
        ).pack()

        ttk.Button(self, text="Calculate", command=self._calculate).pack(pady=15)

        self.result_text = tk.Text(
            self, wrap=tk.WORD, height=30, font=("Consolas", 11), bg="#1e1e1e", fg="#e0e0e0"
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    def _calculate(self) -> None:
        try:
            gdate = self.date_entry.get_date()
            output = self._build_output(gdate, self.loc_var.get())
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", str(exc))
            return

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, output)

    def _build_output(self, gdate: date, loc_name: str) -> str:
        lat, lon, tz, elev, diaspora = LOCATIONS.get(loc_name, _FALLBACK)

        loc = Location(
            name=loc_name,
            latitude=lat,
            longitude=lon,
            timezone=tz,
            altitude=elev,
            diaspora=diaspora,
        )

        h = HDateInfo(date=gdate, diaspora=diaspora)
        z = Zmanim(date=gdate, location=loc)

        zmanim_dict = z.zmanim
        sunrise = z.zmanim["netz_hachama"].local or "Not available"
        sunset = z.zmanim["shkia"].local or "Not available"
        candle_lighting = z.candle_lighting or "Not available"
        havdalah = z.havdalah or "Not available"

        birth_heb = HebrewDate.from_gdate(gdate)
        bar_mitzvah_heb = birth_heb.replace(year=birth_heb.year + 13)
        bar_mitzvah_greg = bar_mitzvah_heb.to_gdate()

        holidays = ", ".join(str(hol) for hol in h.holidays) or "None"
        parasha = h.parasha or "None"

        return (
            f"RESULTS for {gdate}\n"
            f"\n"
            f"Hebrew Date:\n"
            f"  {h.hdate}\n"
            f"\n"
            f"Shabbat / Holiday:\n"
            f"  Is Shabbat:  {h.is_shabbat}\n"
            f"  Is Yom Tov:  {h.is_yom_tov}\n"
            f"  Holidays:    {holidays}\n"
            f"  Parasha:     {parasha}\n"
            f"\n"
            f"Zmanim ({loc_name}):\n"
            f"  Sunrise:          {sunrise}\n"
            f"  Sunset:           {sunset}\n"
            f"  Candle Lighting:  {candle_lighting}\n"
            f"  Havdalah:         {havdalah}\n"
            f"\n"
            f"Bar/Bat Mitzvah date if born on {gdate}\n"
            f"  Hebrew: {bar_mitzvah_heb}\n"
            f"  Gregorian (approx): {bar_mitzvah_greg}\n"
            f"\n"
            f"Powered by py-libhdate (fully offline).\n"
        )

