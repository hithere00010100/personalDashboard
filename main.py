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
        Inbox(self)

        # Execute the app
        self.mainloop()

class Inbox(ctk.CTkFrame):
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
        self.tasksFrame = ctk.CTkScrollableFrame(self)

        # Print previous widgets in the global container
        self.addTaskFrame.pack()
        self.addTaskEntry.pack(side = "left")
        self.addTaskButton.pack(side = "left")
        self.tasksFrame.pack()
        # Print global container itself
        self.pack()

    def restoreTasks(self):
        # Read tasks file, enumerate them and close saved file
        self.tasksFile = open("tasks.txt", "r")
        self.oldTasks = self.tasksFile.readlines()
        self.tasksFile.close()

        # Store total tasks number
        self.tasksNumber = len(self.oldTasks)

        for a in range(self.tasksNumber):
            # Create previously added task container, checkbox and name
            self.taskFrame = ctk.CTkFrame(self.tasksFrame)
            self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = self.oldTasks[a])

            # Print those widgets
            self.taskFrame.pack(fill = "x")
            self.taskInfo.pack(side = "left")

    def addTask(self):
        # Open tasks file, append whatever the user wrote on the entry when he presses the add button and close the saved file
        self.tasksFile = open("tasks.txt", "a")
        self.tasksFile.write(self.taskName.get() + "\n")
        self.tasksFile.close()

        # Open tasks file, read it line by line and close saved file
        self.tasksFile = open("tasks.txt", "r")
        self.tasks = self.tasksFile.readlines()
        self.tasksFile.close()

        # Create added task container, checkbox and name at the end of the list
        self.taskFrame = ctk.CTkFrame(self.tasksFrame)

        a = len(self.tasks)
        # Fix current index because it's zero based
        a -= 1
        self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = self.tasks[a])

        # Print previous widgets in the tasks container
        self.taskFrame.pack(fill = "x")
        self.taskInfo.pack(side = "left")

App()