import heapq
import os
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle

# ------------------ Node ------------------ #
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

# ------------------ Huffman Core ------------------ #
def build_frequency(text):
    return Counter(text)

def build_huffman_tree(freq_dict):
    heap = [Node(char, freq) for char, freq in freq_dict.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        print(merged)
        merged.left = left
        print(left);
        merged.right = right
        print(right);
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def generate_codes(root):
    codes = {}
    def helper(node, code):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = code
        helper(node.left, code + "0")
        helper(node.right, code + "1")
    helper(root, "")
    return codes

def encode(text, codes):
    return ''.join(codes[char] for char in text)

def decode(encoded_text, root):
    result = ""
    current = root
    for bit in encoded_text:
        current = current.left if bit == '0' else current.right
        if current.char is not None:
            result += current.char
            current = root
    return result

# ------------------ GUI Class ------------------ #
class HuffmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman Compression & Decompression")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f8ff")

        self.codes = {}
        self.huffman_root = None
        self.encoded_text = ""
        self.original_text = ""
        self.original_file_path = ""

        # Title
        title = tk.Label(root, text="📦 Huffman Compression Tool", font=("Helvetica", 20, "bold"), bg="#f0f8ff", fg="#003366")
        title.pack(pady=10)

        # Buttons
        button_frame = tk.Frame(root, bg="#f0f8ff")
        button_frame.pack(pady=5)

        self.load_btn = tk.Button(button_frame, text="📂 Load TXT", command=self.load_file, font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10)
        self.load_btn.grid(row=0, column=0, padx=10)

        self.compress_btn = tk.Button(button_frame, text="🗜️ Compress", command=self.compress, font=("Helvetica", 12), bg="#2196F3", fg="white", padx=10)
        self.compress_btn.grid(row=0, column=1, padx=10)

        self.save_btn = tk.Button(button_frame, text="💾 Save BIN", command=self.save_compressed, font=("Helvetica", 12), bg="#673AB7", fg="white", padx=10)
        self.save_btn.grid(row=0, column=2, padx=10)

        self.load_compressed_btn = tk.Button(button_frame, text="📂 Load BIN", command=self.load_compressed, font=("Helvetica", 12), bg="#009688", fg="white", padx=10)
        self.load_compressed_btn.grid(row=0, column=3, padx=10)

        self.decompress_btn = tk.Button(button_frame, text="🔓 Decompress", command=self.decompress, font=("Helvetica", 12), bg="#FF9800", fg="white", padx=10)
        self.decompress_btn.grid(row=0, column=4, padx=10)

        # File size label
        self.size_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f8ff", fg="#333")
        self.size_label.pack(pady=5)

        # Output Box
        label_output = tk.Label(root, text="🔍 Output Preview", font=("Helvetica", 14, "bold"), bg="#f0f8ff", anchor="w")
        label_output.pack(padx=20, anchor="w")

        self.output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12, font=("Consolas", 11), bg="white")
        self.output_box.pack(padx=20, pady=5, fill="both", expand=True)

        # Graph
        label_graph = tk.Label(root, text="📊 Character Frequency Graph", font=("Helvetica", 14, "bold"), bg="#f0f8ff", anchor="w")
        label_graph.pack(padx=20, pady=(10, 0), anchor="w")

        self.figure = Figure(figsize=(7, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding='utf-8') as file:
                self.original_text = file.read()
                self.original_file_path = file_path

            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(tk.END, f"✅ Loaded File:\n{self.original_text[:500]}...\n\n")
            self.encoded_text = ""
            self.huffman_root = None
            self.update_graph(self.original_text)
            self.show_file_sizes()

    def compress(self):
        if not self.original_text:
            messagebox.showwarning("No File", "Please load a text file first.")
            return

        freq = build_frequency(self.original_text)
        self.huffman_root = build_huffman_tree(freq)
        self.codes = generate_codes(self.huffman_root)
        self.encoded_text = encode(self.original_text, self.codes)

        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, f"📦 Compressed Bits (first 500):\n{self.encoded_text[:500]}...\n\n")
        self.output_box.insert(tk.END, f"📊 Huffman Codes:\n{self.codes}\n")

        self.update_graph(self.original_text)
        self.show_file_sizes()

    def save_compressed(self):
        if not self.encoded_text or not self.huffman_root:
            messagebox.showerror("Error", "No compressed data to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary Files", "*.bin")])
        if file_path:
            with open(file_path, "wb") as file:
                pickle.dump((self.encoded_text, self.huffman_root), file)
            messagebox.showinfo("Success", "Compressed data saved successfully!")

    def load_compressed(self):
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if file_path:
            with open(file_path, "rb") as file:
                self.encoded_text, self.huffman_root = pickle.load(file)

            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(tk.END, "📂 Compressed file loaded.\nClick 'Decompress' to view the content.")

    def decompress(self):
        if not self.encoded_text or not self.huffman_root:
            messagebox.showwarning("No Compression", "No compressed data found.")
            return

        decoded_text = decode(self.encoded_text, self.huffman_root)
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, f"🔓 Decompressed Text:\n{decoded_text[:1000]}...\n\n")

        self.update_graph(decoded_text)

    def show_file_sizes(self):
        if not self.original_text:
            return
        original_size = len(self.original_text.encode('utf-8'))
        compressed_size = len(self.encoded_text) // 8 if self.encoded_text else 0

        self.size_label.config(text=f"📏 Original Size: {original_size} bytes | 📉 Estimated Compressed Size: {compressed_size} bytes")

    def update_graph(self, text):
        freq = build_frequency(text)
        chars = list(freq.keys())
        values = list(freq.values())

        self.ax.clear()
        self.ax.bar(chars, values, color='#1f77b4')
        self.ax.set_title("Character Frequency")
        self.ax.set_xlabel("Characters")
        self.ax.set_ylabel("Frequency")
        self.ax.tick_params(axis='x', labelrotation=45)
        self.canvas.draw()

# ------------------ Main ------------------ #
if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanGUI(root)
    root.mainloop()