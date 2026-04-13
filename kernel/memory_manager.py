class MemoryManager:
    def __init__(self, total_size):
        self.total_size  = total_size
        self.memory      = [0] * total_size
        self.allocations = {}

    def allocate(self, pid, size):
        if size <= 0:
            return None
        for start in range(self.total_size - size + 1):
            if all(self.memory[i] == 0 for i in range(start, start + size)):
                for i in range(start, start + size):
                    self.memory[i] = pid
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
            self.memory[i] = 0
        print(f"[Memory] PID {pid} freed {size} blocks")

    def get_memory_snapshot(self):
        return self.memory

    def get_used(self):
        return sum(1 for c in self.memory if c != 0)

    def get_free(self):
        return self.total_size - self.get_used()