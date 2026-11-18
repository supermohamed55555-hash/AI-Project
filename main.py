"""
main.py
Main entry point for the XO (Tic-Tac-Toe) AI Project.
Course: Introduction to Artificial Intelligence (CAI3101 & CS366)
Arab Academy for Science, Technology and Maritime Transport (AASTMT)
"""

import tkinter as tk
from gui import TicTacToeGUI


def main():
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
