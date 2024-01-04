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
        self.entryValue = ctk.StringVar()
        self.checkboxesStates = []

        # Set initial conditions
        self.isFirstTime = True

        # Open database
        self.connection = db.connect("tasks.db")

        # Create inbox tasks table (with row id and task label columns) in the database
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS inbox (id INTEGER, label TEXT)")

        # Close database
        self.connection.close()
        
        # Create and print widgets, restore previously added tasks when relaunching the app and start watching checkboxes states changes
        self.createWidgets()
        self.restoreTasks()
        self.completeTask()

    def createWidgets(self):
        # Create add task container, entry and add button
        self.addTaskFrame = ctk.CTkFrame(self)
        self.addTaskEntry = ctk.CTkEntry(self.addTaskFrame, width = 170, textvariable = self.entryValue)
        self.addTaskButton = ctk.CTkButton(self.addTaskFrame, width = 40, text = "+", command = self.addTask)
        
        # Print previous widgets in the global container
        self.addTaskFrame.pack()
        self.addTaskEntry.pack(side = "left")
        self.addTaskButton.pack(side = "left")
        # Print global container itself
        self.pack()

    def restoreTasks(self):
        # Open database
        self.connection = db.connect("tasks.db")
        self.cursor = self.connection.cursor()
        
        if self.isFirstTime == False:
            # Reset checkboxes list when a task is marked as completed
            self.checkboxesStates = []
            # Unprint added task frame
            self.addedTasksFrame.pack_forget()

            # Get inbox rows number
            self.cursor.execute("SELECT COUNT (label) FROM inbox")
            # Use rows number as an index
            self.tasksNumber = self.cursor.fetchone()[0]

            b = self.checkedTaskIndex
            c = self.checkedTaskIndex + 1

            for a in range(self.tasksNumber):
                # Use deleted task index on other remaining tasks
                self.cursor.execute("UPDATE inbox SET id = ? WHERE id = ?", (b, c,))
                
                # Go to the next task to set its new index
                c += 1
                b += 1
            
            # Save modified database
            self.connection.commit()

        # With the database open, get all the tasks labels
        self.cursor.execute("SELECT label FROM inbox")
        self.tasksLabels = self.cursor.fetchall()

        # Create and print added tasks container
        self.addedTasksFrame = ctk.CTkScrollableFrame(self)
        self.addedTasksFrame.pack()

        a = 0

        for label in self.tasksLabels:
            # Append something to checkboxes list and then replace that item to a checkbox variable
            self.checkboxesStates.append("X")
            self.checkboxesStates[a] = ctk.StringVar()
            
            # Go through every task and create its container, checkbox and label
            self.taskFrame = ctk.CTkFrame(self.addedTasksFrame)
            self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = label[0], variable=self.checkboxesStates[a])

            # Print previous widgets in the added tasks container
            self.taskFrame.pack(fill = "x")
            self.taskInfo.pack(side = "left")
            
            # Go to the next checkboxes list item
            a += 1

        # Close database
        self.connection.close()
        
        # Make available update tasks when a task is deleted
        self.isFirstTime = False
    
    def addTask(self):
        # Open database
        self.connection = db.connect("tasks.db")
        self.cursor = self.connection.cursor()

        # Get inbox rows number
        self.cursor.execute("SELECT COUNT (label) FROM inbox")
        # Use rows number as an index
        self.tasksNumber = self.cursor.fetchone()[0]
        a = self.tasksNumber + 1
        b = self.tasksNumber

        # Append entry field text as a new task in the database with an identifier
        self.cursor.execute("INSERT INTO inbox (id, label) VALUES (?, ?)", (a, self.entryValue.get(),))
        # Save modified database
        self.connection.commit()

        # Append something to checkboxes list and then replace that item to a checkbox variable
        self.checkboxesStates.append("X")
        self.checkboxesStates[b] = ctk.StringVar()

        # Get the task label from the database
        self.cursor.execute("SELECT label FROM inbox WHERE id = ?", (a,))
        self.label = self.cursor.fetchone()
        
        # Close database
        self.connection.close()
        
        # Create task container, checkbox and label
        self.taskFrame = ctk.CTkFrame(self.addedTasksFrame)
        self.taskInfo = ctk.CTkCheckBox(self.taskFrame, text = self.label[0], variable=self.checkboxesStates[b])

        # Print previous widgets in the added tasks container
        self.taskFrame.pack(fill = "x")
        self.taskInfo.pack(side = "left")

    def completeTask(self):
        # Open database
        self.connection = db.connect("tasks.db")
        self.cursor = self.connection.cursor()

        # Get inbox rows number
        self.cursor.execute("SELECT COUNT (label) FROM inbox")
        # Use rows number as an index
        self.tasksNumber = self.cursor.fetchone()[0]

        for a in range(self.tasksNumber):
            if self.checkboxesStates[a].get() == "1":
                b = a + 1
                
                # Capture checked task id
                self.checkedTaskIndex = b

                # Check every checkbox variable and delete the one that is checked
                self.cursor.execute("DELETE FROM inbox WHERE id = ?", (b,))
                # Save modified database
                self.connection.commit()

                # Rebuild remaining tasks
                self.restoreTasks()
                # Do not consider other checked tasks below this one
                break

        # Close database
        self.connection.close()

        # Keep on checking checked tasks every half second
        self.after(500, self.completeTask)

App()