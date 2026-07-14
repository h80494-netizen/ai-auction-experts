import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    path = 'backend/ai_analyzer.py'
    with open(path, 'rb') as f:
        raw_data = f.read()
        
    try:
        content = raw_data.decode('utf-8')
        print("Successfully decoded as UTF-8!")
        print("Content length:", len(content))
        # print first 50 lines
        lines = content.split('\n')
        for i in range(min(50, len(lines))):
            print(f"{i+1}: {lines[i]}")
    except Exception as e:
        print("UTF-8 decoding failed:", e)

if __name__ == '__main__':
    main()
