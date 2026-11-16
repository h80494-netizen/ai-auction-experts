from flask import Flask, render_template, send_file, jsonify
import os
import sys
import subprocess
import glob
import threading
import uuid
import time
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# 전역 프로세스 딕셔너리
active_processes = {}
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

def get_latest_file(pattern):
    search_path = os.path.join(BASE_DIR, pattern)
    files = sorted([f for f in glob.glob(search_path) if '요약' not in f], key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def run_task_thread(task_id, cmd_list, file_pattern):
    try:
        process = subprocess.Popen(cmd_list, cwd=BASE_DIR)
        active_processes[task_id] = process
        return_code = process.wait()
        
        if active_processes.get(task_id) is None:
            tasks[task_id] = {"status": "error", "message": "크롤링이 취소되었습니다."}
            return
            
        active_processes.pop(task_id, None)
        
        if return_code != 0:
            tasks[task_id] = {"status": "error", "message": f"크롤링 프로세스가 비정상 종료되었습니다 (코드: {return_code})."}
            return
        
        # 파일이 완전히 생성되도록 잠시 대기
        time.sleep(1)
        output_filepath = get_latest_file(file_pattern)
        
        if not output_filepath or not os.path.exists(output_filepath):
            tasks[task_id] = {"status": "error", "message": "파일 생성에 실패했습니다."}
            return
            
        tasks[task_id] = {"status": "completed", "filepath": output_filepath}
    except Exception as e:
        tasks[task_id] = {"status": "error", "message": str(e)}

@app.route('/api/crawl', methods=['POST'])
def crawl_api():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running"}
    thread = threading.Thread(target=run_task_thread, args=(task_id, [sys.executable, 'onbid_crawler.py'], '온비드_관심물건_*.xlsx'))
    thread.start()
    return jsonify({"status": "running", "task_id": task_id})

@app.route('/api/crawl_dooin', methods=['POST'])
def crawl_dooin_api():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running"}
    thread = threading.Thread(target=run_task_thread, args=(task_id, [sys.executable, 'run_dooin_merged.py'], '수도권_두인경매통합_*.xlsx'))
    thread.start()
    return jsonify({"status": "running", "task_id": task_id})

@app.route('/api/crawl_dooin_regional', methods=['POST'])
def crawl_dooin_regional_api():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running"}
    thread = threading.Thread(target=run_task_thread, args=(task_id, [sys.executable, 'run_dooin_regional_merged.py'], '지방권_두인경매통합_*.xlsx'))
    thread.start()
    return jsonify({"status": "running", "task_id": task_id})

@app.route('/api/weekly_pipeline', methods=['POST'])
def weekly_pipeline_api():
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running"}
    final_excel_pattern = os.path.join(os.path.dirname(BASE_DIR), '바이브코딩', 'data', '경공매업데이트', '경공매데이터_업데이트_대항력추가.xlsx')
    thread = threading.Thread(target=run_task_thread, args=(task_id, [sys.executable, 'weekly_auto_pipeline.py'], final_excel_pattern))
    thread.start()
    return jsonify({"status": "running", "task_id": task_id})

@app.route('/api/crawl_region/<region>', methods=['POST'])
def crawl_region_api(region):
    scripts = {
        'seoul': ('seoul_dooin.py', '서울_두인경매데이터_*.xlsx'),
        'incheon': ('incheon_dooin.py', '인천_두인경매데이터_*.xlsx'),
        'kyunggi': ('kyunggi_dooin.py', '경기도_두인경매데이터_*.xlsx'),
        'kangwon': ('kangwon_dooin.py', '강원도_두인경매데이터_*.xlsx'),
        'chungnam': ('chungnam_dooin.py', '충청남도_두인경매데이터_*.xlsx'),
        'jeonnam': ('jeonnam_dooin.py', '전라남도_두인경매데이터_*.xlsx')
    }
    
    if region not in scripts:
        return jsonify({"status": "error", "message": "잘못된 지역입니다."}), 400
        
    script_name, file_pattern = scripts[region]
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running"}
    thread = threading.Thread(target=run_task_thread, args=(task_id, [sys.executable, script_name], file_pattern))
    thread.start()
    return jsonify({"status": "running", "task_id": task_id})

@app.route('/api/status/<task_id>', methods=['GET'])
def status_api(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"status": "error", "message": "알 수 없는 작업입니다."}), 404
    return jsonify(task)

@app.route('/api/download/<task_id>', methods=['GET'])
def download_api(task_id):
    task = tasks.get(task_id)
    if not task or task.get("status") != "completed":
        return jsonify({"status": "error", "message": "파일이 준비되지 않았습니다."}), 400
    
    filepath = task["filepath"]
    filename = os.path.basename(filepath)
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/api/cancel', methods=['POST'])
def cancel_crawl():
    global active_processes
    count = 0
    for key, p in list(active_processes.items()):
        try:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            count += 1
        except Exception as e:
            print(f"종료 실패 {key}: {e}")
    
    active_processes.clear()
    
    # 실행 중인 태스크를 에러 상태로 변경
    for task_id in tasks:
        if tasks[task_id]["status"] == "running":
            tasks[task_id] = {"status": "error", "message": "크롤링이 취소되었습니다."}
            
    return jsonify({"status": "success", "message": f"{count}개의 크롤링 작업이 취소되었습니다."})

def open_browser():
    time.sleep(1.2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("=" * 60)
    print("  온비드 / 두인경매 자동 수집 시스템 서버가 시작되었습니다.")
    print("  브라우저 주소: http://127.0.0.1:5000")
    print("  ※ 이 콘솔 창을 닫으면 서버가 종료되므로 닫지 마세요.")
    print("=" * 60)
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
