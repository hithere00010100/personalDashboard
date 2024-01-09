from settings import *
import customtkinter as ctk
import tkinter as tk
import sqlite3 as db

class Inbox(ctk.CTkFrame):
    def __init__(self, parent, window):
        # Set container master and color
        super().__init__(master = parent, fg_color = DARKER_GRAY)

        # Make available here all those external attributes and methods
        self.window = window

        # Set placeholder
        self.entryValue = ctk.StringVar(value = "Enter task name")
        
        # Create essential variables for later use
        self.checkboxesStates = []
        self.tasksNumber = ctk.StringVar()

        # Set initial conditions
        self.isFirstTime = True

        # Open database
        connection = db.connect("tasks.db")

        # Create inbox tasks table (with row id and task label columns) in the database
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS inbox (id INTEGER, label TEXT)")

        # Close database
        connection.close()
        
        # Create and print widgets, restore previously added tasks when relaunching the app
        self.createWidgets()
        self.restoreTasks()

    def createWidgets(self):
        # Create fonts
        projectNameFont = ctk.CTkFont(family = FONT_FAMILY,
                           size = PROJECT_NAME_SIZE)
        
        projectTaskCounterFont = ctk.CTkFont(family = FONT_FAMILY,
                                       size = PROJECT_TASK_COUNTER_SIZE)
        
        self.taskNameFont = ctk.CTkFont(family = FONT_FAMILY,
                                        size = TASK_NAME_SIZE)

        # Create project container, project name label, task counter label and add task button
        projectFrame = ctk.CTkFrame(self,
                                    fg_color = DARKER_GRAY)
        
        projectName = ctk.CTkLabel(projectFrame,
                                    text = "Inbox",
                                    text_color = WHITE,
                                    font = projectNameFont)
        
        projectTaskCounter = ctk.CTkLabel(projectFrame,
                                          text = "",
                                          text_color = WHITE,
                                          textvariable = self.tasksNumber,
                                          font = projectTaskCounterFont)

        addTaskButton = ctk.CTkButton(projectFrame,
                                      width = 30,
                                      height = 30,
                                      fg_color = DARK_GRAY,
                                      hover_color = LIGHT_GRAY,
                                      text = "+",
                                      text_color = WHITE,
                                      font = projectNameFont,
                                      command = self.openAddTaskWindow)
        
        # Create added tasks container for the first time
        self.addedTasksFrame = ctk.CTkScrollableFrame(self,
                                                      fg_color = DARK_GRAY,
                                                      scrollbar_button_color = WHITE,
                                                      scrollbar_button_hover_color = WHITE)

        # Print created widgets in the global container
        projectFrame.pack(fill = "x", padx = 10, pady = 10)
        projectName.pack(side = "left")
        projectTaskCounter.pack(side = "left", padx = 10)
        addTaskButton.pack(side = "right")
        self.addedTasksFrame.pack(padx = 10, pady = 10)
        # Print global container itself
        self.pack(fill = "x")

        # Create keyboard shortcuts
        self.window.bind("<Alt-KeyPress-q>", lambda event: self.openAddTaskWindow())

    def restoreTasks(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()
        
        if self.isFirstTime == False:
            # Reset checkboxes list when a task is marked as completed
            self.checkboxesStates = []

            # Unprint added tasks container
            self.addedTasksFrame.pack_forget()

            # Create and print added tasks container again
            self.addedTasksFrame = ctk.CTkScrollableFrame(self,
                                                      fg_color = DARK_GRAY,
                                                      scrollbar_button_color = WHITE,
                                                      scrollbar_button_hover_color = WHITE)
            
            self.addedTasksFrame.pack(padx = 10, pady = 10)

            # Get inbox rows number
            cursor.execute("SELECT COUNT (label) FROM inbox")
            # Use rows number as an index
            tasksNumber = cursor.fetchone()[0]

            b = self.checkedTaskIndex
            c = self.checkedTaskIndex + 1

            for a in range(tasksNumber):
                # Use deleted task index on other remaining tasks
                cursor.execute("UPDATE inbox SET id = ? WHERE id = ?", (b, c,))
                
                # Go to the next task to set its new index
                c += 1
                b += 1
            
            # Save modified database
            connection.commit()

        # With the database open, get all the tasks labels
        cursor.execute("SELECT label FROM inbox")
        taskNames = cursor.fetchall()

        a = 0

        for taskName in taskNames:
            # Append something to checkboxes list and then replace that item to a checkbox variable
            self.checkboxesStates.append("X")
            self.checkboxesStates[a] = ctk.StringVar()
            
            # Go through every added task and create its container and checkbox
            taskFrame = ctk.CTkFrame(self.addedTasksFrame,
                                     fg_color = DARKER_GRAY)

            taskCheckbox = ctk.CTkCheckBox(taskFrame,
                                           width = 0,
                                           checkbox_width = 20,
                                           checkbox_height = 20,
                                           border_width = 1,
                                           fg_color = DARKER_GRAY,
                                           border_color = WHITE,
                                           hover_color = LIGHT_GRAY,
                                           text = None,
                                           variable = self.checkboxesStates[a],
                                           command = self.completeTask)
            
            # Set a different textbox height based on task name length
            self.taskNameCharsNumber = len(taskName)

            if self.taskNameCharsNumber <= 18:
                self.textboxHeight = 25
            
            else:
                self.textboxHeight = 50

            # Create task name textbox
            self.taskTextbox = ctk.CTkTextbox(taskFrame,
                                              height = self.textboxHeight,
                                              wrap = "word",
                                              activate_scrollbars = False,
                                              fg_color = DARKER_GRAY,
                                              text_color = WHITE,
                                              font = self.taskNameFont)
            
            # Add task name as the textbox default value
            self.taskTextbox.insert(1.0, taskName[0])

            # Create bindings to expand and collapse textbox on hover and off hover
            self.taskTextbox.bind("<Enter>", lambda event: self.expandTaskTextbox(event))
            self.taskTextbox.bind("<Leave>", lambda event: self.collapseTaskTextbox(event))

            # Print previous widgets in the added tasks container
            taskFrame.pack(fill = "x", padx = (0, 2), pady = (0, 2))
            taskCheckbox.pack(side = "left", padx = (5, 0))
            self.taskTextbox.pack(side = "left", pady = 5, padx = (0, 5))

            # Go to the next checkboxes list item
            a += 1

        # Close database
        connection.close()

        # Update project tasks counter
        self.updateTaskCounter()
        
        # Make available update tasks when a task is deleted
        self.isFirstTime = False

    def addTask(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Get inbox rows number
        cursor.execute("SELECT COUNT (label) FROM inbox")
        # Use rows number as an index
        tasksNumber = cursor.fetchone()[0]
        a = tasksNumber + 1
        b = tasksNumber

        # Append entry field text as a new task in the database with an identifier
        cursor.execute("INSERT INTO inbox (id, label) VALUES (?, ?)", (a, self.entryValue.get(),))
        # Save modified database
        connection.commit()

        # Append something to checkboxes list and then replace that item to a checkbox variable
        self.checkboxesStates.append("X")
        self.checkboxesStates[b] = ctk.StringVar()

        # Get the task label from the database
        cursor.execute("SELECT label FROM inbox WHERE id = ?", (a,))
        taskName = cursor.fetchone()
        
        # Close database
        connection.close()
        
        # Create added task container and checkbox
        taskFrame = ctk.CTkFrame(self.addedTasksFrame,
                                 fg_color = DARKER_GRAY)

        taskCheckbox = ctk.CTkCheckBox(taskFrame,
                                       width = 0,
                                       checkbox_width = 20,
                                       checkbox_height = 20,
                                       border_width = 1,
                                       fg_color = DARKER_GRAY,
                                       border_color = WHITE,
                                       hover_color = LIGHT_GRAY,
                                       text = None,
                                       variable = self.checkboxesStates[b],
                                       command = self.completeTask)
        
        # Set a different textbox height based on task name length
        self.taskNameCharsNumber = len(taskName[0])

        if self.taskNameCharsNumber <= 18:
            self.textboxHeight = 25
        
        else:
            self.textboxHeight = 50

        # Create task name textbox
        self.taskTextbox = ctk.CTkTextbox(taskFrame,
                                          height = self.textboxHeight,
                                          wrap = "word",
                                          activate_scrollbars = False,
                                          fg_color = DARKER_GRAY,
                                          text_color = WHITE,
                                          font = self.taskNameFont)
        
        # Add task name as the textbox default value
        self.taskTextbox.insert(1.0, taskName[0])

        # Create bindings to expand and collapse textbox on hover and off hover
        self.taskTextbox.bind("<Enter>", lambda event: self.expandTaskTextbox(event))
        self.taskTextbox.bind("<Leave>", lambda event: self.collapseTaskTextbox(event))

        # Print previous widgets in the added tasks container
        taskFrame.pack(fill = "x", padx = (0, 2), pady = (0, 2))
        taskCheckbox.pack(side = "left", padx = (5, 0))
        self.taskTextbox.pack(side = "left", pady = 5, padx = (0, 5))

        # Clear added task name
        AddTaskWindow.clearPlaceholder(self)

        # Update project tasks counter
        self.updateTaskCounter()

    def openAddTaskWindow(self):
        # Open add task window
        AddTaskWindow(self.entryValue, self.addTask)

    def completeTask(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Get inbox rows number
        cursor.execute("SELECT COUNT (label) FROM inbox")
        # Use rows number as an index
        tasksNumber = cursor.fetchone()[0]

        for a in range(tasksNumber):
            if self.checkboxesStates[a].get() == "1":
                b = a + 1
                
                # Capture checked task id
                self.checkedTaskIndex = b

                # Check every checkbox variable and delete the one that is checked
                cursor.execute("DELETE FROM inbox WHERE id = ?", (b,))
                # Save modified database
                connection.commit()

                # Rebuild remaining tasks
                self.restoreTasks()
                # Do not consider other checked tasks below this one
                break

        # Close database
        connection.close()

    def updateTaskCounter(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Get inbox task number
        cursor.execute("SELECT COUNT (label) FROM inbox")
        tasksNumber = cursor.fetchone()[0]

        # Update project tasks counter
        self.tasksNumber.set(value = tasksNumber)

    def expandTaskTextbox(self, event):
        # Set textbox height to 3
        event.widget.configure(height = 3)

    def collapseTaskTextbox(self, event):
        # Go back to the previous textbox height
        event.widget.configure(height = 1)

class AddTaskWindow(ctk.CTkToplevel):
    def __init__(self, entryValue, addTask):
        super().__init__(fg_color = DARKER_GRAY)

        # Set window title and size
        self.title("")
        self.geometry("230x100+1300+300")
        self.resizable(False, False)
        # Focus this window
        self.grab_set()

        # Make external attributes and methods local
        self.entryValue = entryValue
        self.addTask = addTask

        # Create and print widgets
        self.createWidgets()

    def createWidgets(self):
        # Create font
        entriesFont = ctk.CTkFont(family = FONT_FAMILY,
                                       size = TASK_NAME_SIZE)

        # Create entries container, add task entry and add description entry
        inputFrame = ctk.CTkFrame(self,
                                  fg_color = DARKER_GRAY)

        taskNameEntry = ctk.CTkEntry(inputFrame,
                                     text_color = WHITE,
                                     font = entriesFont,
                                     border_color = DARK_GRAY,
                                     fg_color = DARK_GRAY,
                                     textvariable = self.entryValue)
        
        taskDescriptionEntry = ctk.CTkEntry(inputFrame,
                                            border_color = DARK_GRAY,
                                            fg_color = DARK_GRAY)

        # Print previously created widgets
        inputFrame.pack(fill = "x")
        taskNameEntry.pack(pady = (10, 5))
        taskDescriptionEntry.pack(pady = (5, 10))

        # Set placeholder everytime the window is open
        self.entryValue.set("Enter task name")
        # Clear placeholder when task name entry is focus
        taskNameEntry.bind("<FocusIn>", lambda event: self.clearPlaceholder())

        # Create keyboard shortcuts
        self.bind("<Return>", lambda event: self.addTask())
        self.bind("<Escape>", lambda event: self.closeWindow())

    def closeWindow(self):
        # Close add task window
        self.destroy()

    def clearPlaceholder(self):
        self.entryValue.set("")

    def restorePlaceholder(self):
        self.entryValue.set("Enter task name")