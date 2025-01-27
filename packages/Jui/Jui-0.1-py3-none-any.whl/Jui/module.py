"""                                               PRIVATE USE AND DERIVATIVE LICENSE AGREEMENT 

        By using this software (the "Software"), you (the "User") agree to the following terms:  

1. Grant of License:  
    The Software is licensed to you for personal and non-commercial purposes, as well as for incorporation into your own projects, whether for private or public release.  

2. Permitted Use:  
    - You may use the Software as part of a larger project and publish your program, provided you include appropriate attribution to the original author (the "Licensor").  
    - You may modify the Software as needed for your project but must clearly indicate any changes made to the original work.  

3. Restrictions:  
     - You may not sell, lease, or sublicense the Software as a standalone product.  
     - If using the Software in a commercial project, prior written permission from the Licensor is required.(Credit,Cr)
     - You may not change or (copy a part of) the original form of the Software.  

4. Attribution Requirement:  
      Any published program or project that includes the Software, in whole or in part, must include the following notice:  
      *"This project includes software developed by [Jynoqtra], © 2025. Used with permission under the Private Use and Derivative License Agreement."*  

5. No Warranty:  
      The Software is provided "as is," without any express or implied warranties. The Licensor is not responsible for any damage or loss resulting from the use of the Software.  

6. Ownership:  
      All intellectual property rights, including but not limited to copyright and trademark rights, in the Software remain with the Licensor.  

7. Termination:  
     This license will terminate immediately if you breach any of the terms and conditions set forth in this agreement.  

8. Governing Law:  
      This agreement shall be governed by the laws of [the applicable jurisdiction, without regard to its conflict of law principles].  

9. Limitation of Liability:  
     In no event shall the Licensor be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, incurred by you or any third party, whether in an action in contract, tort (including but not limited to negligence), or otherwise, even if the Licensor has been advised of the possibility of such damages.  

            Effective Date: [2025]  

            © 2025 [Jynoqtra]
"""

import tkinter as tk
from tkinter import ttk
def show_error_messagebox(message):
    from tkinter import messagebox
    messagebox.showerror("Error", message)
class Jwin:
    def __init__(self, layout, widgets_config, user_callbacks=None):
        self.root = tk.Tk()
        self.root.title("Dynamic User-Controlled Window")
        self.widgets = {}
        self.user_callbacks = user_callbacks or {}
        self.root.geometry("")
        self.root.grid_propagate(True)
        self.layout_lines = [line.strip() for line in layout.strip().split("\n") if line.strip()]
        self.num_rows = len(self.layout_lines)
        self.num_cols = max(len(line) for line in self.layout_lines)
        for r in range(self.num_rows):
            self.root.grid_rowconfigure(r, weight=1)
        for c in range(self.num_cols):
            self.root.grid_columnconfigure(c, weight=1)
        self._create_widgets(widgets_config)
        self._create_layout()

    def _create_widgets(self, widgets_config):
        for widget_config in widgets_config:
            row, col = widget_config['position']
            widget_type = widget_config['type']
            options = widget_config.get('options', {})

            widget = self._create_widget(widget_type, options)
            if isinstance(widget, list):
                for w in widget:
                    w.grid(row=row, column=col, padx=5, pady=5)
            else:
                widget.grid(row=row, column=col, padx=5, pady=5)

            widget_id = options.get("id")
            if widget_id:
                self.widgets[widget_id] = widget

    def _create_widget(self, widget_type, options):
        widget = None
        if widget_type == "button":
            widget = tk.Button(self.root, text=options.get("text", "Button"),
                               command=lambda: self._execute_callback(options.get("id")))
        elif widget_type == "label":
            widget = tk.Label(self.root, text=options.get("text", "Label"))
        elif widget_type == "input":
            widget = tk.Entry(self.root)
        elif widget_type == "password":
            widget = tk.Entry(self.root, show="*")
        elif widget_type == "checkbox":
            var = tk.BooleanVar()
            widget = tk.Checkbutton(self.root, text=options.get("text", "Checkbox"), variable=var)
        elif widget_type == "dropdown":
            values = options.get("values", [])
            widget = ttk.Combobox(self.root, values=values)
        elif widget_type == "radio":
            var = tk.StringVar()
            widget = []
            for idx, text in enumerate(options.get("values", [])):
                radio_button = tk.Radiobutton(self.root, text=text, variable=var, value=text)
                widget.append(radio_button)
        elif widget_type == "textarea":
            widget = tk.Text(self.root, height=5, width=20)
        elif widget_type == "slider":
            min_val = options.get("min", 0)
            max_val = options.get("max", 100)
            widget = tk.Scale(self.root, from_=min_val, to=max_val)
        elif widget_type == "listbox":
            widget = tk.Listbox(self.root, selectmode=tk.SINGLE)
            for item in options.get("values", []):
                widget.insert(tk.END, item)
        elif widget_type == "canvas":
            widget = tk.Canvas(self.root, width=options.get("width", 200), height=options.get("height", 100))
        elif widget_type == "progressbar":
            widget = ttk.Progressbar(self.root, length=200, mode=options.get("mode", "determinate"))
        elif widget_type == "spinbox":
            min_val = options.get("min", 0)
            max_val = options.get("max", 100)
            widget = tk.Spinbox(self.root, from_=min_val, to=max_val)
        else:
            widget = tk.Label(self.root, text=f"Unsupported: {widget_type}")
        return widget

    def _create_layout(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell_content = self.layout_lines[r][c]
                if cell_content == ' ':
                    continue

    def _execute_callback(self, widget_id):
        if widget_id and widget_id in self.user_callbacks:
            callback = self.user_callbacks[widget_id]
            callback()

    def get_value(self, widget_id):
        widget = self.widgets.get(widget_id)
        if isinstance(widget, tk.Entry):
            return widget.get()
        elif isinstance(widget, ttk.Combobox):
            return widget.get()
        elif isinstance(widget, tk.BooleanVar):
            return widget.get()
        elif isinstance(widget, tk.StringVar):
            return widget.get()
        elif isinstance(widget, tk.Text):
            return widget.get("1.0", tk.END)
        elif isinstance(widget, tk.Scale):
            return widget.get()
        elif isinstance(widget, tk.Listbox):
            return widget.get(tk.ACTIVE)
        elif isinstance(widget, tk.Spinbox):
            return widget.get()
        elif isinstance(widget, ttk.Progressbar):
            return widget['value']
        return None

    def run(self):
        self.root.mainloop()
def JynPopMod():print("Click to see about JynPopMod https://github.com/Jynoqtra/JynPopMod that made by Jynoqtra")
def switch_case(_v, _c, d=None): return _c.get(_v, d)() if callable(_c.get(_v, d)) else _c.get(_v, d)
def pop(message, title="Information"):tk.Tk().withdraw();from tkinter import messagebox;messagebox.showinfo(title, message)
def popinp(_p, _t="Input"):from tkinter import simpledialog;return simpledialog.askstring(_t, _p) or None
def popp(_a, _b): return _a + _b
def pop_with_image(_m, _img_path, _t="Information"):from tkinter import messagebox;_img = tk.PhotoImage(file=_img_path); tk.Tk().withdraw(); messagebox.showinfo(_t, _m, _icon=_img)
def set_theme(root, theme="light"): [root.configure(bg="black") for widget in root.winfo_children()] if theme == "dark" else [root.configure(bg="white") for widget in root.winfo_children()]
def pop_switch(c, d=None, n="User"):option = popinp("Select an option:", title=n);result = switch_case(option, c, d);pop(f"Selected: {result}", title="Result")
def track_interaction(widget_name, event_type):print(f"Interaction with {widget_name}: {event_type}")
def main_win():return tk.Tk()
def set_window_size(_root, width=300, height=200):_root.geometry(f"{width}x{height}");track_interaction("window", "size set")
def set_window_title(_root, _title):_root.title(_title);track_interaction("window", "title set")
def set_window_icon(_root, _icon_path):_root.iconbitmap(_icon_path);track_interaction("window", "icon set")
def minimize_window(_root):_root.iconify();track_interaction("window", "minimized")
def maximize_window(_root):_root.state('zoomed');track_interaction("window", "maximized")
def destroy_window(_root):_root.destroy();track_interaction("window", "destroyed")
def center_window(_root, width=300, height=200):_root.geometry(f"{width}x{height}+{(_root.winfo_screenwidth()//2)-(width//2)}+{(_root.winfo_screenheight()//2)-(height//2)}");track_interaction("window", "centered")
def set_window_bg_color(_root, color):_root.configure(bg=color);track_interaction("window", f"background color set to {color}")
def set_window_always_on_top(_root):_root.attributes("-topmost", True);track_interaction("window", "always on top set")
def remove_window_always_on_top(_root):_root.attributes("-topmost", False);track_interaction("window", "always on top removed")
def set_window_opacity(_root, opacity):_root.attributes("-alpha", opacity);track_interaction("window", f"opacity set to {opacity}")
def hide_window(_root):_root.withdraw();track_interaction("window", "hidden")
def show_window(_root):_root.deiconify();track_interaction("window", "shown")
def set_window_fixed_size(_root):_root.resizable(False, False);track_interaction("window", "fixed size set")
def enable_window_resizing(_root):_root.resizable(True, True);track_interaction("window", "resizing enabled")
def set_window_bg_image(_root, image_path):img = tk.PhotoImage(file=image_path);label = tk.Label(_root, image=img);label.place(relwidth=1, relheight=1);label.image = img;track_interaction("window", f"background image set from {image_path}")
def change_window_icon(_root, icon_path):_root.iconbitmap(icon_path);track_interaction("window", f"icon changed to {icon_path}")
def create_label(_root, _text):label = tk.Label(_root, text=_text);label.pack();label.bind("<Button-1>", lambda event: track_interaction("label", "clicked"));track_interaction("label", "created");return label
def create_button(_root, _text, _command):button = tk.Button(_root, text=_text, command=lambda: [track_interaction("button", "clicked"), _command()]);button.pack();track_interaction("button", "created");return button
def create_entry(_root):entry = tk.Entry(_root);entry.pack();entry.bind("<FocusIn>", lambda event: track_interaction("entry", "focused"));entry.bind("<FocusOut>", lambda event: track_interaction("entry", "unfocused"));track_interaction("entry", "created");return entry
def create_text_widget(_root, _width=30, _height=10):text_widget = tk.Text(_root, width=_width, height=_height);text_widget.pack();text_widget.bind("<KeyRelease>", lambda event: track_interaction("text widget", f"key released: {event.keysym}"));track_interaction("text widget", "created");return text_widget
def create_checkbox(_root, _text, _command):checkbox = tk.Checkbutton(_root, text=_text, command=lambda: [track_interaction("checkbox", "clicked"), _command()]);checkbox.pack();track_interaction("checkbox", "created");return checkbox
def create_radio_buttons(_root, _options, _command):
    var = tk.StringVar()
    for option in _options:radio_button = tk.Radiobutton(_root, text=option, variable=var, value=option, command=lambda: [track_interaction("radio button", "selected"), _command()]);radio_button.pack();track_interaction("radio buttons", "created");return var
def create_dropdown(_root, _options, _command):var = tk.StringVar();dropdown = tk.OptionMenu(_root, var, * _options, command=lambda _: [track_interaction("dropdown", "selected"), _command()]);dropdown.pack();track_interaction("dropdown", "created");return var
def create_listbox(_root, _items, _command):
    listbox = tk.Listbox(_root)
    for item in _items:listbox.insert(tk.END, item)
    listbox.pack();listbox.bind("<ButtonRelease-1>", lambda event: track_interaction("listbox", "item selected"));track_interaction("listbox", "created");return listbox
def create_canvas(_root, _width=400, _height=300):canvas = tk.Canvas(_root, width=_width, height=_height);canvas.pack();track_interaction("canvas", "created");return canvas
def create_progress_bar(_root):progress_bar = tk.Progressbar(_root, length=200, mode='indeterminate');progress_bar.pack();track_interaction("progress bar", "created");return progress_bar
def create_scrollbar(_root, _widget):scrollbar = tk.Scrollbar(_root, orient=tk.VERTICAL, command=_widget.yview);_widget.config(yscrollcommand=scrollbar.set);scrollbar.pack(side=tk.RIGHT, fill=tk.Y);track_interaction("scrollbar", "created");return scrollbar
def create_frame(_root):frame = tk.Frame(_root);frame.pack();track_interaction("frame", "created");return frame
def create_menu_bar(_root):menu_bar = tk.Menu(_root);_root.config(menu=menu_bar);track_interaction("menu bar", "created");return menu_bar
def bind_key_press(_root, _key, _function): _root.bind(_key, _function)
def bind_mouse_click(_root, _function): _root.bind("<Button-1>", _function)
def bind_mouse_enter(_widget, _function): _widget.bind("<Enter>", _function)
def bind_mouse_leave(_widget, _function): _widget.bind("<Leave>", _function)
def bind_mouse_wheel(_root, _function): _root.bind("<MouseWheel>", _function)
def trigger_event(_widget, _event): _widget.event_generate(_event)
def update_label_text(_label, _new_text): _label.config(text=_new_text)
def update_entry_text(_entry, _new_text): _entry.delete(0, tk.END); _entry.insert(0, _new_text)
def update_text_widget(_text_widget, _new_content): _text_widget.delete(1.0, tk.END); _text_widget.insert(tk.END, _new_content)
def update_checkbox_state(_checkbox, _state): _checkbox.select() if _state else _checkbox.deselect()
def update_radio_selection(_var, _value): _var.set(_value)
def update_progress_bar(_progress, _value): _progress["value"] = _value
def disable_widget(_widget): _widget.config(state=tk.DISABLED)
def enable_widget(_widget): _widget.config(state=tk.NORMAL)
def change_widget_bg_color(_widget, _color): _widget.config(bg=_color)
def change_widget_fg_color(_widget, _color): _widget.config(fg=_color)
def change_widget_font(_widget, _font_name, _font_size): _widget.config(font=(_font_name, _font_size))
def add_widget_border(_widget, _border_width=2, _border_color="black"): _widget.config(borderwidth=_border_width, relief="solid", highlightbackground=_border_color)
def pack_with_padding(_widget, _padx=10, _pady=10): _widget.pack(padx=_padx, pady=_pady)
def grid_widget(_widget, _row, _col, _rowspan=1, _columnspan=1): _widget.grid(row=_row, column=_col, rowspan=_rowspan, columnspan=_columnspan)
def place_widget(_widget, _x, _y): _widget.place(x=_x, y=_y)
def set_grid_widget_sticky(_widget, _sticky="nsew"): _widget.grid(sticky=_sticky)
def show_info_messagebox(_message):from tkinter import messagebox; messagebox.showinfo("Information", _message)
def show_error_messagebox(_message):from tkinter import messagebox;messagebox.showerror("Error", _message)
def show_warning_messagebox(_message):from tkinter import messagebox;messagebox.showwarning("Warning", _message)
def ask_yes_no_question(_question):from tkinter import messagebox;return messagebox.askyesno("Question", _question)
def ask_for_input(_prompt):from tkinter import simpledialog;return simpledialog.askstring("Input", _prompt)
def show_messagebox_with_image(_message, _image_path):from tkinter import messagebox;_img = tk.PhotoImage(file=_image_path); messagebox.showinfo("Information", _message, icon=_img)
def show_confirmation_messagebox(_message):from tkinter import messagebox;return messagebox.askokcancel("Confirmation", _message)
def create_modal_dialog(_root, _message): dialog = tk.Toplevel(_root); dialog.title("Modal Dialog"); tk.Label(dialog, text=_message).pack(); tk.Button(dialog, text="OK", command=dialog.destroy).pack()
def prn(pnt):return print(pnt)
def delayed_pop(message, delay=3):import time;time.sleep(delay);pop(message)
def create_checkbox_widget(root, text, default=False):
    checkbox = create_checkbox(root, text, command=lambda: pop(f"Selected: {checkbox.isChecked()}"))
    if default:checkbox.setChecked(True)
def validate_input(prompt, valid_type, error_message="Invalid input!"):
    while True:
        user_input = popinp(prompt)
        if valid_type == "int" and user_input.isdigit():return int(user_input)
        elif valid_type == "float" and is_valid_float(user_input):return float(user_input)
        else:pop(error_message)
def is_valid_float(value):
    try:float(value);return True
    except ValueError:return False
def depop(message, delay=3):import time;time.sleep(delay);pop(message)
def pfk(task_name, progress, total):progress_percentage = (progress / total) * 100;message = f"{task_name} - Progress: {progress_percentage:.2f}%";pop(message)
def so(options, prompt="Select an option:"):selection = pop_switch(options, default="Invalid selection", name=prompt);return selection
def msgbox(message): pop(message)
def aynq(question):response = pop_switch({"Yes": True, "No": False}, default=False, name=question) ;return response
def show_warning_messagebox(message): show_warning_messagebox(message)
def bind_key_press(root, key, function): bind_key_press(root, key, function)
def bind_mouse_click(root, function):bind_mouse_click(root, function)
def bind_mouse_enter(widget, function):bind_mouse_enter(widget, function)
def bind_mouse_leave(widget, function):bind_mouse_leave(widget, function)
def bind_mouse_wheel(root, function):bind_mouse_wheel(root, function)
def set_window_size(_root, width=300, height=200):
    _root.geometry(f"{width}x{height}")
    track_interaction("window", "size set")
def animate_widget(widget, start_x, start_y, end_x, end_y, duration=1000):
    import time
    for t in range(duration):progress = t / duration;new_x = start_x + (end_x - start_x) * progress;new_y = start_y + (end_y - start_y) * progress;widget.place(x=new_x, y=new_y);time.sleep(0.01)