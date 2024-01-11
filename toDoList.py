from settings import *
import customtkinter as ctk
import tkinter as tk
import sqlite3 as db

class Project(ctk.CTkFrame):
    def __init__(self, parent, projectName, shortcut, window):
        # Set container master and color
        super().__init__(master = parent, fg_color = BLACK)

        # Make available here all those external attributes, methods and parameters
        self.projectName = projectName
        self.hotkey = shortcut
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

        # Create project tasks table (with task id and task name columns) in the database
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.projectName} (id INTEGER, name TEXT)")

        # Close database
        connection.close()
        
        # Create and print widgets, restore previously added tasks when relaunching the app
        self.createWidgets()
        self.restoreTasks()

    def createWidgets(self):
        # Create fonts
        projectNameFont = ctk.CTkFont(family = FONT_FAMILY,
                           size = M)
        
        projectTaskCounterFont = ctk.CTkFont(family = FONT_FAMILY,
                                       size = XS)
        
        self.taskNameFont = ctk.CTkFont(family = FONT_FAMILY,
                                        size = S)

        # Create project container, project name label, task counter label and add task button
        projectFrame = ctk.CTkFrame(self,
                                    fg_color = BLACK)
        
        projectName = ctk.CTkLabel(projectFrame,
                                    text = self.projectName,
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

        # Create keyboard shortcuts based on user definition
        self.window.bind(f"<Alt-KeyPress-{self.hotkey}>", lambda event: self.openAddTaskWindow())

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

            # Get project table rows number
            cursor.execute(f"SELECT COUNT (name) FROM {self.projectName}")
            # Use rows number as an index
            tasksNumber = cursor.fetchone()[0]

            b = self.checkedTaskIndex
            c = self.checkedTaskIndex + 1

            for a in range(tasksNumber):
                # Set deleted task index on other remaining tasks
                cursor.execute(f"UPDATE {self.projectName} SET id = ? WHERE id = ?", (b, c,))
                
                # Go to the next task to set its new index
                c += 1
                b += 1
            
            # Save modified database
            connection.commit()

        # With the database open, get all the tasks names
        cursor.execute(f"SELECT name FROM {self.projectName}")
        taskNames = cursor.fetchall()

        a = 0

        for taskName in taskNames:
            # Append something to checkboxes list and then replace that item to a checkbox variable
            self.checkboxesStates.append("X")
            self.checkboxesStates[a] = ctk.StringVar()
            
            # Go through every added task and create its container and checkbox
            taskFrame = ctk.CTkFrame(self.addedTasksFrame,
                                     fg_color = BLACK)

            taskCheckbox = ctk.CTkCheckBox(taskFrame,
                                           width = 0,
                                           checkbox_width = 20,
                                           checkbox_height = 20,
                                           border_width = 1,
                                           fg_color = BLACK,
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
                                              fg_color = BLACK,
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

        # Get project table rows number
        cursor.execute(f"SELECT COUNT (name) FROM {self.projectName}")
        # Use rows number as an index
        tasksNumber = cursor.fetchone()[0]
        a = tasksNumber + 1
        b = tasksNumber

        # Append entry field text as a new task in the database with an identifier
        cursor.execute(f"INSERT INTO {self.projectName} (id, name) VALUES (?, ?)", (a, self.entryValue.get(),))
        # Save modified database
        connection.commit()

        # Append something to checkboxes list and then replace that item to a checkbox variable
        self.checkboxesStates.append("X")
        self.checkboxesStates[b] = ctk.StringVar()

        # Get the task name from the database
        cursor.execute(f"SELECT name FROM {self.projectName} WHERE id = ?", (a,))
        taskName = cursor.fetchone()
        
        # Close database
        connection.close()
        
        # Create added task container and checkbox
        taskFrame = ctk.CTkFrame(self.addedTasksFrame,
                                 fg_color = BLACK)

        taskCheckbox = ctk.CTkCheckBox(taskFrame,
                                       width = 0,
                                       checkbox_width = 20,
                                       checkbox_height = 20,
                                       border_width = 1,
                                       fg_color = BLACK,
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
                                          fg_color = BLACK,
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

        # Get project table rows number
        cursor.execute(f"SELECT COUNT (name) FROM {self.projectName}")
        # Use rows number as an index
        tasksNumber = cursor.fetchone()[0]

        for a in range(tasksNumber):
            if self.checkboxesStates[a].get() == "1":
                b = a + 1
                
                # Capture checked task id
                self.checkedTaskIndex = b

                # Go through every checkbox variable and delete the one that is checked
                cursor.execute(f"DELETE FROM {self.projectName} WHERE id = ?", (b,))
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

        # Get project table task number
        cursor.execute(f"SELECT COUNT (name) FROM {self.projectName}")
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
        super().__init__(fg_color = BLACK)

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
                                       size = S)

        # Create entries container, add task entry and add description entry
        inputFrame = ctk.CTkFrame(self,
                                  fg_color = BLACK)

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

class ProjectManagementBar(ctk.CTkFrame):
    def __init__(self, parent, window):
        # Set project management container master and color
        super().__init__(master = parent, fg_color = BLACK)

        # Bring the app general container here
        self.window = window

        # Create add new project entry variable
        self.projectName = ctk.StringVar(value = "newProject")

        # Create and print widgets, restore third project
        self.createWidgets()
        self.createBindings()
        self.restoreProject()

    def createWidgets(self):
        # Create font
        font = ctk.CTkFont(family = FONT_FAMILY,
                           size = M)
        
        # Create set project name entry, add button and delete button
        self.setProjectNameEntry = ctk.CTkEntry(self,
                                        width = 120,
                                        fg_color = DARK_GRAY,
                                        border_color = DARK_GRAY,
                                        text_color = WHITE,
                                        font = font,
                                        textvariable = self.projectName)
        
        addProjectButton = ctk.CTkButton(self,
                                         width = 30,
                                         height = 30,
                                         fg_color = DARK_GRAY,
                                         hover_color = LIGHT_GRAY,
                                         text = "+",
                                         text_color = WHITE,
                                         font = font,
                                         command = self.addProject)
        
        deleteProjectButton = ctk.CTkButton(self,
                                            width = 30,
                                            height = 30,
                                            fg_color = DARK_GRAY,
                                            hover_color = LIGHT_GRAY,
                                            text = "-",
                                            text_color = WHITE,
                                            font = font,
                                            command = self.deleteProject)
        
        # Print previously created widgets
        self.setProjectNameEntry.pack(side = "left", padx = 10, pady = 10)
        deleteProjectButton.pack(side = "right", padx = (2.5, 10), pady = 10)
        addProjectButton.pack(side = "right", padx = (10, 2.5), pady = 10)
        # Print general container itself
        self.pack(fill = "x")

    def createBindings(self):
        # When focus is on setProjectNameEntry, clear placeholder; pressing enter when focus is on setProjectNameEntry, add project;
        # When losing setProjectNameEntry focus, restore placeholder
        self.setProjectNameEntry.bind("<FocusIn>", lambda event: self.clearPlaceholder())
        self.setProjectNameEntry.bind("<FocusOut>", lambda event: self.restorePlaceholder())
        self.setProjectNameEntry.bind("<Return>", lambda event: self.addProject())

    def addProject(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Get database tables number
        cursor.execute("SELECT COUNT (*) FROM sqlite_master WHERE type = 'table'")
        tablesNumber = cursor.fetchone()[0]

        # Get whatever the setProjectNameEntry has
        projectName = self.projectName.get()
        # Set as add task shortcut the combination of Alt + shortcut
        shortcut = tablesNumber + 1

        if tablesNumber == 2:
            # Create and SHOW new project as long as there is space on the app 
            Project(self.window, projectName, shortcut, self.window)

        else:
            # Create but DO NOT SHOW new project if there's a third project that is being showed
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.projectName.get()} (id INTEGER, name TEXT)")

        # Close database
        connection.close()

        self.restorePlaceholder()
        self.loseCurrentFocus()

    def restoreProject(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Get database tables number
        cursor.execute("SELECT COUNT (*) FROM sqlite_master WHERE type = 'table'")
        tablesNumber = cursor.fetchone()[0]

        if tablesNumber >= 3:
            # Get all database tables names
            cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            projectsNames = cursor.fetchall()

            for projectName in projectsNames:
                # Go through every table name and store the last one
                projectName = projectName[0]
            
            # Set as add task shortcut the combination of Alt + shortcut
            shortcut = tablesNumber

            # Restore third project when reopening app (if it exists)
            Project(self.window, projectName, shortcut, self.window)

        # Close database
        connection.close()

    def deleteProject(self):
        # Open window to select project to delete
        deleteProjectWindow()

    def clearPlaceholder(self):
        # Clear placeholder when pressing on setProjectNameEntry
        self.projectName.set(value = "")

    def restorePlaceholder(self):
        self.projectName.set(value = "newProject")

    def loseCurrentFocus(self):
        # Set focus on the window instead of anything else
        self.window.focus()

class deleteProjectWindow(ctk.CTkToplevel):
    def __init__(self):
        # Set window color, title, size and position
        super().__init__(fg_color = BLACK)
        self.title("")
        self.geometry("230x50+1300+500")
        self.resizable(False, False)
        # Focus on this window
        self.grab_set()

        # Create variable to store project to delete name
        self.projectToDelete = ctk.StringVar()

        # Create fonts, create and print widgets, create shortcuts
        self.createFonts()
        self.createWidgets()
        self.createBindings()

    def createFonts(self):
        # Create widgets fonts
        self.selectedOptionFont = ctk.CTkFont(family = FONT_FAMILY, size = S, weight = "normal")
        self.otherOptionsFont = ctk.CTkFont(family = FONT_FAMILY, size = XS, weight = "normal")
        self.buttonFont = ctk.CTkFont(family = FONT_FAMILY, size = S, weight = "normal")

    def createWidgets(self):
        # Create list with the added projects names
        self.createProjectsNamesList()

        # Create deletable projects menu
        deletableProjectsMenu = ctk.CTkOptionMenu(self,
                                                  width = 150,
                                                  fg_color = DARK_GRAY,
                                                  button_color = DARK_GRAY,
                                                  button_hover_color = LIGHT_GRAY,
                                                  dropdown_fg_color = DARK_GRAY,
                                                  dropdown_hover_color = LIGHT_GRAY,
                                                  text_color = WHITE,
                                                  dropdown_text_color = WHITE,
                                                  font = self.selectedOptionFont,
                                                  dropdown_font = self.otherOptionsFont,
                                                  values = self.projectsNamesList,
                                                  variable = self.projectToDelete)
        
        # Print previously created widgets
        deletableProjectsMenu.pack(pady = 10)

    def createBindings(self):
        # Delete project when pressing enter, close window when pressing escape
        self.bind("<Return>", lambda event: self.deleteProject())
        self.bind("<Escape>", lambda event: self.closeWindow())

    def closeWindow(self):
        # Close window when escape is pressed
        self.destroy()

    def createProjectsNamesList(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Get all database tables names
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        projectsNames = cursor.fetchall()

        # Close database
        connection.close()

        # Clear added projects list
        self.projectsNamesList = []

        # Fill emptied list with currently added projects names
        for projectName in projectsNames:
            self.projectsNamesList.append(projectName[0])

        # Do not consider main projects like Inbox and Due
        self.projectsNamesList.remove("Inbox")
        self.projectsNamesList.remove("Due")

    def deleteProject(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()

        # Delete selected project table from database
        cursor.execute(f"DROP TABLE {self.projectToDelete.get()}")

        # Save modified database and close it
        connection.commit()
        connection.close()


