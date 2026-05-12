def compute_heavy_task(n):
    """Simulate heavy computation - calculate fibonacci with delay"""
    def fibonacci(num):
        if num <= 1:
            return num
        return fibonacci(num - 1) + fibonacci(num - 2)
    
    return fibonacci(min(n, 35))  # Cap at 35 to avoid infinite time