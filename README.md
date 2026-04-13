# RetroCore OS

*A Visual Operating System Simulator*

---

## 1. Overview

RetroCore OS is a graphical operating system simulator built using Python and Pygame. It demonstrates core OS concepts—such as CPU scheduling, memory management, and process lifecycle—through an interactive retro-style interface where games act as processes.

The system is designed as a **“glass-box OS”**, allowing users to observe how an operating system manages multiple applications in real time.

---

## 2. Features

### Core OS Functionality

* **Round Robin Scheduler**

  * Foreground process runs every frame
  * Background processes share CPU using time quantum
* **Memory Management**

  * Contiguous memory allocation
  * Dynamic allocation and deallocation
  * Real-time memory visualization
* **Process Lifecycle**

  * Create, run, and terminate processes
  * PID tracking and CPU time monitoring

### Hardware Abstraction

* Custom **Display Engine** (NumPy framebuffer + Pygame rendering)
* Input handling via keyboard abstraction
* OS_API layer for safe communication between apps and hardware

### Applications (Processes)

* Pong
* Snake
* Breakout
* System Monitor
* Memory Viewer

### Visualization

* Live kernel stats (CPU, PID, ticks)
* Memory usage bar
* Process table (state, CPU time, memory)
* Retro UI with consistent color system

---

## 3. System Architecture

```
User Apps (Games / Tools)
        ↓
     OS_API
        ↓
 ┌───────────────┐
 │   Scheduler   │
 │ Memory Manager│
 └───────────────┘
        ↓
   Hardware Layer
 (Display + Input)
```

---

## 4. How It Works

* Each app runs as a **process**
* Scheduler manages execution:

  * Foreground process → always runs
  * Background processes → time-shared
* Memory Manager assigns fixed-size blocks per process
* Display renders a low-resolution framebuffer scaled to window
* Dashboard overlays real-time system information

---

## 5. Controls

| Key   | Action        |
| ----- | ------------- |
| ↑ / ↓ | Navigate menu |
| ENTER | Launch app    |
| ESC   | Exit app      |
| ← / → | Game controls |
| Z / X | A / B buttons |

---

## 6. Installation

### Requirements

* Python 3.x
* Pygame
* NumPy

### Install dependencies

```bash
pip install pygame numpy
```

### Run

```bash
python main.py
```

---

## 7. Project Structure

```
kernel/
  scheduler.py
  memory_manager.py
  process.py
  syscall.py

hardware/
  display.py
  input_device.py
  font.py

apps/
  launcher.py
  pong.py
  snake.py
  breakout.py
  system_monitor.py
  memory_viewer.py
  system_dashboard.py
  ui.py

main.py
```

---

## 8. Strengths

* Clear demonstration of OS concepts
* Clean modular architecture
* Real-time visualization of kernel behavior
* Strong retro UI/UX design
* Functional multitasking simulation

---

## 9. Limitations

* Fixed logical resolution (160×144)
* No process priority or blocking states
* Memory allocation is simplified (no fragmentation)
* Background processes are not visually rendered

---

## 10. Future Improvements

* Dynamic resolution support
* Visual scheduler queue display
* Process states (WAITING / BLOCKED)
* Advanced memory allocation strategies
* Inter-process communication
* Enhanced UI animations and transitions

---

## 11. Conclusion

RetroCore OS successfully demonstrates how an operating system manages processes, memory, and execution flow in a simplified yet visually intuitive way. It bridges theoretical OS concepts with interactive simulation, making it a useful educational tool.

---
