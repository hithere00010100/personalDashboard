from settings import *
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import sqlite3 as db

class App():
    def __init__(self):
        self.window = ctk.CTk()

        # Set window title, size and position
        self.window.title("")
        self.window.geometry("230x400+1600+100")
        self.window.resizable(False, False)

        # Set window dark mode and color accent
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Set both timers initial states
        self.isTimer1Running = ctk.BooleanVar(value = False)
        self.isTimer2Running = ctk.BooleanVar(value = False)

        # Create essential variables for later use
        self.isBothering = ctk.BooleanVar()
        self.afterId = ctk.StringVar()

        # Create tasks database
        connection = db.connect("tasks.db")
        connection.close()

        # Create timers container
        timersFrame = ctk.CTkFrame(self.window)
        timersFrame.pack(fill = "x")

        # Print pomodoro timer, eating timer and inbox components in the global container
        PomodoroTimer(timersFrame, self.isTimer1Running, self.isTimer2Running, self.bother, self.isBothering, self.window, self.afterId)
        EatingTimer(timersFrame, self.isTimer2Running, self.isTimer1Running, self.bother, self.window)
        Inbox(self.window)

        # Show reminder to start a timer
        self.bother()

        # Execute the app
        self.window.mainloop()

    def bother(self):
        if self.isTimer1Running.get() == False and self.isTimer2Running.get() == False:
            # Tell pomodoro timer to wait before showing another unnecesary alert when no timer is running
            self.isBothering.set(value = True)

            # Show windows and pin it on the screen
            self.window.state(newstate = "normal")
            self.window.attributes("-topmost", True)
            # Show the start a timer reminder and unpin window when alert is closed
            messagebox.showerror(message = "Start a timer", type = "ok")
            self.window.attributes("-topmost", False)
            
            # Show that reminder every minute and store its cancel id to stop it later
            identifier = self.window.after(60000, self.bother)
            self.afterId.set(value = identifier)

        else:
            # Tell pomodoro timer that is okay to show an alert because there is no active alert right now
            self.isBothering.set(value = False)

class PomodoroTimer(ctk.CTkFrame):
    def __init__(self, parent, isTimer1Running, isTimer2Running, bother, isBothering, window, afterId):
        # Set pomodoro timer master and container color
        super().__init__(master = parent, fg_color = DARKER_GRAY)

        # Make available here those external variables and methods
        self.isTimerRunning = isTimer1Running
        self.isTimer2Running = isTimer2Running
        self.bother = bother
        self.isBothering = isBothering
        self.window = window
        self.afterId = afterId
        
        # Set initial conditions
        self.isFirstTimeRunning = True
        self.isFocusTime = True
        self.skip = False

        # Create widgets and set timer to focus time
        self.createWidgets()
        self.resetTimer()

        # Create keyboard shortcuts
        self.window.bind("<KeyPress-1>", lambda event: self.triggerTimer())
        self.window.bind("<KeyPress-r>", lambda event: self.resetTimer())
        self.window.bind("<KeyPress-s>", lambda event: self. skipTimer())

    def createWidgets(self):
        # Set font
        font = ctk.CTkFont(family = FONT_FAMILY, size = TIMERS_SIZE, weight = "bold")

        # Create reset and skip buttons' dark mode icons with the proper size
        resetIcon = ctk.CTkImage(dark_image = Image.open("images/reset.png"), size = (20, 20))
        self.skipIcon = ctk.CTkImage(dark_image = Image.open("images/skipDisabled.png"), size = (20, 20))

        # Create and set time label properties
        self.timeLabel = ctk.CTkButton(self, width = 100, height = 50, fg_color = DARK_GRAY, hover_color = LIGHT_GRAY, font = font, command = self.triggerTimer)
        
        # Create buttons container
        buttonsFrame = ctk.CTkFrame(self)

        # Create and set reset button properties
        resetButton = ctk.CTkButton(buttonsFrame, width = 1, fg_color = DARKER_GRAY, hover_color = DARK_GRAY, command = self.resetTimer,
                                    text = "", image = resetIcon)
        
        # Create and set skip button properties
        skipButton = ctk.CTkButton(buttonsFrame, width = 1, fg_color = DARKER_GRAY, hover_color = DARK_GRAY, command = self.skipTimer,
                                   text = "", image = self.skipIcon)

        # Print those widgets in the global container
        self.timeLabel.pack()
        buttonsFrame.pack()
        resetButton.pack(side = "left")
        skipButton.pack(side = "left")
        # Print container itself
        self.pack(side = "left", padx = 10)

    def triggerTimer(self):
        if self.isTimerRunning.get() == False:
            # Put skip button enabled icon when the timer is running
            self.skipIcon.configure(dark_image = Image.open("images/skipEnabled.png"))

            # Start pomodoro timer but stop eating timer
            self.isTimerRunning.set(value = True)
            self.isTimer2Running.set(value = False)

            if self.isFirstTimeRunning == True:
                # Start counting but only once
                self.updateTimer()
                self.isFirstTimeRunning = False

        else:
            # Put skip button disabled icon when the timer is stopped
            self.skipIcon.configure(dark_image = Image.open("images/skipDisabled.png"))

            # Stop counting
            self.isTimerRunning.set(value = False)

            if self.isBothering.get() == False:
                # Show start a timer reminder every minute as long as there's no active alerts
                self.bother()

            else:
                # Cancel current bother loop (using its id) to start a new one
                self.after_cancel(self.afterId.get())
                self.bother()

    def updateTimer(self):
        if self.isTimerRunning.get() == True:
            # Reduce a second and set that reduced value in the time label
            self.time -= 1
            minutes, seconds = divmod(self.time, 60)
            self.timeLabel.configure(text = "{:02d}:{:02d}".format(minutes, seconds))

            if self.time == 0 or self.skip == True:
                if self.baseTime == FOCUS_TIME:
                    # Set break time block if previous time was focus time
                    self.isFocusTime = False

                else:
                    # Set focus time block if previous time was break time
                    self.isFocusTime = True

                # Turn off timer, show start a timer reminder and set time based on previous selection
                self.triggerTimer()
                self.resetTimer()

        # Keep counting every second
        self.after(1000, self.updateTimer)

    def resetTimer(self):
        if self.isFocusTime == True:
            # Set focus time if current block time is focus
            self.time = FOCUS_TIME
        
        else:
            # Set break time if current block time is break
            self.time = BREAK_TIME

        # Store the complete assigned time as a base to compare later
        self.baseTime = self.time

        # Turn off skip flag and show updated time label with 35 or 10 min
        self.skip = False
        minutes, seconds = divmod(self.time, 60)
        self.timeLabel.configure(text = "{:02d}:{:02d}".format(minutes, seconds))

    def skipTimer(self):
        if self.isTimerRunning.get() == True:
            # Turn on skip flag as long as pomodoro timer is running
            self.skip = True

class EatingTimer(ctk.CTkFrame):
    def __init__(self, parent, isTimer2Running, isTimer1Running, bother, window):
        # Set eating timer master, container color and font
        super().__init__(master = parent, fg_color = DARKER_GRAY)

        # Make available here those external variables and methods
        self.isTimerRunning = isTimer2Running
        self.isTimer1Running = isTimer1Running
        self.bother = bother
        self.window = window

        # Set initial conditions
        self.isFirstTimeRunning = True
        self.isLunchTime = True

        # Create widgets and set timer to lunch time
        self.createWidgets()
        self.resetTimer()

        # Create keyboard shortcuts
        self.window.bind("<KeyPress-2>", lambda event: self.triggerTimer())
        self.window.bind("<Alt-KeyPress-r>", lambda event: self.resetTimer())
        self.window.bind("<Alt-KeyPress-s>", lambda event: self. switchTimer())

    def createWidgets(self):
        # Set font
        font = ctk.CTkFont(family = FONT_FAMILY, size = TIMERS_SIZE, weight = "bold")

        # Create reset and switch time buttons' dark mode icons with the proper size
        resetIcon = ctk.CTkImage(light_image = Image.open("images/reset.png"), size = (20, 20))
        switchTimeIcon = ctk.CTkImage(light_image = Image.open("images/switchTime.png"), size = (20, 20))

        # Create and set time label properties
        self.timeLabel = ctk.CTkButton(self, width = 100, height = 50, fg_color = DARK_GRAY, hover_color = LIGHT_GRAY, command = self.triggerTimer,
                                       font = font)
        
        # Create buttons container
        buttonsFrame = ctk.CTkFrame(self)
        
        # Create and set reset button properties
        resetButton = ctk.CTkButton(buttonsFrame, width = 1, fg_color = DARKER_GRAY, hover_color = DARK_GRAY, command = self.resetTimer, text = "",
                                    image = resetIcon)
        
        # Create and set switch time button properties
        switchTimeButton = ctk.CTkButton(buttonsFrame, width = 1, fg_color = DARKER_GRAY, hover_color = DARK_GRAY, command = self.switchTimer, text = "",
                                         image = switchTimeIcon)

        # Print those widgets in the global container
        self.timeLabel.pack()
        buttonsFrame.pack()
        resetButton.pack(side = "left")
        switchTimeButton.pack(side = "left")
        # Print container itself
        self.pack(side = "left")

    def triggerTimer(self):
        if self.isTimerRunning.get() == False:
            # Start eating timer but stop pomodoro timer
            self.isTimerRunning.set(value = True)
            self.isTimer1Running.set(value = False)
            
            # Start timer only once
            if(self.isFirstTimeRunning == True):
                # Start counting but only once
                self.isFirstTimeRunning = False
                self.updateTimer()
        
        # Stop timer when stop button is pressed
        else:
            # Stop counting and show start a timer reminder
            self.isTimerRunning.set(value = False)
            self.bother()

    def updateTimer(self):
        if self.isTimerRunning.get() == True:
            # Reduce a second and set that reduced value in the time label
            self.time -= 1
            minutes, seconds = divmod(self.time, 60)
            self.timeLabel.configure(text = "{:02d}:{:02d}".format(minutes, seconds))

            if self.time == 0:
                # Turn off timer, show start a timer reminder and set time based on current mode (lunch or dinner)
                self.triggerTimer()
                self.resetTimer()

        # Keep counting every second
        self.after(1000, self.updateTimer)

    def resetTimer(self):
        if self.isLunchTime == True:
            # Set timer's time to 15 min if current moe is lunch
            self.time = LUNCH_TIME

        else:
            # Set timer's time to 10 min if current mode is dinner
            self.time = DINNER_TIME
        
        # Show updated time label with 15 or 10 min
        minutes, seconds = divmod(self.time, 60)
        self.timeLabel.configure(text = "{:02d}:{:02d}".format(minutes, seconds))

    def switchTimer(self):
        if self.isLunchTime == True:
            # Switch to dinner time when switch button is pressed and previous timer was lunch time
            self.isLunchTime = False

        else:
            # Switch to lunch time when switch button is pressed and previous timer was dinner time
            self.isLunchTime = True

        # Show updated time label with 15 or 10 min
        self.resetTimer()

class Inbox(ctk.CTkFrame):
    def __init__(self, parent):
        # Set component master
        super().__init__(master = parent)

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
        
        # Create and print widgets, restore previously added tasks when relaunching the app and start watching checkboxes states changes
        self.createWidgets()
        self.restoreTasks()
        self.completeTask()

    def createWidgets(self):
        # Create project container, name label and tasks counter
        projectFrame = ctk.CTkFrame(self)
        projectLabel = ctk.CTkLabel(projectFrame, text = "Inbox")
        projectTasksNumber = ctk.CTkLabel(projectFrame, text = "", textvariable = self.tasksNumber)

        # Create added tasks container for the first time
        self.addedTasksFrame = ctk.CTkScrollableFrame(self)

        # Create add task button container and button
        self.addTaskFrame = ctk.CTkFrame(self)
        self.addTaskButton = ctk.CTkButton(self.addTaskFrame, text = "+", height = 30, width = 30, command = self.openAddTaskWindow)
        
        # Print previous widgets in the global container
        projectFrame.pack(fill = "x")
        projectLabel.pack(side = "left")
        projectTasksNumber.pack(side = "right")

        self.addedTasksFrame.pack()

        self.addTaskFrame.pack(fill = "x")
        self.addTaskButton.pack(side = "right")

        # Print global container itself
        self.pack(fill = "x")

    def restoreTasks(self):
        # Open database
        connection = db.connect("tasks.db")
        cursor = connection.cursor()
        
        if self.isFirstTime == False:
            # Reset checkboxes list when a task is marked as completed
            self.checkboxesStates = []

            # Unprint added task frame and the rest below
            self.addedTasksFrame.pack_forget()
            self.addTaskFrame.pack_forget()

            # Create added task frame, add task button frame and button itself
            self.addedTasksFrame = ctk.CTkScrollableFrame(self)
            self.addTaskFrame = ctk.CTkFrame(self)
            self.addTaskButton = ctk.CTkButton(self.addTaskFrame, text = "+", height = 30, width = 30, command = self.openAddTaskWindow)
            
            # Print previously created widgets in the exact order
            self.addedTasksFrame.pack()
            self.addTaskFrame.pack(fill = "x")
            self.addTaskButton.pack(side = "right")

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
        tasksLabels = cursor.fetchall()

        a = 0

        for label in tasksLabels:
            # Append something to checkboxes list and then replace that item to a checkbox variable
            self.checkboxesStates.append("X")
            self.checkboxesStates[a] = ctk.StringVar()
            
            # Go through every task and create its container, checkbox and label
            taskFrame = ctk.CTkFrame(self.addedTasksFrame)
            taskInfo = ctk.CTkCheckBox(taskFrame, text = label[0], variable = self.checkboxesStates[a])

            # Print previous widgets in the added tasks container
            taskFrame.pack(fill = "x")
            taskInfo.pack(side = "left")
            
            # Go to the next checkboxes list item
            a += 1

        # Close database
        connection.close()
        
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
        label = cursor.fetchone()
        
        # Close database
        connection.close()
        
        # Create task container, checkbox and label
        taskFrame = ctk.CTkFrame(self.addedTasksFrame)
        taskInfo = ctk.CTkCheckBox(taskFrame, text = label[0], variable = self.checkboxesStates[b])

        # Print previous widgets in the added tasks container
        taskFrame.pack(fill = "x")
        taskInfo.pack(side = "left")

        # Clear added task name
        AddTaskWindow.clearPlaceholder(self)

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

        # Update tasks counter project label
        self.tasksNumber.set(value = tasksNumber)

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

        # Keep on checking checked tasks every half second
        self.after(500, self.completeTask)

class AddTaskWindow(ctk.CTkToplevel):
    def __init__(self, entryValue, addTask):
        super().__init__()

        # Set window title and size
        self.title("")
        self.geometry("200x100")
        self.resizable(False, False)

        # Make external attributes and methods local
        self.entryValue = entryValue
        self.addTask = addTask

        # Create and print widgets
        self.createWidgets()

    def createWidgets(self):
        # Create input frame, add task input and add description entry
        inputFrame = ctk.CTkFrame(self)
        taskNameEntry = ctk.CTkEntry(inputFrame, textvariable = self.entryValue)
        taskDescriptionEntry = ctk.CTkEntry(inputFrame)

        # Create add and cancel task button frame, add button and cancel button
        actionButtonsFrame = ctk.CTkFrame(self)
        cancelTaskButton = ctk.CTkButton(actionButtonsFrame, text = "Cancel", width = 1, command = self.cancelTask)
        addTaskButton = ctk.CTkButton(actionButtonsFrame, text = "Add", width = 1, command = self.addTask)

        # Print previously created widgets
        inputFrame.pack()
        taskNameEntry.pack()
        taskDescriptionEntry.pack()

        actionButtonsFrame.pack()
        cancelTaskButton.pack(side = "left")
        addTaskButton.pack(side = "left")

        # Clear placeholder when task name entry is focus
        taskNameEntry.bind("<FocusIn>", lambda event: self.clearPlaceholder())
        # Restore placeholder when task name entry losses focus
        taskNameEntry.bind("<FocusOut>", lambda event: self.restorePlaceholder())

    def cancelTask(self):
        # Close add task window
        self.destroy()

    def clearPlaceholder(self):
        self.entryValue.set("")

    def restorePlaceholder(self):
        self.entryValue.set("Enter task name")

App()