from PIL import Image, ImageGrab
from threading import Thread
import imagehash
import time

@app.route('/screen_capture')
def screen_cap():
    return render_template('screen_capture.html')

@app.route('/start_capture')
@login_required
def start_capture():
    global capture_thread, stop_capture
    if capture_thread is None or not capture_thread.is_alive():
        stop_capture = False
        user_info = {
            'username': current_user.username,
            'user_rank': current_user.rta_rank
        }
        capture_thread = Thread(target=run_capture, kwargs={'user_info': user_info})
        capture_thread.start()
    return redirect(url_for('screen_capture'))

@app.route('/stop_capture')
@login_required
def stop_capture():
    global stop_capture
    stop_capture = True
    return redirect(url_for('screen_capture'))

@app.route('/screen_capture')
@login_required
def screen_capture():
    return render_template('screen_capture.html')

@login_required
def run_capture(user_info):
    regions = {
        'unit': {'x': 170, 'y': 206, 'width': 700, 'height': 70},
        'cp': {'x': 230, 'y': 608, 'width': 170, 'height': 50},
        'imprint': {'x': 296, 'y': 393, 'width': 210, 'height': 135},
        'attack': {'x': 413, 'y': 670, 'width': 100, 'height': 30},
        'defense': {'x': 413, 'y': 703, 'width': 100, 'height': 30}, 
        'health': {'x': 413, 'y': 735, 'width': 100, 'height': 30},
        'speed': {'x': 413, 'y': 773, 'width': 100, 'height': 30}, 
        'critical_hit_chance': {'x': 413, 'y': 810, 'width': 100, 'height': 29}, 
        'critical_hit_damage': {'x': 413, 'y': 842, 'width': 100, 'height': 34},
        'effectiveness':  {'x': 413, 'y': 880, 'width': 100, 'height': 34}, 
        'effect_resistance': {'x': 413, 'y': 914, 'width': 100, 'height': 34},
        'set1': {'x': 230, 'y': 1005, 'width': 250, 'height': 34},
        'set2':  {'x': 230, 'y': 1040, 'width': 250, 'height': 34}, 
        'set3': {'x': 230, 'y': 1075, 'width': 250, 'height': 34}
    }
    global stop_capture
    previous_hash = None
    hash_threshold = 2 

    while not stop_capture:
        screen_image = ImageGrab.grab()
        current_hash = imagehash.average_hash(screen_image)

        if previous_hash is None or (current_hash - previous_hash) > hash_threshold:
            stats = {name: pytesseract.image_to_string(screen_image.crop((data['x'], data['y'], data['x'] + data['width'], data['y'] + data['height'])), config='--psm 6') for name, data in regions.items()}
            if stats:
                save_stats(stats, user_info)
                previous_hash = current_hash
        time.sleep(1)
 
    return render_template('display.html', stats=stats)

def save_stats(stats, user_info):
    stats.update({
        'uploaded_by': user_info['username'],
        'user_rank': user_info['user_rank']
    })
    new_stats = ImageStats(**stats)
    db.session.add(new_stats)
    db.session.commit()