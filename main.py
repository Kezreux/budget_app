"""Simple family budget GUI application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from calendar import month_name

from database import BudgetDB


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Family Budget")
        self.geometry("500x400")
        self.db = BudgetDB()

        today = date.today()
        self.current_year = today.year
        self.current_month = today.month

        self.create_widgets()
        self.refresh()

    def create_widgets(self) -> None:
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)

        prev_btn = ttk.Button(control_frame, text="< Prev", command=self.prev_month)
        prev_btn.pack(side="left")

        self.title_label = ttk.Label(control_frame, text="")
        self.title_label.pack(side="left", padx=10)

        next_btn = ttk.Button(control_frame, text="Next >", command=self.next_month)
        next_btn.pack(side="left")

        summary_frame = ttk.Frame(self)
        summary_frame.pack(pady=10)
        self.income_var = tk.StringVar()
        self.expense_var = tk.StringVar()
        self.balance_var = tk.StringVar()
        ttk.Label(summary_frame, textvariable=self.income_var).pack()
        ttk.Label(summary_frame, textvariable=self.expense_var).pack()
        ttk.Label(summary_frame, textvariable=self.balance_var).pack()

        form = ttk.Frame(self)
        form.pack(pady=10)
        ttk.Label(form, text="Amount:").grid(row=0, column=0)
        self.amount_entry = ttk.Entry(form)
        self.amount_entry.grid(row=0, column=1)

        ttk.Label(form, text="Type:").grid(row=1, column=0)
        self.type_var = tk.StringVar(value="income")
        ttk.OptionMenu(form, self.type_var, "income", "income", "expense").grid(row=1, column=1)

        ttk.Label(form, text="Description:").grid(row=2, column=0)
        self.desc_entry = ttk.Entry(form)
        self.desc_entry.grid(row=2, column=1)

        add_btn = ttk.Button(form, text="Add", command=self.add_transaction)
        add_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.transaction_list = tk.Listbox(self)
        self.transaction_list.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh(self) -> None:
        month_name_str = month_name[self.current_month]
        self.title_label.config(text=f"{month_name_str} {self.current_year}")
        summary = self.db.get_month_summary(self.current_year, self.current_month)
        income = summary.get("income", 0)
        expense = summary.get("expense", 0)
        self.income_var.set(f"Total income: {income:.2f}")
        self.expense_var.set(f"Total expenses: {expense:.2f}")
        self.balance_var.set(f"Balance: {income - expense:.2f}")

        self.transaction_list.delete(0, tk.END)
        for t_date, t_type, amount, desc in self.db.get_month_transactions(self.current_year, self.current_month):
            when = datetime.fromisoformat(t_date).strftime("%Y-%m-%d")
            self.transaction_list.insert(tk.END, f"{when} - {t_type}: {amount:.2f} ({desc})")

    def add_transaction(self) -> None:
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter a valid number.")
            return
        t_type = self.type_var.get()
        desc = self.desc_entry.get()
        self.db.add_transaction(date.today(), t_type, amount, desc)
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.refresh()

    def prev_month(self) -> None:
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh()

    def next_month(self) -> None:
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh()

    def on_close(self) -> None:
        self.db.close()
        self.destroy()


def main() -> None:
    app = BudgetApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
