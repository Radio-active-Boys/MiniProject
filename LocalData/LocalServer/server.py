from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# HTML template for the webpage
html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Set Raspberry Pi Time</title>
  </head>
  <body>
    <div class="container">
      <h1 class="mt-5">Set Raspberry Pi Time</h1>
      <p id="time-info"></p>
    </div>

    <script>
      document.addEventListener('DOMContentLoaded', (event) => {
        // Get client's time
        var clientTime = new Date();
        var clientTimeString = clientTime.toISOString();

        // Display client's time
        document.getElementById('time-info').innerHTML = 'Your device time is: ' + clientTimeString;

        // Send client's time to the server
        fetch('/set_time', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ time: clientTimeString })
        }).then(response => response.json()).then(data => {
          console.log('Server response:', data);
        }).catch((error) => {
          console.error('Error:', error);
        });
      });
    </script>
  </body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/set_time', methods=['POST'])
def set_time():
    data = request.json
    client_time = data['time']
    print(f"Received client time: {client_time}")

    try:
        # Set the system time using the received client time
        subprocess.run(['sudo', 'date', '-s', client_time], check=True)
        return {'status': 'success', 'message': 'Time updated successfully'}, 200
    except subprocess.CalledProcessError as e:
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
