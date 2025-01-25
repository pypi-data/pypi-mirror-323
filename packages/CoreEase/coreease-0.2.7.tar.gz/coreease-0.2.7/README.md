
---

**CoreEase**  
**Why work harder when you can CoreEase?**

### What is CoreEase?  
CoreEase is a Python package designed to simplify your workflow by automating repetitive tasks, handling threads efficiently, and providing easy utilities for system operations. Whether it's managing files, automating browsers, or working with system resources, CoreEase helps you do more with less effort.

---

### Features:  

1. **Thread Management**:  
   - Execute tasks in parallel with simple threading.  
   - Includes an animated load buffer to keep things looking productive.  

2. **Browser Automation**:  
   - Headless browsing, form filling, and button clicking.  
   - Easy parsing of links, buttons, and login forms.  

3. **File Handling**:  
   - Check file existence, create files, append content, and overwrite efficiently.  

4. **Console Tricks**:  
   - Clear the console, print centered text, or enumerate lists stylishly.  

5. **System Utilities**:  
   - Get system-related information like the current user, CPU count, console size, and system time.  
   - Calculate time differences between current time and a target time (useful for scheduling tasks).  

---

### Installation:  
You can install CoreEase directly from **PyPI** using pip:

```
pip install CoreEase
```  

Alternatively, to get the latest version from GitHub:

```
pip install git+https://github.com/Casbian/CoreEase.git
```  

After uploading to **PyPI**, users can easily install the package directly from there.

---

### Quickstart Guide:

1. **Master Multithreading**  
   Let CoreEase handle thread management for you:  

   ```python
   from CoreEase.threads import SubmitTasktoThreadWITHLoadBuffer

   def my_task():  
       print("Doing some important stuff...")

   SubmitTasktoThreadWITHLoadBuffer(my_task)
   ```  

   Effortless threading with built-in buffering.

2. **Browser Automation**  
   Automate web tasks with minimal effort:  

   ```python
   from CoreEase.web import StartBrowser, GoToUrl, ParseforLinks

   StartBrowser()  
   GoToUrl("https://example.com")  
   http_links, https_links = ParseforLinks()  
   print("HTTP Links:", http_links)  
   print("HTTPS Links:", https_links)
   ```  

3. **Handle Files**  
   Simplify file operations:  

   ```python
   from CoreEase.files import CheckFileExistence, CreateFile, AppendtoFile

   file_name = "example.txt"

   if not CheckFileExistence(file_name):  
       CreateFile(file_name)  

   AppendtoFile(file_name, "This is a line of text!")
   ```  

4. **Console Wizardry**  
   Keep your console clean and professional:  

   ```python
   from CoreEase.console import ClearConsole, CenteredPrint

   ClearConsole()  
   CenteredPrint("Welcome to CoreEase!", "*")
   ```  

5. **System Utilities**  
   Use CoreEase to get current system information or calculate time differences:  

   ```python
   from CoreEase.system import CurrentUser, CPUCount, ConsoleHeight, ConsoleWidth, CurrentSystemTime, CalculateTimeDifferencetoTargetTime24HourFrame

   print("Current User:", CurrentUser())  
   print("CPU Count:", CPUCount())  
   print("Console Height:", ConsoleHeight())  
   print("Console Width:", ConsoleWidth())  
   print("Current System Time:", CurrentSystemTime())  

   target_time = "14:30"  # 2:30 PM
   time_diff = CalculateTimeDifferencetoTargetTime24HourFrame(target_time)
   if time_diff:
       print(f"Time difference to {target_time}: {time_diff}")
   else:
       print("Target time has already passed.")
   ```  

---

### New Features:

- **Time Management**:  
   CoreEase provides an easy way to calculate the time difference between the current system time and a target time (in a 24-hour format). Ideal for scheduling tasks or automating time-sensitive workflows.

   ```python
   from CoreEase.system import CalculateTimeDifferencetoTargetTime24HourFrame

   target_time = "23:59"
   time_diff = CalculateTimeDifferencetoTargetTime24HourFrame(target_time)
   if time_diff:
       print(f"Time until target time: {time_diff}")
   else:
       print("The target time has already passed.")
   ```

- **System Information**:  
   Quickly get essential system information like the current user, CPU count, console size, and system time:

   ```python
   from CoreEase.system import CurrentUser, CPUCount, ConsoleHeight, ConsoleWidth, CurrentSystemTime

   print("Current User:", CurrentUser())
   print("CPU Count:", CPUCount())
   print("Console Height:", ConsoleHeight())
   print("Console Width:", ConsoleWidth())
   print("Current Time:", CurrentSystemTime())
   ```

---

### Contributing:  
Want to add a feature or fix a bug? Contributing is simple:

1. Fork the repository.  
2. Clone it:  
   `git clone https://github.com/Casbian/CoreEase.git`  
3. Make your changes.  
4. Submit a pull request.  

---

### License:  
CoreEase is licensed under the MIT License. Feel free to share, remix, and improve it!

---

This expansion covers the new utilities you added, focusing on system info retrieval, time management, and enhancements to threading. Let me know if you'd like to add anything else or further refine the README!Based on the new code you've provided, I'll expand your README to include these additional features, such as system-related utilities, time management, and more advanced threading options. Here's the updated README with those enhancements:

---

**CoreEase**  
**Why work harder when you can CoreEase?**

### What is CoreEase?  
CoreEase is a Python package designed to simplify your workflow by automating repetitive tasks, handling threads efficiently, and providing easy utilities for system operations. Whether it's managing files, automating browsers, or working with system resources, CoreEase helps you do more with less effort.

---

### Features:  

1. **Thread Management**:  
   - Execute tasks in parallel with simple threading.  
   - Includes an animated load buffer to keep things looking productive.  

2. **Browser Automation**:  
   - Headless browsing, form filling, and button clicking.  
   - Easy parsing of links, buttons, and login forms.  

3. **File Handling**:  
   - Check file existence, create files, append content, and overwrite efficiently.  

4. **Console Tricks**:  
   - Clear the console, print centered text, or enumerate lists stylishly.  

5. **System Utilities**:  
   - Get system-related information like the current user, CPU count, console size, and system time.  
   - Calculate time differences between current time and a target time (useful for scheduling tasks).  

---

### Installation:  
You can install CoreEase directly from **PyPI** using pip:

```
pip install CoreEase
```  

Alternatively, to get the latest version from GitHub:

```
pip install git+https://github.com/Casbian/CoreEase.git
```  

After uploading to **PyPI**, users can easily install the package directly from there.

---

### Quickstart Guide:

1. **Master Multithreading**  
   Let CoreEase handle thread management for you:  

   ```python
   from CoreEase.threads import SubmitTasktoThreadWITHLoadBuffer

   def my_task():  
       print("Doing some important stuff...")

   SubmitTasktoThreadWITHLoadBuffer(my_task)
   ```  

   Effortless threading with built-in buffering.

2. **Browser Automation**  
   Automate web tasks with minimal effort:  

   ```python
   from CoreEase.web import StartBrowser, GoToUrl, ParseforLinks

   StartBrowser()  
   GoToUrl("https://example.com")  
   http_links, https_links = ParseforLinks()  
   print("HTTP Links:", http_links)  
   print("HTTPS Links:", https_links)
   ```  

3. **Handle Files**  
   Simplify file operations:  

   ```python
   from CoreEase.files import CheckFileExistence, CreateFile, AppendtoFile

   file_name = "example.txt"

   if not CheckFileExistence(file_name):  
       CreateFile(file_name)  

   AppendtoFile(file_name, "This is a line of text!")
   ```  

4. **Console Wizardry**  
   Keep your console clean and professional:  

   ```python
   from CoreEase.console import ClearConsole, CenteredPrint

   ClearConsole()  
   CenteredPrint("Welcome to CoreEase!", "*")
   ```  

5. **System Utilities**  
   Use CoreEase to get current system information or calculate time differences:  

   ```python
   from CoreEase.system import CurrentUser, CPUCount, ConsoleHeight, ConsoleWidth, CurrentSystemTime, CalculateTimeDifferencetoTargetTime24HourFrame

   print("Current User:", CurrentUser())  
   print("CPU Count:", CPUCount())  
   print("Console Height:", ConsoleHeight())  
   print("Console Width:", ConsoleWidth())  
   print("Current System Time:", CurrentSystemTime())  

   target_time = "14:30"  # 2:30 PM
   time_diff = CalculateTimeDifferencetoTargetTime24HourFrame(target_time)
   if time_diff:
       print(f"Time difference to {target_time}: {time_diff}")
   else:
       print("Target time has already passed.")
   ```  

---

### New Features:

- **Time Management**:  
   CoreEase provides an easy way to calculate the time difference between the current system time and a target time (in a 24-hour format). Ideal for scheduling tasks or automating time-sensitive workflows.

   ```python
   from CoreEase.system import CalculateTimeDifferencetoTargetTime24HourFrame

   target_time = "23:59"
   time_diff = CalculateTimeDifferencetoTargetTime24HourFrame(target_time)
   if time_diff:
       print(f"Time until target time: {time_diff}")
   else:
       print("The target time has already passed.")
   ```

- **System Information**:  
   Quickly get essential system information like the current user, CPU count, console size, and system time:

   ```python
   from CoreEase.system import CurrentUser, CPUCount, ConsoleHeight, ConsoleWidth, CurrentSystemTime

   print("Current User:", CurrentUser())
   print("CPU Count:", CPUCount())
   print("Console Height:", ConsoleHeight())
   print("Console Width:", ConsoleWidth())
   print("Current Time:", CurrentSystemTime())
   ```

---

### Contributing:  
Want to add a feature or fix a bug? Contributing is simple:

1. Fork the repository.  
2. Clone it:  
   `git clone https://github.com/Casbian/CoreEase.git`  
3. Make your changes.  
4. Submit a pull request.  

---

### License:  
CoreEase is licensed under the MIT License. Feel free to share, remix, and improve it!

---
