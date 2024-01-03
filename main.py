from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from tkinter import ttk

# Create a Tkinter window
window = tk.Tk()
window.title("Quilt Animator")

# Set the window size
window_width = 400
window_height = 500
window.geometry(f"{window_width}x{window_height}")

# Define a dictionary of presets
presets = {
    "Looking Glass Portrait": {"num_rows": 6, "num_columns": 8},
    "Looking Glass Portrait DBL": {"num_rows": 12, "num_columns": 16},
    # Add more presets here if needed
}

# Update the window to get the requested width and height
window.update_idletasks()

# Get the screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate the x and y coordinates for the window to be centered
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Set the window's position
window.geometry(f"+{x}+{y}")

# Define the dark mode theme colors
dark_mode_bg = "#333333"
dark_mode_fg = "#ffffff"
dark_mode_button_bg = "#555555"
dark_mode_button_fg = "black"

# Set the window background color
window.configure(bg=dark_mode_bg)

# Create a dark mode style for the elements
style = Style()
style.configure("TButton", background=dark_mode_button_bg, foreground=dark_mode_button_fg)
style.configure("TEntry", fieldbackground=dark_mode_bg, foreground="black")
style.configure("TLabel", background=dark_mode_bg, foreground=dark_mode_fg)

# Function to select the folder containing quilt images
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        select_button.configure(style="Green.TButton")  # Change button style to green
        folder_path_var.set(folder_path)  # Set the folder path in the variable

# Function to update num_rows and num_columns when a preset is selected
def update_preset(*args):
    preset_name = preset_var.get()
    if preset_name in presets:
        num_rows_var.set(presets[preset_name]["num_rows"])
        num_columns_var.set(presets[preset_name]["num_columns"])

# Create a dropdown box for selecting presets
preset_label = Label(window, text="Looking Glass Model:")
preset_label.pack(pady=(50, 0))
preset_var = tk.StringVar(window)
preset_var.set("Looking Glass Portrait")  # Set the default preset
preset_var.trace("w", update_preset)  # Call update_preset when the preset is selected
preset_combobox = Combobox(window, textvariable=preset_var, values=list(presets.keys()))
preset_combobox.pack()

# Create variables for num_rows and num_columns
num_rows_var = tk.IntVar(window, value=6)  # Default value
num_columns_var = tk.IntVar(window, value=8)  # Default value

# Function to process the quilt images
def process_quilt(folder_path):
    num_rows = num_rows_var.get()
    num_columns = num_columns_var.get()
    num_frames = num_rows * num_columns

    # Create a blank image to stitch the frames onto
    output_quilt = None

    # Get the user-specified file name and increment format
    file_name = file_name_var.get()
    increment_format = increment_format_var.get()

    # Get the selected file format from the drop-down menu
    file_format = file_format_var.get()

    # Update the self-updating label
    update_label(file_name, increment_format, file_format)
    window.update()

    # Check if all necessary variables are valid
    if not all([file_name, increment_format, file_format]):
        messagebox.showerror("Error", "Please enter valid values for all fields.")
        return

    # Create a progress bar
    progress_bar = Progressbar(window, orient="horizontal", length=250, mode="determinate")
    progress_bar.pack(pady=10)

    # Iterate over each tile (frame) sequentially
    for frame in range(num_frames):
        # Calculate the row and column for this frame
        row = frame // num_columns
        col = frame % num_columns

        # Construct the file path for the current tile
        frame_number = str(frame + 1).zfill(len(increment_format))
        quilt_image_path = os.path.join(folder_path, f"{file_name}{frame_number}.{file_format}")

        # Check if the image file exists
        if not os.path.exists(quilt_image_path):
            messagebox.showerror("Error", f"Image file for frame {frame + 1} not found.\nCheck your file name & format!")
            return

        quilt_image = Image.open(quilt_image_path)

        # Create output quilt with the same size as the input quilt
        if output_quilt is None:
            output_quilt = Image.new("RGB", quilt_image.size)

        # Calculate the coordinates for the current tile
        tile_x = quilt_image.width - ((col + 1) * quilt_image.width // num_columns)
        tile_y = row * quilt_image.height // num_rows
        tile_width = quilt_image.width // num_columns
        tile_height = quilt_image.height // num_rows

        # Extract the tile from the quilt image
        tile = quilt_image.crop((tile_x, tile_y, tile_x + tile_width, tile_y + tile_height))

        # Calculate the coordinates to stitch the tile onto the output quilt
        stitch_x = (num_columns - col - 1) * tile_width
        stitch_y = row * tile_height

        # Stitch the tile onto the output quilt
        output_quilt.paste(tile, (stitch_x, stitch_y))

        # Update the progress bar
        progress_bar["value"] = (frame + 1) / num_frames * 100
        window.update()
        window.update_idletasks()  # Update the window

    # Save the final stitched quilt
    save_path = os.path.join(folder_path, f"animated_quilt.{file_format}")
    output_quilt.save(save_path)

    # Close the progress bar
    progress_bar.destroy()
    os.startfile(folder_path)
    messagebox.showinfo("Quilt Animation", "Quilt animation generated!\nAnimated quilt saved in source folder.")
    # Close the progress bar
    progress_bar.destroy()


def update_label(*args):
    folder_path = folder_path_var.get()
    file_name = file_name_var.get()
    increment_format = increment_format_var.get()
    file_format = file_format_var.get()
    num_rows = num_rows_var.get()
    num_columns = num_columns_var.get()
    num_frames = num_rows * num_columns  # Calculate num_frames

    if all([file_name, increment_format, file_format, folder_path]):
        increment = int(increment_format)
        increment_format_zeros = "0" * (len(increment_format) - len(str(increment)))
        # Format the increment value with leading zeros
        increment_formatted = increment_format_zeros + str(increment)
        label_text = f"Will look for images:\n" \
                     f"{file_name}{increment_formatted}.{file_format}, " \
                     f"{file_name}{increment_format_zeros}{increment + 1}.{file_format}, etc.\n" \
                     f"In the directory:\n" \
                     f"{folder_path}\n" \
                     f"With: {num_rows} rows and {num_columns} columns\n" \
                     f"Total Frames: {num_frames} /image"  # Include num_frames
    else:
        label_text = "Please enter valid values for all fields, and ensure a folder is selected!"

    label.config(text=label_text)


def start_process():
    folder_path = folder_path_var.get()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder containing images.")
        return

    # Disable the start button
    start_button.configure(state="disabled")
    process_quilt(folder_path)
    # Enable the start button
    start_button.configure(state="normal")

# Create a button to select the folder containing quilt images
select_button = Button(window, text="Select Images Folder", command=select_folder)
select_button.pack(pady=(25, 0))

# Create a variable to store the folder path
folder_path_var = tk.StringVar()

# Create a label to display the selected folder path
folder_path_label = Label(window, textvariable=folder_path_var, wraplength=350)  # Adjust the wraplength value as needed
folder_path_label.pack(pady=(5, 0))

# Create a horizontal Separator widget to add a divider line
#horizontal_separator = ttk.Separator(window, orient='horizontal')
#horizontal_separator.pack(fill='x', padx=10, pady=20)

# Create an entry field for the file name
file_name_label = Label(window, text="File Name:")
file_name_label.pack()
file_name_var = tk.StringVar(window)
file_name_var.trace("w", update_label)  # Call the update_label function when the variable is modified
#file_name_var.set("image")  # Set a default value
file_name_entry = Entry(window, textvariable=file_name_var)
file_name_entry.pack()

def validate_increment_format(new_value):
    if new_value.isdigit() or new_value == "":
        return True
    else:
        return False

# Create an entry field for the increment format
increment_format_label = Label(window, text="Increment Format:")
increment_format_label.pack()
increment_format_var = tk.StringVar(window)
increment_format_var.trace("w", update_label)  # Call the update_label function when the variable is modified
increment_format_var.set("00")  # Set a default value for the increment format
increment_format_entry = Entry(window, textvariable=increment_format_var, validate="key",
                               validatecommand=(window.register(validate_increment_format), '%P'))
increment_format_entry.pack()

# Create a drop-down menu for the file format
file_format_label = Label(window, text="File Format:")
file_format_label.pack()
file_format_var = tk.StringVar(window)
file_format_var.trace("w", update_label)  # Call the update_label function when the variable is modified
file_format_var.set("png")
file_format_option_menu = OptionMenu(window, file_format_var, "png", "jpg", "jpeg", "png")
file_format_option_menu.pack()

# Create the self-updating label
label = Label(window)
label.pack(pady=10)

# Create a START button to initiate the quilt making process
start_button = Button(window, text="START", command=start_process)
start_button.pack(pady=10)

window.mainloop()