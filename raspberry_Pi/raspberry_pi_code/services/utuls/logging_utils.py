def log_to_console_and_file(message, log_file="/home/pi/BUZZWatch/errors/errors.log"):
    """
    Logs a message to both the console and a file.
    """
    print(message)
    with open(log_file, "a") as f:
        f.write(f"{message}\n")
