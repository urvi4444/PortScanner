from flask import Flask, render_template, request, jsonify
import socket
import threading
import queue
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    target = data.get('target')
    start_port = int(data.get('start_port', 1))
    end_port = int(data.get('end_port', 1024))
    timeout = 1  # Timeout in seconds

    try:
        # Validate target
        try:
            socket.gethostbyname(target)
        except socket.gaierror:
            return jsonify({
                'status': 'error',
                'message': 'Invalid target IP or hostname'
            })

        results = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = 'unknown'
                    results.append({
                        'port': port,
                        'state': 'open',
                        'service': service
                    })
                sock.close()
            except Exception as e:
                pass

        # Create thread pool
        threads = []
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return jsonify({
            'status': 'success',
            'results': results,
            'target': target
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
