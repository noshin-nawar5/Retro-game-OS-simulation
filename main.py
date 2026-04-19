import pygame

from kernel.memory_manager import MemoryManager
from kernel.scheduler      import RoundRobinScheduler
from kernel.process        import Process
from kernel.syscall        import OS_API

from hardware.display      import Display
from hardware.input_device import InputDevice

from apps.launcher         import Launcher
from apps.system_dashboard import SystemDashboard


# ---------- HARDWARE ----------
display      = Display()
input_device = InputDevice()

# ---------- KERNEL ----------
memory    = MemoryManager(256)
scheduler = RoundRobinScheduler(time_quantum=5, memory_manager=memory)

# ---------- OS API ----------
os_api = OS_API(display, scheduler, input_device)

# ---------- LAUNCHER — PID 1, foreground at boot ----------
launcher         = Launcher(os_api)
launcher_process = Process(pid=scheduler.generate_pid(),
                           app=launcher, memory_needed=10)
scheduler.add_process(launcher_process)
scheduler.foreground_process = launcher_process

# ---------- DASHBOARD — memory allocated but NOT in scheduler ----------
dashboard = SystemDashboard(os_api)
dash_pid  = scheduler.generate_pid()
memory.allocate(dash_pid, 5)   # visible in memory map

# ---------- MAIN LOOP ----------
running = True
clock   = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                scheduler.foreground_process = launcher_process

    input_device.update()

    display.clear()
    scheduler.schedule()
    dashboard.draw_overlay()
    display.render()

    clock.tick(60)

pygame.quit()