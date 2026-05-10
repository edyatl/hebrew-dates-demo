import tkinter as tk
from tkinter import ttk, messagebox
import hdate
from datetime import date

class HebrewDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hebrew Dates Demo - Powered by hdate")
        self.geometry("820x680")
        
        # Presets
        self.locations = {
            "Jerusalem": (31.778, 35.236, "Asia/Jerusalem", 750),
            "Tel Aviv": (32.085, 34.781, "Asia/Jerusalem", 20),
            "New York": (40.713, -74.006, "America/New_York", 10),
            "London": (51.507, -0.128, "Europe/London", 35),
            # add more...
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Date input
        ttk.Label(self, text="Gregorian Date:").pack(pady=5)
        self.date_entry = ttk.Entry(self)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack()
        
        # Location
        ttk.Label(self, text="Location:").pack(pady=5)
        self.loc_var = tk.StringVar(value="New York")
        loc_combo = ttk.Combobox(self, textvariable=self.loc_var, values=list(self.locations.keys()))
        loc_combo.pack()
        
        ttk.Button(self, text="Calculate", command=self.calculate).pack(pady=15)
        
        # Results area
        self.result_text = tk.Text(self, wrap=tk.WORD, height=30, font=("Consolas", 11))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calculate(self):
        try:
            gdate = date.fromisoformat(self.date_entry.get().strip())
            loc_name = self.loc_var.get()
            lat, lon, tz, elev = self.locations.get(loc_name, (31.778, 35.236, "Asia/Jerusalem", 750))
            
            loc = hdate.Location(name=loc_name, latitude=lat, longitude=lon,
                               timezone=tz, elevation=elev)
            
            h = hdate.HDateInfo(gdate)                    # Basic Hebrew date
            z = hdate.Zmanim(date=gdate, location=loc)   # Zmanim
            
            # Bar Mitzvah (simple +13 Hebrew years)
            bm_heb = h.hdate + hdate.HebrewDate(13, 0, 0)  # rough, you can refine
            
            output = f"""📅 RESULTS for {gdate}

Hebrew Date:
{h}

Zmanim ({loc_name}):
Sunrise:     {z.sunrise}
Sunset:      {z.sunset}
Nightfall:   {z.nightfall}   (or your preferred method)

Bar Mitzvah Date (approx +13 Hebrew years):
{bm_heb}

This demo runs 100% locally using the py-libhdate library.
"""
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, output)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
