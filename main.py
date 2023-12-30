import customtkinter as ctk
import tkinter as tk

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

        # Print today view component in the global container
        TodayView(self)

        # Execute the app
        self.mainloop()

class TodayView(ctk.CTkFrame):
    def __init__(self, parent):
        # Set component master
        super().__init__(master = parent)

        # Create essential variables for later use
        self.taskName = ctk.StringVar()
        self.a = 0

        # Create and print widgets
        self.createWidgets()

    def createWidgets(self):
        # Create add task container, its entry and add button
        self.addTaskFrame = ctk.CTkFrame(self)
        self.addTaskEntry = ctk.CTkEntry(self.addTaskFrame, width = 170, textvariable = self.taskName)
        self.addTaskButton = ctk.CTkButton(self.addTaskFrame, width = 40, text = "+", command = self.addTask)
        
        # Create added tasks container
        self.allTasksFrame = ctk.CTkScrollableFrame(self)

        # Print previous widgets in the global container
        self.addTaskFrame.pack()
        self.addTaskEntry.pack(side = "left")
        self.addTaskButton.pack(side = "left")
        self.allTasksFrame.pack()
        # Print global container itself
        self.pack()

    def addTask(self):
        # Open tasks database file and append whatever the user wrote on the entry when he presses the add button
        self.tasksDatabase = open("tasks.txt", "a")
        self.tasksDatabase.write(self.taskName.get() + "\n")
        # Close database when it finishes writing the task
        self.tasksDatabase.close()

        # Open tasks database file and read it line by line
        self.tasksDatabase = open("tasks.txt", "r")
        self.task = self.tasksDatabase.readlines()

        # Create a container for that added task, its checkbox and task name
        self.taskFrame = ctk.CTkFrame(self.allTasksFrame)
        self.task = ctk.CTkCheckBox(self.taskFrame, text = self.task[self.a])

        # Print previous widgets in the tasks container
        self.taskFrame.pack(fill = "x")
        self.task.pack(side = "left")

        # Grab next task when the user presses the button again
        self.a += 1

App()