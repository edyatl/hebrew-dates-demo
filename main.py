"""Entry point for the Hebrew Dates Demo application."""

import tkinter as tk

from hdate_demo_app import HebrewDemo

root = tk.Tk()
root.tk.call("tk", "scaling", 1.5)
root.destroy()


def run_app() -> None:
    """Entry point for the application."""
    app = HebrewDemo()
    app.mainloop()


if __name__ == "__main__":
    run_app()
