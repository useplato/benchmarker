import difflib
import json
import os
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BenchmarkViewer(tk.Tk):
    def __init__(self, initial_test_data: list[dict] = []):
        super().__init__()
        self.title("Benchmark Viewer")
        self.geometry("1024x768")
        self.test_data_dir = "test_data"

        self.create_widgets()
        self.test_data = []

        if len(initial_test_data) > 0:
            self.test_data = initial_test_data
            self.display_results()

        self.selected_test_case = None  # Track the selected test case

    def create_widgets(self):
        self.file_label = ttk.Label(self, text="Select JSON File:")
        self.file_label.pack(pady=10)

        self.file_dropdown = ttk.Combobox(self, state="readonly")
        self.file_dropdown.pack(pady=10)
        self.file_dropdown.bind("<<ComboboxSelected>>", self.load_data)

        self.load_json_files()

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for the test case dropdown and the diff button
        self.test_case_frame = ttk.Frame(self)
        self.test_case_frame.pack(pady=10)

        self.test_case_dropdown = ttk.Combobox(self.test_case_frame, state="readonly")
        self.test_case_dropdown.pack(side=tk.LEFT, padx=5)
        self.test_case_dropdown.bind("<<ComboboxSelected>>", self.on_test_select)

        self.diff_button = ttk.Button(
            self.test_case_frame, text="Show JSON Diff", command=self.show_json_diff
        )
        self.diff_button.pack(side=tk.LEFT, padx=5)

    def load_json_files(self):
        json_files = [f for f in os.listdir(self.test_data_dir) if f.endswith(".json")]
        self.file_dropdown["values"] = json_files

    def load_data(self, event):
        selected_file = self.file_dropdown.get()
        file_path = os.path.join(self.test_data_dir, selected_file)

        with open(file_path, "r") as f:
            self.test_data = json.load(f)

        self.display_results()

    def display_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        try:
            self.test_data = [test for test in self.test_data if test["completed"]]
        except KeyError:
            ttk.Label(self.results_frame, text="Invalid test data format").pack(pady=10)
            return

        if len(self.test_data) == 0:
            ttk.Label(self.results_frame, text="No completed tests found").pack(pady=10)
            return

        scores = [test["score"] for test in self.test_data]
        time_diffs = [test["time_diff"] for test in self.test_data]
        avg_score = sum(scores) / len(scores)
        avg_time_diff = sum(time_diffs) / len(time_diffs)

        avg_label = ttk.Label(
            self.results_frame,
            text=f"Average Score: {avg_score:.2f}, Average Time Diff: {avg_time_diff:.2f}",
        )
        avg_label.pack(pady=10)

        fig, ax = plt.subplots()
        bars = ax.bar(
            [test["name"] for test in self.test_data], scores, color="skyblue"
        )
        ax.set_title("Benchmark Scores")
        ax.set_xlabel("Test Name")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 100)

        def on_hover(event):
            for bar, time_diff in zip(bars, time_diffs):
                if bar.contains(event)[0]:
                    if not hasattr(on_hover, "annotation"):
                        on_hover.annotation = ax.annotate(
                            f"Time Diff: {time_diff:.2f}",
                            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center",
                            va="bottom",
                        )
                    else:
                        on_hover.annotation.set_text(
                            f"Time Diff: {time_diff:.2f} seconds"
                        )
                        on_hover.annotation.xy = (
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height(),
                        )
                    fig.canvas.draw_idle()
                    break
            else:
                if hasattr(on_hover, "annotation"):
                    on_hover.annotation.remove()
                    del on_hover.annotation
                    fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)

        canvas = FigureCanvasTkAgg(fig, master=self.results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Update the test case dropdown with test names
        self.test_case_dropdown["values"] = [test["name"] for test in self.test_data]
        self.test_case_dropdown.set("")  # Clear selection

    def on_test_select(self, event):
        selected_name = self.test_case_dropdown.get()
        for test in self.test_data:
            if test["name"] == selected_name:
                self.selected_test_case = test
                break

    def show_json_diff(self):
        if not self.selected_test_case:
            ttk.Label(self.results_frame, text="No test case selected").pack(pady=10)
            return

        apify_results = self.selected_test_case.get("apify_results", {})
        plato_results = self.selected_test_case.get("plato_results", {})

        diff_window = tk.Toplevel(self)
        diff_window.title("JSON Diff")

        left_frame = ttk.Frame(diff_window)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(diff_window)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        left_text = tk.Text(left_frame, wrap=tk.WORD)
        left_text.pack(fill=tk.BOTH, expand=True)

        right_text = tk.Text(right_frame, wrap=tk.WORD)
        right_text.pack(fill=tk.BOTH, expand=True)

        self.display_json_diff(left_text, right_text, apify_results, plato_results)

    def display_json_diff(self, left_text, right_text, apify_results, plato_results):
        apify_str = json.dumps(apify_results, indent=4).splitlines()
        plato_str = json.dumps(plato_results, indent=4).splitlines()

        diff = difflib.ndiff(apify_str, plato_str)

        for line in diff:
            if line.startswith("- "):
                left_text.insert(tk.END, line[2:] + "\n", "deletion")
            elif line.startswith("+ "):
                right_text.insert(tk.END, line[2:] + "\n", "addition")
            elif line.startswith("  "):
                left_text.insert(tk.END, line[2:] + "\n")
                right_text.insert(tk.END, line[2:] + "\n")

        left_text.tag_config("deletion", background="red", foreground="white")
        right_text.tag_config("addition", background="green", foreground="white")


if __name__ == "__main__":
    app = BenchmarkViewer()
    app.mainloop()
