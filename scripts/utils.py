import time
import psutil
import torch
import os

class SystemMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = None
        self.start_cpu = None
        self.start_ram = None
        
    def start(self):
        self.process.cpu_percent() # Calibra o psutil para uso de CPU deste processo
        time.sleep(0.1) 
        
        self.start_time = time.time()
        self.start_ram = self.process.memory_info().rss
        
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            
    def stop(self):
        end_time = time.time()
        
        # Uso de CPU no período
        cpu_usage = self.process.cpu_percent() 
        
        # Uso de RAM extra durante a execução (em bytes -> MB)
        ram_end = self.process.memory_info().rss
        ram_usage_diff = ram_end - self.start_ram
        
        vram_peak = 0
        if torch.cuda.is_available():
            vram_peak = torch.cuda.max_memory_allocated()
            
        return {
            "time_seconds": round(end_time - self.start_time, 2),
            "cpu_percent": round(cpu_usage, 2),
            "ram_used_mb": round(ram_usage_diff / (1024 * 1024), 2),
            "vram_peak_mb": round(vram_peak / (1024 * 1024), 2)
        }
