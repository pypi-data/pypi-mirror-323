import serial
import time

def initialize_power_supply(port, baudrate=9600, timeout=1):
    """
    Initializes the connection to the SSP-8160 power supply.

    Parameters:
    port (str): The COM port (e.g., 'COM3') to which the power supply is connected.
    baudrate (int): Communication speed (default is 9600).
    timeout (int): Timeout for serial communication in seconds.

    Returns:
    Serial: The initialized serial connection.
    """
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    time.sleep(2)  # Allow the connection to establish
    print("Connection to SSP-8160 established.")
    return ser

def send_command(ser, command):
    """
    Sends a command to the power supply and returns the response.

    Parameters:
    ser (Serial): The serial connection.
    command (str): The command to send to the power supply.

    Returns:
    str: The response from the power supply.
    """
    print(f"Sending command: {command}")
    ser.write((command + '\r\n').encode('utf-8'))
    time.sleep(0.1)  # Allow time for response
    response = ser.readline().decode('utf-8').strip()
    print(f"Response: {response}")
    return response

def set_voltage(ser, voltage):
    """
    Sets the output voltage of the power supply.

    Parameters:
    ser (Serial): The serial connection.
    voltage (float): The desired voltage in volts.

    Returns:
    str: The response from the power supply.
    """
    if 0 <= voltage <= 84:
        command = f'VOLT 3 {int(voltage * 100):04}'  # Convert voltage to correct format
        return send_command(ser, command)
    else:
        raise ValueError("Voltage must be between 0 and 42 volts.")

def set_current(ser, current):
    """
    Sets the output current of the power supply.

    Parameters:
    ser (Serial): The serial connection.
    current (float): The desired current in amperes.

    Returns:
    str: The response from the power supply.
    """
    if 0 <= current <= 10:
        command = f'CURR 3 {int(current * 100):04}'  # Convert current to correct format
        return send_command(ser, command)
    else:
        raise ValueError("Current must be between 0 and 10 amperes.")

def turn_output_on(ser):
    """
    Turns the output of the power supply on.

    Parameters:
    ser (Serial): The serial connection.

    Returns:
    str: The response from the power supply.
    """
    return send_command(ser, 'SOUT1')

def turn_output_off(ser):
    """
    Turns the output of the power supply off.

    Parameters:
    ser (Serial): The serial connection.

    Returns:
    str: The response from the power supply.
    """
    return send_command(ser, 'SOUT0')

def query_status(ser):
    """
    Queries the current status of the power supply.

    Parameters:
    ser (Serial): The serial connection.

    Returns:
    str: The status information from the power supply.
    """
    return send_command(ser, 'GOUT')

def query_voltage_current(ser):
    """
    Queries the current output voltage and current of the power supply.

    Parameters:
    ser (Serial): The serial connection.

    Returns:
    tuple: The current output voltage and current.
    """
    response = send_command(ser, 'GETD')
    if response:
        voltage = int(response[0:4]) / 100  # Extract and convert voltage
        current = int(response[4:8]) / 100  # Extract and convert current
        return voltage, current
    else:
        raise ValueError("Failed to retrieve voltage and current.")

def close_connection(ser):
    """
    Closes the connection to the power supply.

    Parameters:
    ser (Serial): The serial connection.
    """
    ser.close()
    print("Connection to SSP-8160 closed.")