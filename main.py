import customtkinter as ctk
import tkinter as tk
import sqlite3 as db

class App(ctk.CTk):
    def __init__(self):
        # Set window title, size and position
        super().__init__()
        self.title("")
        self.geometry("230x400+700+200")
        self.resizable(False, False)

        # Set window dark mode and color accent
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Create tasks database
        self.connection = db.connect("tasks.db")
        self.connection.close()

        # Print inbox component in the global container
        Inbox(self)

        # Execute the app
        self.mainloop()

class Inbox(ctk.CTkFrame):
    def __init__(self, parent):
        # Set component master
        super().__init__(master = parent)

        # Create essential variables for later use
        self.taskName = ctk.StringVar()

        # Open database
        self.connection = db.connect("tasks.db")

        # Create inbox tasks table (with task name column) in the database
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS inbox (name TEXT)")

        # Close database
        self.connection.close()
        
        # Create and print widgets, restore previously added tasks when relaunching the app
        self.createWidgets()
        self.restoreTasks()

    def createWidgets(self):
        # Create add task container, entry and add button
        self.addTaskFrame = ctk.CTkFrame(self)
        self.addTaskEntry = ctk.CTkEntry(self.addTaskFrame, width = 170, textvariable = self.taskName)
        self.addTaskButton = ctk.CTkButton(self.addTaskFrame, width = 40, text = "+", command = self.addTask)
        
        # Create added tasks container
        self.tasksFrame = ctk.CTkScrollableFrame(self)

        # Print previous widgets in the global container
        self.addTaskFrame.pack()
        self.addTaskEntry.pack(side = "left")
        self.addTaskButton.pack(side = "left")
        self.tasksFrame.pack()
        # Print global container itself
        self.pack()

    def restoreTasks(self):
        # Open database
        self.connection = db.connect("tasks.db")

        # With the database open, get all the tasks
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT * FROM inbox")
        self.tasks = self.cursor.fetchall()

        # Close database
        self.connection.close()

        for taskName in self.tasks:
            # Go through every task and create its container and checkbox widget (assign checkbox title as the task name)
            self.taskFrame = ctk.CTkFrame(self.tasksFrame)
            self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = taskName[0])

            # Print previous widgets in the added tasks container
            self.taskFrame.pack(fill = "x")
            self.taskInfo.pack(side = "left")

    def addTask(self):
        # Open database
        self.connection = db.connect("tasks.db")

        # Append entry field text as a new task in the database
        self.cursor = self.connection.cursor()
        self.cursor.execute("INSERT INTO inbox (name) VALUES (?)", (self.taskName.get(),))

        # Save modified database
        self.connection.commit()

        # Get database rows number
        self.cursor.execute("SELECT COUNT(*) FROM inbox")
        # Use rows number as an index
        a = self.cursor.fetchone()[0]

        # Get the task name from the database
        self.cursor.execute("SELECT name FROM inbox WHERE rowid = ?", (a,))
        self.name = self.cursor.fetchone()
        
        # Close database
        self.connection.close()

        # Create task container and checkbox widget (assign checkbox title as the task name)
        self.taskFrame = ctk.CTkFrame(self.tasksFrame)
        self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = self.name[0])

        # Print previous widgets in the added tasks container
        self.taskFrame.pack(fill = "x")
        self.taskInfo.pack(side = "left")

App()