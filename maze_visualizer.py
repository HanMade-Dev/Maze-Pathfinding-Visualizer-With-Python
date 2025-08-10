# -*- coding: utf-8 -*-
"""
Maze Pathfinding Visualizer - By HanMade
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from collections import deque
import heapq

# ---------------- Maze Utilities (sama) ----------------

def generate_perfect_maze(rows, cols, rng=None):
    if rows < 5: rows = 5
    if cols < 5: cols = 5
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1

    rng = rng or random.Random()
    grid = [[False for _ in range(cols)] for _ in range(rows)]

    def neighbors(r, c):
        for dr, dc in [(-2,0),(2,0),(0,-2),(0,2)]:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows-1 and 1 <= nc < cols-1:
                yield nr, nc, dr, dc

    start_r = rng.randrange(1, rows, 2)
    start_c = rng.randrange(1, cols, 2)
    grid[start_r][start_c] = True

    stack = [(start_r, start_c)]
    while stack:
        r, c = stack[-1]
        choices = [(nr, nc, dr, dc) for (nr, nc, dr, dc) in neighbors(r, c) if not grid[nr][nc]]
        if choices:
            nr, nc, dr, dc = rng.choice(choices)
            grid[r + dr//2][c + dc//2] = True
            grid[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

    return grid

def valid_neighbors(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
            yield nr, nc

def reconstruct_path(came_from, start, goal):
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = came_from.get(cur)
        if cur is None:
            return []
    path.append(start)
    path.reverse()
    return path

def bfs_search(grid, start, goal):
    queue = deque([start])
    came_from = {start: None}
    visited = set([start])
    nodes_expanded = 0
    while queue:
        cur = queue.popleft()
        nodes_expanded += 1
        yield ('visit', cur, nodes_expanded, came_from)
        if cur == goal:
            path = reconstruct_path(came_from, start, goal)
            yield ('done', path, nodes_expanded, came_from)
            return
        for nb in valid_neighbors(grid, *cur):
            if nb not in visited:
                visited.add(nb)
                came_from[nb] = cur
                queue.append(nb)

def dijkstra_search(grid, start, goal):
    pq = [(0, start)]
    came_from = {start: None}
    dist = {start: 0}
    visited = set()
    nodes_expanded = 0

    while pq:
        d, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        nodes_expanded += 1
        yield ('visit', cur, nodes_expanded, came_from)
        if cur == goal:
            path = reconstruct_path(came_from, start, goal)
            yield ('done', path, nodes_expanded, came_from)
            return
        for nb in valid_neighbors(grid, *cur):
            nd = d + 1
            if nd < dist.get(nb, float('inf')):
                dist[nb] = nd
                came_from[nb] = cur
                heapq.heappush(pq, (nd, nb))

def heuristic_manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar_search(grid, start, goal):
    open_heap = [(heuristic_manhattan(start, goal), 0, start)]
    came_from = {start: None}
    g = {start: 0}
    closed = set()
    nodes_expanded = 0

    while open_heap:
        f, gcost, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)
        nodes_expanded += 1
        yield ('visit', cur, nodes_expanded, came_from)
        if cur == goal:
            path = reconstruct_path(came_from, start, goal)
            yield ('done', path, nodes_expanded, came_from)
            return
        for nb in valid_neighbors(grid, *cur):
            tentative_g = g[cur] + 1
            if tentative_g < g.get(nb, float('inf')):
                g[nb] = tentative_g
                came_from[nb] = cur
                fscore = tentative_g + heuristic_manhattan(nb, goal)
                heapq.heappush(open_heap, (fscore, tentative_g, nb))

def greedy_best_first_search(grid, start, goal):
    pq = [(heuristic_manhattan(start, goal), start)]
    came_from = {start: None}
    visited = set()
    nodes_expanded = 0

    while pq:
        h, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        nodes_expanded += 1
        yield ('visit', cur, nodes_expanded, came_from)
        if cur == goal:
            path = reconstruct_path(came_from, start, goal)
            yield ('done', path, nodes_expanded, came_from)
            return
        for nb in valid_neighbors(grid, *cur):
            if nb not in visited:
                came_from[nb] = cur
                heapq.heappush(pq, (heuristic_manhattan(nb, goal), nb))

# ----------------  UI ----------------

COLOR_WALL   = "#1a1a1a"
COLOR_PATH   = "#ffffff"
COLOR_START  = "#4CAF50"
COLOR_GOAL   = "#F44336"
COLOR_VISIT  = "#64B5F6"
COLOR_TRACE  = "#2d7ff9"
COLOR_FINAL  = "#FFEB3B"

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Pathfinding Visualizer — By HanMade")
        self.root.minsize(900, 600)

        try:
            style = ttk.Style(self.root)
            if 'clam' in style.theme_names():
                style.theme_use('clam')
            style.configure("Primary.TButton", padding=(8,6), font=("Arial", 10, "bold"),
                            background="#2d7ff9", foreground="#ffffff")
            style.map("Primary.TButton",
                      background=[("active", "#1b5fd1"), ("disabled", "#9fb9ff")],
                      foreground=[("disabled", "#f0f0f0")])
            style.configure("Neutral.TButton", padding=(8,6), font=("Arial", 10),
                            background="#ececec", foreground="#222222")
            style.map("Neutral.TButton",
                      background=[("active", "#d9d9d9"), ("disabled", "#f2f2f2")])
        except Exception:
            pass

        # Algoritma
        self.algorithms = {
            "A* (Manhattan - Optimal)": astar_search,
            "Dijkstra (Unweighted demo)": dijkstra_search,
            "BFS (Shortest Path - Unweighted)": bfs_search,
            "Greedy Best-First (Heuristic)": greedy_best_first_search,
        }

        # State
        self.rows = 31
        self.cols = 31
        self.running = False
        self.algo_name = tk.StringVar(value="A* (Manhattan - Optimal)")
        self.nodes_expanded = 0
        self.setting_start = True
        self.marker_ids = {"start": [], "goal": []}

        # Speed params
        self.speed_var = tk.IntVar(value=100)
        self._batch_steps = 800
        self._frame_delay_ms = 0

        # Build UI
        self._build_ui()
        self._bind_events()

        # Data
        self.rng = random.Random()
        self.grid = None
        self.start = None
        self.goal = None

        self._generate_and_draw()

    def _build_ui(self):
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=COLOR_PATH, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        panel = ttk.Frame(container, width=280, padding=12)
        panel.pack(side="right", fill="y")
        panel.pack_propagate(False)

        ttk.Label(panel, text="Menu", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0,10))

        ttk.Label(panel, text="Metode").pack(anchor="w")
        self.algo_combo = ttk.Combobox(panel, textvariable=self.algo_name, state="readonly",
                                       values=list(self.algorithms.keys()))
        self.algo_combo.pack(fill="x", pady=(0,8))

        self.btn_start = ttk.Button(panel, text="Mulai Visualisasi ▶", style="Primary.TButton", command=self.on_start)
        self.btn_start.pack(fill="x", pady=(6,4))

        self.btn_stop = ttk.Button(panel, text="Stop ⏹", style="Neutral.TButton", command=self.on_stop, state="disabled")
        self.btn_stop.pack(fill="x", pady=4)

        self.btn_gen = ttk.Button(panel, text="Buat Maze Acak", style="Neutral.TButton", command=self.on_generate)
        self.btn_gen.pack(fill="x", pady=4)

        self.btn_clear = ttk.Button(panel, text="Clear Paths", style="Neutral.TButton", command=self.on_clear_paths)
        self.btn_clear.pack(fill="x", pady=4)

        ttk.Separator(panel).pack(fill="x", pady=12)

        speed_box = ttk.Frame(panel)
        speed_box.pack(fill="x", pady=(0,8))
        ttk.Label(speed_box, text="Kecepatan").pack(anchor="w")
        self.speed_scale = ttk.Scale(speed_box, from_=0, to=100, orient="horizontal",
                                     command=self._on_speed_change, variable=self.speed_var)
        self.speed_scale.pack(fill="x")
        hint = ttk.Frame(speed_box)
        hint.pack(fill="x")
        ttk.Label(hint, text="Sangat Lambat").pack(side="left")
        ttk.Label(hint, text="Maks").pack(side="right")
        self._apply_speed_value(self.speed_var.get())  # init

        self.status_label = ttk.Label(panel, text="Status: Siap", wraplength=250, justify="left")
        self.status_label.pack(anchor="w", pady=(8,2))

        self.timer_label = ttk.Label(panel, text="Durasi: 0.0 ms")
        self.timer_label.pack(anchor="w")

        self.nodes_label = ttk.Label(panel, text="Node dieksplor: 0")
        self.nodes_label.pack(anchor="w", pady=(0,8))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

    def _bind_events(self):
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _on_speed_change(self, _evt=None):
        self._apply_speed_value(self.speed_var.get())

    def _apply_speed_value(self, val):
        t = max(0.0, min(1.0, float(val)/100.0))
        min_steps, max_steps = 1, 2000
        self._batch_steps = int(min_steps + (max_steps - min_steps) * (t**2))
        if self._batch_steps < 1: self._batch_steps = 1
        self._frame_delay_ms = int(300 * ((1.0 - t) ** 1.5))

    # ---------- Drawing ----------
    def _compute_cell_geometry(self):
        if self.grid is None:
            return 10, 10
        H = max(self.canvas.winfo_height(), 100)
        W = max(self.canvas.winfo_width(), 100)
        rows = len(self.grid); cols = len(self.grid[0])
        return W / cols, H / rows

    def _cell_rect(self, r, c):
        cw, ch = self._compute_cell_geometry()
        x0 = c * cw; y0 = r * ch
        return x0, y0, x0+cw, y0+ch

    def _cell_center(self, r, c):
        x0, y0, x1, y1 = self._cell_rect(r, c)
        return (x0+x1)/2, (y0+y1)/2

    def _raise_markers(self):
        self.canvas.tag_raise("marker_start")
        self.canvas.tag_raise("marker_goal")
        self.canvas.tag_raise("marker_text_start")
        self.canvas.tag_raise("marker_text_goal")

    def _draw_marker(self, cell, kind="start"):
        r, c = cell
        x0, y0, x1, y1 = self._cell_rect(r, c)
        pad = min((x1-x0), (y1-y0)) * 0.1
        fill = COLOR_START if kind == "start" else COLOR_GOAL
        outline = "#0d6b3b" if kind == "start" else "#b32039"
        tag_box = "marker_start" if kind == "start" else "marker_goal"
        tag_text = "marker_text_start" if kind == "start" else "marker_text_goal"
        for iid in getattr(self, "marker_ids", {}).get(kind, []):
            self.canvas.delete(iid)
        box_id = self.canvas.create_rectangle(x0+pad, y0+pad, x1-pad, y1-pad,
                                              fill=fill, outline=outline, width=2, tags=(tag_box,))
        text_id = self.canvas.create_text((x0+x1)/2, (y0+y1)/2,
                                          text="S" if kind=="start" else "G",
                                          fill="#ffffff",
                                          font=("TkDefaultFont", int(max(10, (x1-x0)*0.25)), "bold"),
                                          tags=(tag_text,))
        self.marker_ids[kind] = [box_id, text_id]
        self._raise_markers()

    def _paint_cell(self, r, c, color):
        if (r, c) == self.start or (r, c) == self.goal:
            return
        x0, y0, x1, y1 = self._cell_rect(r, c)
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)
        self._raise_markers()

    def _draw_visit_line(self, frm, to):
        x0, y0 = self._cell_center(*frm)
        x1, y1 = self._cell_center(*to)
        self.canvas.create_line(x0, y0, x1, y1, width=2, fill=COLOR_TRACE, capstyle="round")
        self._raise_markers()

    def _draw_final_path(self, path):
        if len(path) < 2:
            return
        pts = []
        for r, c in path:
            x, y = self._cell_center(r, c)
            pts.extend([x, y])
            self._paint_cell(r, c, COLOR_FINAL)
        self.canvas.create_line(*pts, width=5, fill=COLOR_FINAL, capstyle="round", joinstyle="round")
        self._raise_markers()

    def _redraw_all(self):
        if self.grid is None:
            return
        self.canvas.delete("all")
        rows, cols = len(self.grid), len(self.grid[0])
        for r in range(rows):
            for c in range(cols):
                x0, y0, x1, y1 = self._cell_rect(r, c)
                color = COLOR_PATH if self.grid[r][c] else COLOR_WALL
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)
        if self.start:
            self._draw_marker(self.start, "start")
        if self.goal:
            self._draw_marker(self.goal, "goal")
        self.nodes_label.configure(text="Node dieksplor: 0")
        self.timer_label.configure(text="Durasi: 0.0 ms")

    # ---------- Actions ----------
    def _generate_and_draw(self):
        self.grid = generate_perfect_maze(self.rows, self.cols, random.Random())
        cells = [(r,c) for r in range(len(self.grid)) for c in range(len(self.grid[0])) if self.grid[r][c]]
        if len(cells) < 2:
            messagebox.showerror("Error", "Maze gagal dibuat. Coba lagi.")
            return
        self.start, self.goal = random.sample(cells, 2)
        self.setting_start = True
        self._redraw_all()
        self.status_label.config(text="Status: Siap — Klik kanvas untuk set Start, lalu Finish.")

    def _on_resize(self, _evt):
        self._redraw_all()

    def on_generate(self):
        if self.running: return
        self.status_label.config(text="Status: Membuat maze acak...")
        self._generate_and_draw()
        self.status_label.config(text="Status: Siap — Klik kanvas untuk set Start, lalu Finish.")

    def on_clear_paths(self):
        if self.grid is None: return
        self._redraw_all()
        self.status_label.config(text="Status: Dibersihkan")

    def on_start(self):
        if self.running: return
        if self.grid is None or self.start is None or self.goal is None: return
        algo = self.algorithms.get(self.algo_name.get())
        if algo is None:
            messagebox.showerror("Metode tidak ditemukan", "Pilih metode yang tersedia.")
            return
        self.on_clear_paths()
        self.running = True
        self._set_controls_state(True)
        self.nodes_expanded = 0
        self.t0 = time.perf_counter()
        self.search_gen = algo(self.grid, self.start, self.goal)
        self.status_label.config(text=f"Status: Menjalankan {self.algo_name.get()}...")
        self.root.after_idle(self._step_animation)

    def on_stop(self):
        if not self.running: return
        self.running = False
        self._set_controls_state(False)
        self.status_label.config(text="Status: Dihentikan")

    def _set_controls_state(self, running: bool):
        self.btn_start.configure(state="disabled" if running else "normal")
        self.btn_stop.configure(state="normal" if running else "disabled")
        self.btn_gen.configure(state="disabled" if running else "normal")
        self.btn_clear.configure(state="disabled" if running else "normal")
        self.algo_combo.configure(state="disabled" if running else "readonly")

    def _update_info(self, nodes, elapsed_ms):
        self.nodes_label.configure(text=f"Node dieksplor: {nodes}")
        self.timer_label.configure(text=f"Durasi: {elapsed_ms:.1f} ms")

    def _step_animation(self):
        if not self.running:
            return
        steps = 0
        max_steps = self._batch_steps
        try:
            while steps < max_steps and self.running:
                event = next(self.search_gen)
                et = (time.perf_counter() - self.t0) * 1000.0
                if event[0] == 'visit':
                    cur = event[1]
                    nodes = event[2]
                    came_from = event[3]
                    parent = came_from.get(cur)
                    self.nodes_expanded = nodes
                    self._paint_cell(cur[0], cur[1], COLOR_VISIT)
                    if parent is not None:
                        self._draw_visit_line(parent, cur)
                    self._update_info(nodes, et)
                elif event[0] == 'done':
                    path = event[1]
                    nodes = event[2]
                    self._draw_final_path(path)
                    et = (time.perf_counter() - self.t0) * 1000.0
                    self._update_info(nodes, et)
                    self.running = False
                    self._set_controls_state(False)
                    self.status_label.config(text="Status: Jalur ditemukan!")
                    return
                steps += 1
        except StopIteration:
            self.running = False
            self._set_controls_state(False)
            self.status_label.config(text="Status: Selesai")
            return

        if self._frame_delay_ms <= 0:
            self.root.after_idle(self._step_animation)
        else:
            self.root.after(self._frame_delay_ms, self._step_animation)

    # ---------- Interaction ----------
    def _compute_cell(self, x, y):
        if self.grid is None:
            return None
        cw, ch = self._compute_cell_geometry()
        c = int(x // cw); r = int(y // ch)
        rows, cols = len(self.grid), len(self.grid[0])
        if 0 <= r < rows and 0 <= c < cols:
            return (r, c)
        return None

    def _on_canvas_click(self, event):
        if self.running or self.grid is None:
            return
        cell = self._compute_cell(event.x, event.y)
        if not cell: return
        r, c = cell
        if not self.grid[r][c]:
            return
        if self.setting_start:
            if self.goal == cell: return
            self.start = cell
            self._draw_marker(self.start, "start")
            self.status_label.config(text="Status: Titik Start di-set. Klik sel lain untuk set Finish.")
        else:
            if self.start == cell: return
            self.goal = cell
            self._draw_marker(self.goal, "goal")
            self.status_label.config(text="Status: Titik Finish di-set. Klik lagi untuk set Start.")
        self.setting_start = not self.setting_start

def main():
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
