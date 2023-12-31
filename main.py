import customtkinter as ctk
import tkinter as tk
import sqlite3 as db

class App(ctk.CTk):
    def __init__(self):
        # Set app title and size
        super().__init__()
        self.title("")
        self.geometry("230x400+700+200")
        self.resizable(False, False)

        # Set app dark mode and color accent
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Create tasks database
        self.dbConnection = db.connect("tasks.db")
        self.dbConnection.close()

        # Print today view component in the global container
        Inbox(self)

        # Execute the app
        self.mainloop()

class Inbox(ctk.CTkFrame):
    def __init__(self, parent):
        # Set component master
        super().__init__(master = parent)

        # Create essential variables for later use
        self.taskName = ctk.StringVar()
        self.a = 1

        # Create a table for inbox tasks inside the database
        self.dbConnection = db.connect("tasks.db")

        self.dbCursor = self.dbConnection.cursor()
        self.dbCursor.execute("CREATE TABLE IF NOT EXISTS inbox (name TEXT)")

        self.dbConnection.close()

        # Create and print widgets, restore previously added tasks when reopening the app
        self.createWidgets()
        self.restoreTasks()

    def createWidgets(self):
        # Create add task container, its entry and add button
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
        # Extract every row value from the name column
        self.dbConnection = db.connect("tasks.db")

        self.dbCursor = self.dbConnection.cursor()
        self.dbCursor.execute("SELECT * FROM inbox")

        for taskName in self.dbCursor.fetchall():
            # Create task container, checkbox and name; assign that extracted database value as the name of the task
            self.taskFrame = ctk.CTkFrame(self.tasksFrame)
            self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = taskName[0])

            # Print previous widgets in the tasks container
            self.taskFrame.pack(fill = "x")
            self.taskInfo.pack(side = "left")

        self.dbConnection.close()

    def addTask(self):
        # Store in the database whatever the user typed in the entry and save modified database
        self.dbConnection = db.connect("tasks.db")

        self.dbCursor = self.dbConnection.cursor()
        self.dbCursor.execute("INSERT INTO inbox (name) VALUES (?)", (self.taskName.get(),))
        self.dbConnection.commit()

        # Extract first row value from the name column
        self.dbData = self.dbCursor.execute("SELECT name FROM inbox WHERE rowid = ?", (self.a,))
        self.dbResult = self.dbCursor.fetchone()

        # Create task container, checkbox and name; assign that extracted database value as the name of the task
        self.taskFrame = ctk.CTkFrame(self.tasksFrame)
        self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = self.dbResult[0])

        # Print previous widgets in the tasks container
        self.taskFrame.pack(fill = "x")
        self.taskInfo.pack(side = "left")
        
        # Increase index variable so next time a task is added, it is added in the next row
        self.a += 1

        self.dbConnection.close()

App()