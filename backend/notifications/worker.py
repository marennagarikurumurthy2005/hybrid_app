import time
from notifications import services


if __name__ == "__main__":
    while True:
        services.dispatch_scheduled()
        services.process_queue()
        time.sleep(1)
