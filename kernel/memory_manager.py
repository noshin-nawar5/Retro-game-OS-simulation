class MemoryManager:
    """
    Extended memory manager.
    change_age[i]  : counts down from FADE_TICKS when block i changes (alloc or free)
    fragmentation(): 0.0=none  1.0=fully fragmented
    tick()         : called each frame to age down highlights
    """

    FADE_TICKS = 20

    def __init__(self, total_size):
        self.total_size  = total_size
        self.memory      = [0] * total_size
        self.allocations = {}
        self.change_age  = [0] * total_size

    def allocate(self, pid, size):
        if size <= 0:
            return None
        for start in range(self.total_size - size + 1):
            if all(self.memory[i] == 0 for i in range(start, start + size)):
                for i in range(start, start + size):
                    self.memory[i]     = pid
                    self.change_age[i] = self.FADE_TICKS
                self.allocations[pid] = (start, size)
                print(f"[Memory] PID {pid} -> {size} blocks @ {start}")
                return start
        print(f"[Memory] OOM for PID {pid}")
        return None

    def free(self, pid):
        if pid not in self.allocations:
            return
        start, size = self.allocations.pop(pid)
        for i in range(start, start + size):
            self.memory[i]     = 0
            self.change_age[i] = self.FADE_TICKS
        print(f"[Memory] PID {pid} freed {size} blocks")

    def tick(self):
        for i in range(self.total_size):
            if self.change_age[i] > 0:
                self.change_age[i] -= 1

    def get_memory_snapshot(self):
        return self.memory

    def get_used(self):
        return sum(1 for c in self.memory if c != 0)

    def get_free(self):
        return self.total_size - self.get_used()

    def fragmentation(self):
        """
        External fragmentation: 1 - (largest_free_run / total_free).
        0.0 = no fragmentation, 1.0 = fully fragmented.
        """
        free_total = self.get_free()
        if free_total == 0:
            return 0.0
        largest = cur = 0
        for cell in self.memory:
            if cell == 0:
                cur += 1
                largest = max(largest, cur)
            else:
                cur = 0
        return 1.0 - (largest / free_total)