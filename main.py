from settings import *
from toDoList import *
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import sqlite3 as db

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color = BLACK)

        # Set window title, icon, size and position
        self.title("")
        self.iconbitmap("images/icon.ico")
        self.geometry("230x380+1680+0")
        self.resizable(False, False)

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

        # Print timers container, pomodoro timer container, eating timer container, inbox project container, project management bar container and
        # due project container in the window
        timersFrame = TimersContainer(self)
        
        PomodoroTimer(timersFrame,
                      self.isTimer1Running,
                      self.isTimer2Running,
                      self.bother,
                      self.isBothering,
                      self,
                      self.afterId)
        
        EatingTimer(timersFrame,
                    self.isTimer2Running,
                    self.isTimer1Running,
                    self.bother,
                    self)
        
        Project(self,
                "Inbox",
                1,
                self)
        
        # Show reminder to start a timer
        self.bother()

        # Execute the app
        self.mainloop()

    def bother(self):
        if self.isTimer1Running.get() == False and self.isTimer2Running.get() == False:
            # Tell pomodoro timer to wait before showing another unnecesary alert when no timer is running
            self.isBothering.set(value = True)

            # Show windows and pin it on the screen
            self.state(newstate = "normal")
            self.attributes("-topmost", True)
            # Show the start a timer reminder and unpin window when alert is closed
            messagebox.showerror(message = "Start a timer", type = "ok")
            self.attributes("-topmost", False)
            
            # Show that reminder every minute and store its cancel id to stop it later
            identifier = self.after(60000, self.bother)
            self.afterId.set(value = identifier)

        else:
            # Tell pomodoro timer that is okay to show an alert because there is no active alert right now
            self.isBothering.set(value = False)

class TimersContainer(ctk.CTkFrame):
    def __init__(self, parent):
        # Set container master and color
        super().__init__(master = parent,
                         fg_color = BLACK)
        
        # Print container itself
        self.pack(fill = "x")

class PomodoroTimer(ctk.CTkFrame):
    def __init__(self, parent, isTimer1Running, isTimer2Running, bother, isBothering, window, afterId):
        # Set pomodoro timer master and container color
        super().__init__(master = parent, fg_color = BLACK)

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

    def createWidgets(self):
        # Create font
        timerFont = ctk.CTkFont(family = FONT_FAMILY,
                           size = XL,
                           weight = "bold")

        # Create icons for reset and skip buttons
        resetIcon = ctk.CTkImage(dark_image = Image.open("images/reset.png"),
                                 size = (20, 20))
        
        self.skipIcon = ctk.CTkImage(dark_image = Image.open("images/skipDisabled.png"),
                                     size = (20, 20))

        # Create time interactive label
        self.timeLabel = ctk.CTkButton(self,
                                       width = 100,
                                       height = 50,
                                       fg_color = DARK_GRAY,
                                       hover_color = LIGHT_GRAY,
                                       command = self.triggerTimer,
                                       text_color = WHITE,
                                       font = timerFont)
        
        # Create buttons container, reset button and skip button
        buttonsFrame = ctk.CTkFrame(self,
                                    fg_color = BLACK)

        resetButton = ctk.CTkButton(buttonsFrame,
                                    width = 30,
                                    height = 30,
                                    fg_color = BLACK,
                                    hover_color = DARK_GRAY,
                                    text = "",
                                    image = resetIcon,
                                    command = self.resetTimer)
        
        skipButton = ctk.CTkButton(buttonsFrame,
                                   width = 30,
                                   height = 30,
                                   fg_color = BLACK,
                                   hover_color = DARK_GRAY,
                                   text = "",
                                   image = self.skipIcon,
                                   command = self.skipTimer)

        # Print created widgets in the global container
        self.timeLabel.pack()
        buttonsFrame.pack()
        resetButton.pack(side = "left")
        skipButton.pack(side = "left")
        # Print global container itself
        self.pack(side = "left", padx = 10, pady = 10)

        # Create start/stop shortcut
        self.window.bind("<Alt-KeyPress-q>", lambda event: self.triggerTimer())

    def triggerTimer(self):
        if self.isTimerRunning.get() == False:
            # Put skip button enabled icon when the timer is running
            self.skipIcon.configure(dark_image = Image.open("images/skipEnabled.png"))

            # Start pomodoro timer but stop eating timer
            self.isTimerRunning.set(value = True)
            self.isTimer2Running.set(value = False)

            # Create pomodoro timer buttons shortcuts when it is started
            self.window.bind("<Alt-KeyPress-r>", lambda event: self.resetTimer())
            self.window.bind("<Alt-KeyPress-s>", lambda event: self. skipTimer())

            if self.isFirstTimeRunning == True:
                # Start counting but only once
                self.updateTimer()
                self.isFirstTimeRunning = False

        else:
            # Put skip button disabled icon when the timer is stopped
            self.skipIcon.configure(dark_image = Image.open("images/skipDisabled.png"))

            # Stop counting
            self.isTimerRunning.set(value = False)

            # Delete pomodoro timer buttons shortcuts when it is stopped
            self.window.unbind("<Alt-KeyPress-r>")
            self.window.unbind("<Alt-KeyPress-s>")

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
        super().__init__(master = parent, fg_color = BLACK)

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

    def createWidgets(self):
        # Create font
        timerFont = ctk.CTkFont(family = FONT_FAMILY,
                           size = XL,
                           weight = "bold")

        # Create icons for reset and switch time buttons
        resetIcon = ctk.CTkImage(light_image = Image.open("images/reset.png"),
                                 size = (20, 20))
        
        switchTimeIcon = ctk.CTkImage(light_image = Image.open("images/switchTime.png"),
                                      size = (20, 20))

        # Create time interactive label
        self.timeLabel = ctk.CTkButton(self,
                                       width = 100,
                                       height = 50,
                                       fg_color = DARK_GRAY,
                                       hover_color = LIGHT_GRAY,
                                       text_color = WHITE,
                                       font = timerFont,
                                       command = self.triggerTimer)
        
        # Create buttons container, reset button and switch time button
        buttonsFrame = ctk.CTkFrame(self,
                                    fg_color = BLACK)
        
        resetButton = ctk.CTkButton(buttonsFrame,
                                    width = 30,
                                    height = 30,
                                    fg_color = BLACK,
                                    hover_color = DARK_GRAY,
                                    text = "",
                                    image = resetIcon,
                                    command = self.resetTimer)
        
        switchTimeButton = ctk.CTkButton(buttonsFrame,
                                         width = 30,
                                         height = 30,
                                         fg_color = BLACK,
                                         hover_color = DARK_GRAY,
                                         text = "",
                                         image = switchTimeIcon,
                                         command = self.switchTimer)

        # Print created widgets in the global container
        self.timeLabel.pack()
        buttonsFrame.pack()
        resetButton.pack(side = "left")
        switchTimeButton.pack(side = "left")
        # Print global container itself
        self.pack(side = "left")

        # Create start/stop shortcut
        self.window.bind("<Alt-KeyPress-e>", lambda event: self.triggerTimer())

    def triggerTimer(self):
        if self.isTimerRunning.get() == False:
            # Start eating timer but stop pomodoro timer
            self.isTimerRunning.set(value = True)
            self.isTimer1Running.set(value = False)

            # Create eating timer buttons shortcuts when it is started
            self.window.bind("<Alt-KeyPress-r>", lambda event: self.resetTimer())
            self.window.bind("<Alt-KeyPress-s>", lambda event: self. switchTimer())
            
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

            # Delete eating timer buttons shortcuts when it is stopped
            self.window.unbind("<Alt-KeyPress-r>")
            self.window.unbind("<Alt-KeyPress-s>")
            
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

App()