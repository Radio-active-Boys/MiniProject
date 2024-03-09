import subprocess
import time

def run_wifiinfoview(output_file, format_type='csv'):
    # Define the command to run wifiinfoView.exe
    command = ['wifiinfoView.exe', '/scomma', output_file] if format_type == 'csv' else ['wifiinfoView.exe', '/sjson', output_file]

    # Run the command using subprocess
    subprocess.run(command, shell=True)

# Specify the number of iterations
num_iterations = 5

# Specify the format in which you want to save the data (e.g., 'csv', 'json')
output_format = 'csv'

# Run the wifiinfoView tool iteratively
for iteration in range(1, num_iterations + 1):
    # Specify the output file name for each iteration
    output_file = f'output_iteration_{iteration}.{output_format}'

    # Run wifiinfoView.exe and save the data
    run_wifiinfoview(output_file, format_type=output_format)

    print(f'Iteration {iteration} completed. Data saved to {output_file}')

    # Introduce a delay between iterations if needed
    time.sleep(5)  # Adjust the delay time as needed
