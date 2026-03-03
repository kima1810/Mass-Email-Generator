import os
import pandas as pd
from tkinter import Tk, Label, Entry, Button, filedialog, Text, Checkbutton, IntVar, messagebox
from src.paths import get_token_path
from src.processor import process_contacts

def process_csv():
    subject = subject_entry.get()
    template = template_box.get("1.0", "end-1c")
    include_signature = signature.get()
    csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_path or not subject or not template:
        messagebox.showwarning("Missing Input", "Please fill in subject and template, then select a CSV file")
        return

    try:
        token_path = get_token_path()
        if not os.path.exists(token_path):
            messagebox.showinfo("Authentication Required", "You will now be redirected to your browser to login with Google.\n\nPlease complete the authentication and return to this application.")
        draft_count, failed_drafts = process_contacts(
            csv_path=csv_path,
            subject=subject,
            template=template,
            include_signature=bool(include_signature)
        )
        
        if failed_drafts:
            failed_list = '\n'.join(failed_drafts[:10])
            if len(failed_drafts) > 10:
                failed_list += f"\n... and {len(failed_drafts) - 10} more"
            messagebox.showwarning("Partially Complete", 
                f"Created {draft_count} drafts successfully.\n\n"
                f"Failed to create {len(failed_drafts)} drafts:\n{failed_list}")
        else:
            messagebox.showinfo("Success", f"Successfully created {draft_count} email drafts in your Gmail!")
        
    except FileNotFoundError:
        messagebox.showerror("Error", "credentials.json file not found")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", "CSV file is empty")
    except ValueError as error:
        messagebox.showerror("Error", str(error))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Frontend GUI
root = Tk()
root.title("Email Automation Assist")

Label(root, text="Subject:").pack()
subject_entry = Entry(root, width=50)
subject_entry.pack()

Label(root, text="Template (use {{first_name}}):").pack()
template_box = Text(root, height=10, width=50)
template_box.pack()

signature = IntVar()
Checkbutton(root, text="Include Signature", variable=signature).pack()

Button(root, text="Create Drafts", command=process_csv).pack()

root.mainloop()
