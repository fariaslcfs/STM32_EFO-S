import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from collections import deque
from datetime import datetime

# Initialize serial port
def init_serial(port, baudrate):
    ser = serial.Serial(port, baudrate)
    return ser

# Function to receive and process data
def receive_data(ser):
    line = ser.readline().strip().decode()
    # Filter out non-numeric characters
    line_filtered = ''.join(filter(lambda x: x.isdigit() or x in '.-', line))
    return line_filtered

# Global variables for frequency calculation
last_time = None
frequency = 0.0

# Function to update the plot
def update(frame):
    global data_points, last_time, frequency
    # Receive data
    line_data = receive_data(ser)
    if line_data:
        value = float(line_data)
        data_points.append(value)
        
        # Calculate frequency
        current_time = datetime.now()
        if last_time is not None:
            time_diff = (current_time - last_time).total_seconds()  # Time difference in seconds
            if time_diff > 0:  # Prevent division by zero
                frequency = 1 / time_diff  # Frequency in Hz
        last_time = current_time
        
        # Update the plot with the new data points
        line.set_data(range(len(data_points)), data_points)
        ax.relim()
        ax.autoscale_view()
        
        # Update frequency text
        freq_text.set_text(f'Data Points Frequency: {frequency:.2f} Hz')
    
    return line,

# Function to update max_data_points
def update_max_data_points(val):
    global max_data_points, data_points
    max_data_points = int(val)
    data_points = deque(data_points, maxlen=max_data_points)

# Initialize serial port
port = input("Enter the communication port (default: COM16): ")
port = port if port else "COM16"  # Set default value if empty
baudrate = input("Enter the baudrate (default: 9600): ")
baudrate = int(baudrate) if baudrate else 9600  # Set default value if empty
ser = init_serial(port, baudrate)

# Initialize plot
fig, ax = plt.subplots()
ax.set_xlabel('Index')
ax.set_ylabel('Volts')
ax.set_title('Real-Time Data Plot')

# Set the y-axis limit to 4.0
ax.set_ylim(0, 4.0)

# Initialize empty data points deque with a maximum length
max_data_points = 100  # Adjust this value as needed
data_points = deque(maxlen=max_data_points)
line, = ax.plot([], [])

# Place to show the frequency on the plot
freq_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

# Create animation with a smaller interval for closer to real-time plotting
ani = FuncAnimation(fig, update, frames=None, interval=10)

# Create a slider to change max_data_points
slider_ax = plt.axes([0.93, 0.3, 0.03, 0.35], facecolor='red')  # Define slider position and size
slider = Slider(slider_ax, 'H', 2, 200, valinit=max_data_points, color='lightgreen', orientation='vertical')
slider.on_changed(update_max_data_points)  # Set slider update action

plt.show()

# Close serial port after plotting is finished
ser.close()
