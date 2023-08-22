from flask import Flask, request, jsonify
import requests
import concurrent.futures
import json
import time

app = Flask(__name__)

def fetch_numbers(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("numbers", [])
    except:
        pass
    return []

def merge_and_sort_numbers(numbers_lists):
    merged = set()
    for numbers in numbers_lists:
        merged.update(numbers)
    return sorted(merged)

@app.route('/numbers', methods=['GET'])
def get_numbers():
    urls = request.args.getlist('url')
    
    start_time = time.time()
    
    numbers_lists = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_numbers, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            numbers = future.result()
            if numbers:
                numbers_lists.append(numbers)
    
    merged_numbers = merge_and_sort_numbers(numbers_lists)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if elapsed_time > 0.5:
        return jsonify({"error": "Timeout exceeded"}), 500
    
    return jsonify({"numbers": merged_numbers})

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=8008)