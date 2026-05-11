import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

from hdate import HDateInfo, HebrewDate, Location, Zmanim

# (lat, lon, timezone, altitude_m, diaspora)
LOCATIONS: dict[str, tuple[float, float, str, int, bool]] = {
    "Jerusalem": (31.778, 35.236, "Asia/Jerusalem", 750, False),
    "Tel Aviv": (32.085, 34.781, "Asia/Jerusalem", 20, False),
    "New York": (40.713, -74.006, "America/New_York", 10, True),
    "London": (51.507, -0.128, "Europe/London", 35, True),
}

_FALLBACK = LOCATIONS["Jerusalem"]


class HebrewDemo(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Hebrew Dates Demo - Powered by hdate")
        self.geometry("820x680")
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        ttk.Label(self, text="Gregorian Date (YYYY-MM-DD):").pack(pady=5)
        self.date_entry = ttk.Entry(self)
        self.date_entry.insert(0, date.today().isoformat())
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
            self, wrap=tk.WORD, height=30, font=("Consolas", 11)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    def _calculate(self) -> None:
        try:
            gdate = date.fromisoformat(self.date_entry.get().strip())
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
        sunrise = zmanim_dict.get("sunrise") or "Not available"
        sunset = zmanim_dict.get("sunset") or "Not available"
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


