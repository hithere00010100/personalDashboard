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

        # Create and print widgets, restore added tasks when reopening the app
        self.createWidgets()
        self.restoreTasks()

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

    def restoreTasks(self):
        # Read tasks file, enumerate them and close their file
        self.tasksFile = open("tasks.txt", "r")
        self.tasks = self.tasksFile.readlines()
        self.tasksFile.close()

        # Store total tasks number
        self.tasksNumber = len(self.tasks)

        for a in range(self.tasksNumber):
            # Create previously added task container, checkbox and name
            self.taskFrame = ctk.CTkFrame(self.allTasksFrame)
            self.taskCheckbox = ctk.CTkCheckBox(self.taskFrame, text = self.tasks[a])

            # Print those widgets
            self.taskFrame.pack(fill = "x")
            self.taskCheckbox.pack(side = "left")

    def addTask(self):
        # Open tasks database file and append whatever the user wrote on the entry when he presses the add button
        self.tasksDatabase = open("tasks.txt", "a")
        self.tasksDatabase.write(self.taskName.get() + "\n")
        # Close database when it finishes writing the task
        self.tasksDatabase.close()

        # Open tasks database file and read it line by line
        self.tasksDatabase = open("tasks.txt", "r")
        self.task = self.tasksDatabase.readlines()

        # Append added task container, checkbox and name
        self.taskFrame = ctk.CTkFrame(self.allTasksFrame)

        a = len(self.task)
        # Fix current index because it's zero based
        a -= 1
        self.task = ctk.CTkCheckBox(self.taskFrame, text = self.task[a])

        # Print previous widgets in the tasks container
        self.taskFrame.pack(fill = "x")
        self.task.pack(side = "left")

App()