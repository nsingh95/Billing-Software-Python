import tkinter as tk
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from datetime import datetime
import win32api
import win32print
import os

class BillGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Bill Generator")
        self.root.geometry("700x500")  # Adjusted size for landscape orientation

        # Fixed color scheme
        self.colors = {
            'background': '#f0f8ff',  # Alice Blue
            'label': '#000000',       # Black
            'entry': '#ffffff',       # White
            'button': '#4682b4',      # Steel Blue
            'text': '#000000'         # Black
        }

        self.customer_name = tk.StringVar()
        self.phone_number = tk.StringVar()
        self.item_name = tk.StringVar()
        self.item_quantity = tk.IntVar()
        self.item_price = tk.DoubleVar()
        self.items = []

        self.create_widgets()

    def create_widgets(self):
        # Set background color for the root window
        self.root.configure(bg=self.colors['background'])

        # Main Heading
        self.create_label("B.M.SOLUTION", 20, "bold", row=0, colspan=2)
        self.create_label("Gurhatta, Patna- 8", 14, "bold", row=1, colspan=2)
        self.create_label("9934007606", 14, "bold", row=2, colspan=2)

        # Labels and Entry fields in a grid
        self.create_entry("Customer Name", self.customer_name, row=3)
        self.create_entry("Phone Number", self.phone_number, row=4)
        self.create_entry("Item Name", self.item_name, row=5)
        self.create_entry("Item Quantity", self.item_quantity, row=6)
        self.create_entry("Item Price", self.item_price, row=7)

        # Buttons centered
        button_frame = tk.Frame(self.root, bg=self.colors['background'])
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        self.create_button(button_frame, "Add Item", self.add_item)
        self.create_button(button_frame, "Generate Bill", self.generate_bill)
        self.create_button(button_frame, "Save and Print Bill", self.save_and_print_bill)
        self.create_button(button_frame, "Clear", self.clear_entries)
        self.create_button(button_frame, "Save PDF", self.save_pdf)

        # Landscape-oriented text box
        self.bill_area = tk.Text(self.root, height=15, width=90, bg=self.colors['entry'], fg=self.colors['text'], font=("Arial", 12))
        self.bill_area.grid(row=9, column=0, columnspan=2, pady=10, padx=10)

    def create_label(self, text, size, weight, row, colspan=1):
        tk.Label(self.root, text=text, font=("Arial", size, weight), fg=self.colors['text'], bg=self.colors['background']).grid(row=row, column=0, columnspan=colspan, pady=5, padx=10)

    def create_entry(self, label_text, textvariable, row):
        tk.Label(self.root, text=label_text, font=("Arial", 12, "bold"), fg=self.colors['label'], bg=self.colors['background']).grid(row=row, column=0, pady=5, padx=10, sticky='E')
        tk.Entry(self.root, textvariable=textvariable, bg=self.colors['entry'], fg=self.colors['text'], font=("Arial", 12)).grid(row=row, column=1, pady=5, padx=10, sticky='W')

    def create_button(self, parent, text, command):
        tk.Button(parent, text=text, command=command, bg=self.colors['button'], fg=self.colors['text'], font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

    def add_item(self):
        item = self.item_name.get()
        quantity = self.item_quantity.get()
        price = self.item_price.get()
        if item and quantity > 0 and price > 0:
            self.items.append((item, quantity, price))
            self.item_name.set("")
            self.item_quantity.set(0)
            self.item_price.set(0.0)
            self.generate_bill()  # Automatically generate bill after adding item
            messagebox.showinfo("Info", f"Added item: {item} (x{quantity}) - {price:.2f} each")
        else:
            messagebox.showwarning("Warning", "Item name, quantity, and price must be provided")

    def generate_bill(self):
        if not self.customer_name.get() or not self.phone_number.get():
            messagebox.showwarning("Warning", "Customer name and phone number must be provided")
            return

        total_price = sum(quantity * price for _, quantity, price in self.items)
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.bill_area.delete(1.0, tk.END)
        self.bill_area.insert(tk.END, f"Customer Name: {self.customer_name.get()}\n")
        self.bill_area.insert(tk.END, f"Phone Number: {self.phone_number.get()}\n")
        self.bill_area.insert(tk.END, f"Date & Time: {current_datetime}\n\n")
        self.bill_area.insert(tk.END, "{:<20} {:<7} {:<7} {:<7}\n".format("Item", "Quantity", "Price", "Total"))
        self.bill_area.insert(tk.END, "-"*60 + "\n")
        for item, quantity, price in self.items:
            total_item_price = quantity * price
            self.bill_area.insert(tk.END, "{:<20} {:<7} {:<7} {:<7}\n".format(item, quantity, f"{price:.2f}", f"{total_item_price:.2f}"))
        self.bill_area.insert(tk.END, "-"*60 + "\n")
        self.bill_area.insert(tk.END, f"{'Total Price:':<30} {total_price:.2f}\n")

    def save_pdf(self):
        file_name = self.save_bill_as_pdf()  # Save and get the file name
        if file_name:
            messagebox.showinfo("Info", f"PDF saved as {file_name}")

    def save_bill_as_pdf(self):
        if not self.customer_name.get() or not self.phone_number.get():
            messagebox.showwarning("Warning", "Customer name and phone number must be provided")
            return

        # Prepare text lines
        lines = self.prepare_pdf_lines()

        # Fixed width of 58mm (2.28 inches), estimate height based on number of lines
        width = 58 * 0.03937 * inch  # Convert mm to inches
        line_height = 0.2 * inch  # Approximate height per line
        height = len(lines) * line_height + 1 * inch  # Add extra height for margin

        file_name = f"{self.customer_name.get()}_{self.phone_number.get()}.pdf"
        c = canvas.Canvas(file_name, pagesize=(width, height))

        # Draw heading and other text
        self.draw_heading_and_text(c, width, height, line_height)

        # Draw the watermark
        c.setFont("Helvetica", 50)
        c.setFillColorRGB(0.8, 0.8, 0.8, alpha=0.3)  # Light gray with transparency
        c.rotate(45)
        c.drawString(width / 4, -height / 2, "")
        c.rotate(-45)  # Reset rotation

        c.save()
        return file_name  # Return the file name for printing

    def prepare_pdf_lines(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"Customer Name: {self.customer_name.get()}",
            f"Phone Number: {self.phone_number.get()}",
            f"Date & Time: {current_datetime}",
            "",
            "{:<20} {:<7} {:<7} {:<7}".format("Item", "Quantity", "Price", "Total"),
            "-" * 60
        ]

        for item, quantity, price in self.items:
            total_item_price = quantity * price
            lines.append("{:<20} {:<7} {:<7} {:<7}".format(item, quantity, f"{price:.2f}", f"{total_item_price:.2f}"))

        lines.append("-" * 60)
        total_price = sum(quantity * price for _, quantity, price in self.items)
        lines.append(f"{'Total Price:':<40} {total_price:.2f}")
        lines.append("")  # Spacer
        lines.append("Thank You :) Visit Again ;)")  # Footer

        return lines

    def draw_heading_and_text(self, c, width, height, line_height):
        # Define font size for the heading
        heading_font_size = 12
        c.setFont("Helvetica-Bold", heading_font_size)

        # Draw the heading in the center
        heading_text = "B.M.SOLUTION"
        heading_width = c.stringWidth(heading_text, "Helvetica-Bold", heading_font_size)
        c.drawString((width - heading_width) / 2, height - line_height, heading_text)

        # Draw the subheading in the center
        subheading_font_size = 10
        c.setFont("Helvetica-Bold", subheading_font_size)
        subheading_text = "Gurhatta, Patna-8"
        subheading_width = c.stringWidth(subheading_text, "Helvetica-Bold", subheading_font_size)
        c.drawString((width - subheading_width) / 2, height - 2 * line_height, subheading_text)

        # Draw the phone number in the center
        phone_font_size = 10
        c.setFont("Helvetica-Bold", phone_font_size)
        phone_text = "9934007606"
        phone_width = c.stringWidth(phone_text, "Helvetica-Bold", phone_font_size)
        c.drawString((width - phone_width) / 2, height - 3 * line_height, phone_text)

        # Define font size for the rest of the text
        font_size = 8
        c.setFont("Helvetica", font_size)

        # Draw the rest of the text with fixed width and dynamic height
        y_position = height - 4 * line_height  # Adjusted for heading and subheading height
        for line in self.prepare_pdf_lines():
            c.drawString(0.1 * inch, y_position, line)  # Start 0.1 inch from the left
            y_position -= line_height  # Move down for the next line

    def save_and_print_bill(self):
        file_name = self.save_bill_as_pdf()
        if file_name:
            self.print_pdf(file_name)

    def print_pdf(self, file_name):
        try:
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(
                0,
                "print",
                file_name,
                f'/d:"{printer_name}"',
                ".",
                0
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print the document: {e}")

    def clear_entries(self):
        self.customer_name.set("")
        self.phone_number.set("")
        self.item_name.set("")
        self.item_quantity.set(0)
        self.item_price.set(0.0)
        self.items = []
        self.bill_area.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BillGenerator(root)
    root.mainloop()
