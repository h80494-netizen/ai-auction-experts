import os

file_path = 'backend/app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoints = """
@app.get("/api/images/{case_number:path}")
async def get_images(case_number: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    dir_path = os.path.join(downloads_dir, safe_case)
    if not os.path.exists(dir_path):
        dir_path = os.path.join(downloads_dir, case_number)
        
    images = []
    if os.path.exists(dir_path):
        for f in os.listdir(dir_path):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(f)
    
    # Sort them so photo_01 comes before photo_02
    images.sort()
    
    # If no images, return empty list or maybe the default ones
    if not images:
        return {"status": "success", "images": []}
        
    return {"status": "success", "images": images}

@app.get("/api/download_image/{case_number:path}/{filename}")
async def download_image(case_number: str, filename: str):
    safe_case = case_number.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(downloads_dir, safe_case, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(downloads_dir, case_number, filename)
    if not os.path.exists(file_path):
        test_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images")
        file_path = os.path.join(test_images_dir, "thumb_0.png")
    return FileResponse(path=file_path)

"""

# Let's insert it before `def download_photo`
start_idx = content.find('@app.get("/api/download_photo')

new_content = content[:start_idx] + new_endpoints + "\n" + content[start_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("backend/app.py updated successfully")
