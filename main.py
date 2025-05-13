import random
import time
from tkinter import *
root = Tk()
root.title("Sudoku Solver")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.configure(bg="#0f111a")
root.iconbitmap('icon.ico')
grid_refs = [[StringVar(root) for _ in range(9)] for _ in range(9)]
current_pos = [0, 0]

def center_grid(frame):
    frame.place(relx=0.5, rely=0.45, anchor='center')

class PuzzleBrain:
    def __init__(self, ui_ref):
        self.ui = ui_ref
        self._sanitize()
        self._solving = True
        self._solve()
        self._solving = False

    def _sanitize(self):
        for r in range(9):
            for c in range(9):
                if grid_refs[r][c].get() not in '123456789':
                    grid_refs[r][c].set('0')

    def _solve(self):
        if self.ui._cancel_solve:
            return False

        pos = self._next_empty()
        if pos is None:
            return True
        x, y = pos
        for val in range(1, 10):
            if self._is_safe(x, y, val):
                grid_refs[x][y].set(str(val))
                self.ui.mark_cell(x, y, 'normal')
                root.update()
                root.after(40)
                
                if self.ui._cancel_solve:
                    return False

                if self._solve():
                    return True
                grid_refs[x][y].set('0')
        self.ui.mark_cell(x, y, 'error')
        root.update()
        root.after(40)
        return False

    def _next_empty(self):
        for i in range(9):
            for j in range(9):
                if grid_refs[i][j].get() == '0' or grid_refs[i][j].get() == '':
                    return i, j
        return None

    def _is_safe(self, row, col, num):
        str_num = str(num)
        for k in range(9):
            if grid_refs[row][k].get() == str_num or grid_refs[k][col].get() == str_num:
                return False
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if grid_refs[i][j].get() == str_num:
                    return False
        return True

class SudokuUI:
    def __init__(self, root):
        self.root = root
        self.cells = [[None for _ in range(9)] for _ in range(9)]

        self.frame = Frame(root, bg="#0f111a")
        center_grid(self.frame)

        self.draw_grid()
        self.bind_keys()

        self.solving = False
        self._cancel_solve = False
        self.start_time = 0

        self.status_label = Label(root, text="Status: Idle", fg="white", bg="#0f111a", font=("Consolas", 12))
        self.status_label.place(relx=0.45, rely=0.9, anchor='center')

        self.timer_label = Label(root, text="Time: 0.0s", fg="white", bg="#0f111a", font=("Consolas", 12))
        self.timer_label.place(relx=0.55, rely=0.9, anchor='center')

        self.decode_btn = Button(root, text="Decode", command=self.toggle_solve,
           font=('Consolas', 14), bg="#007acc", fg="white",
           activebackground="#005f99", relief=FLAT, bd=2, highlightthickness=2, highlightbackground="#005a9c")
        self.decode_btn.place(relx=0.15, rely=0.93, relwidth=0.2, relheight=0.06)
        self.decode_btn.bind("<Enter>", lambda e: self._btn_hover(self.decode_btn))
        self.decode_btn.bind("<Leave>", lambda e: self._btn_leave(self.decode_btn))

        generate_btn = Button(root, text="Generate", command=self.generate,
            font=('Consolas', 14), bg="#28a745", fg="white",
            activebackground="#1e7e34", relief=FLAT, bd=2, highlightthickness=2, highlightbackground="#1b6b2a")
        generate_btn.place(relx=0.4, rely=0.93, relwidth=0.2, relheight=0.06)
        generate_btn.bind("<Enter>", lambda e: generate_btn.config(bg="#1e7e34"))
        generate_btn.bind("<Leave>", lambda e: generate_btn.config(bg="#28a745"))

        reset_btn = Button(root, text="Reset", command=self.clear_all,
            font=('Consolas', 14), bg="#e53935", fg="white",
            activebackground="#b71c1c", relief=FLAT, bd=2, highlightthickness=2, highlightbackground="#a81a1a")
        reset_btn.place(relx=0.65, rely=0.93, relwidth=0.2, relheight=0.06)
        reset_btn.bind("<Enter>", lambda e: reset_btn.config(bg="#b71c1c"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.config(bg="#e53935"))

    def _btn_hover(self, btn):
        if btn == self.decode_btn:
            if not self.solving:
                btn.config(bg="#005f99", highlightbackground="#004f7a")
            else:
                btn.config(bg="#c9302c", highlightbackground="#a12724")  

    def _btn_leave(self, btn):
        if btn == self.decode_btn:
            if not self.solving:
                btn.config(bg="#007acc", highlightbackground="#005a9c")
            else:
                btn.config(bg="#d9534f", highlightbackground="#b52f2a") 

    def draw_grid(self):
        font = ('Consolas', 22)
        for r in range(9):
            for c in range(9):
                color = '#1e202f' if (r // 3 + c // 3) % 2 == 0 else '#282c3a'
                entry = Entry(self.frame, width=2, font=font, justify='center',
                              bg=color, fg='white', insertbackground='white',
                              relief=FLAT, textvar=grid_refs[r][c])
                entry.grid(row=r, column=c, padx=4, pady=4, ipadx=15, ipady=15)
                self.cells[r][c] = entry

    def bind_keys(self):
        self.root.bind("<Left>", lambda e: self.move_cursor(0, -1))
        self.root.bind("<Right>", lambda e: self.move_cursor(0, 1))
        self.root.bind("<Up>", lambda e: self.move_cursor(-1, 0))
        self.root.bind("<Down>", lambda e: self.move_cursor(1, 0))
        self.focus_cell(*current_pos)

    def move_cursor(self, dr, dc):
        current_pos[0] = (current_pos[0] + dr) % 9
        current_pos[1] = (current_pos[1] + dc) % 9
        self.focus_cell(*current_pos)

    def focus_cell(self, r, c):
        self.cells[r][c].focus_set()

    def clear_all(self):
        if self.solving:
            self._cancel_solve = True
        for r in range(9):
            for c in range(9):
                grid_refs[r][c].set('')
                self.mark_cell(r, c, 'normal')
        self.status_label.config(text="Status: Idle")
        self.timer_label.config(text="Time: 0.0s")
        self.solving = False
        self._cancel_solve = False
        self.decode_btn.config(text="Decode", bg="#007acc", activebackground="#005f99", highlightbackground="#005a9c")

    def toggle_solve(self):
        if not self.solving:
            self.solving = True
            self._cancel_solve = False
            self.status_label.config(text="Status: Solving...")
            self.decode_btn.config(text="Stop", bg="#d9534f", activebackground="#c9302c", highlightbackground="#b52f2a")
            self.start_time = time.time()
            self.update_timer()
            self.root.after(10, self.run_solver_step)
        else:
            self._cancel_solve = True
            self.status_label.config(text="Status: Stopping...")

    def run_solver_step(self):
        if self._cancel_solve:
            self.solving = False
            self.status_label.config(text="Status: Stopped")
            self.decode_btn.config(text="Decode", bg="#007acc", activebackground="#005f99", highlightbackground="#005a9c")
            return



        import threading

        def solver_thread():
            PuzzleBrain(self)
            self.root.after(0, self.solve_done)

        threading.Thread(target=solver_thread, daemon=True).start()

    def solve_done(self):
        if not self._cancel_solve:
            self.status_label.config(text="Status: Solved")
        else:
            self.status_label.config(text="Status: Stopped")
        self.solving = False
        self._cancel_solve = False
        self.decode_btn.config(text="Decode", bg="#007acc", activebackground="#005f99", highlightbackground="#005a9c")
        self.timer_label.config(text=f"Time: {time.time()-self.start_time:.1f}s")

    def update_timer(self):
        if self.solving:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"Time: {elapsed:.1f}s")
            self.root.after(100, self.update_timer)
        else:
            pass

    def mark_cell(self, r, c, status):
        if status == 'error':
            self.cells[r][c].config(bg="#b71c1c")
        else:
            self.cells[r][c].config(bg='#3a3d56' if (r // 3 + c // 3) % 2 == 0 else '#40445d')

    def generate(self):
        self.clear_all()
        puzzle = self.generate_puzzle()
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] != 0:
                    grid_refs[r][c].set(str(puzzle[r][c]))

    def generate_puzzle(self):
        def is_valid(grid, r, c, val):
            str_val = str(val)
            for i in range(9):
                if grid[r][i] == val or grid[i][c] == val:
                    return False
            br, bc = 3 * (r // 3), 3 * (c // 3)
            for i in range(br, br + 3):
                for j in range(bc, bc + 3):
                    if grid[i][j] == val:
                        return False
            return True

        def fill_grid(grid):
            for i in range(9):
                for j in range(9):
                    if grid[i][j] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            if is_valid(grid, i, j, num):
                                grid[i][j] = num
                                if fill_grid(grid):
                                    return True
                                grid[i][j] = 0
                        return False
            return True

        full_grid = [[0 for _ in range(9)] for _ in range(9)]
        fill_grid(full_grid)

        for _ in range(40):
            i, j = random.randint(0, 8), random.randint(0, 8)
            full_grid[i][j] = 0
        return full_grid

SudokuUI(root)
root.mainloop()
