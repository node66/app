import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from starlette import status

app = FastAPI()

app_path = os.getcwd()
orig_path = Path(app_path + '/data/orig/')
copy_path = Path(app_path + '/data/copy')


def update(file):
    file_name = file.name
    file_dir = file.parents[1]
    copy_file_dir = file_dir.joinpath('copy/')

    if not os.path.exists(copy_file_dir):
        os.mkdir(copy_file_dir)

    with open(file, 'r') as orig_file:
        data = json.load(orig_file)
        new_data = {'update_timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        new_data.update(data)

    copy_file = str(copy_file_dir) + '/' + file_name
    with open(copy_file, 'w') as copy_file:
        json.dump(new_data, copy_file, indent=2)


@app.on_event("startup")
def startup_event():
    for file in orig_path.glob('*.json'):
        update(file)


@app.get("/api/feed")
async def get_feed(feed_id):
    filename = str(copy_path) + '/' + feed_id + '.json'
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/api/update", status_code=status.HTTP_200_OK)
async def get_update(feed_id):
    filename = str(copy_path) + '/' + feed_id + '.json'
    try:
        with open(filename, 'r') as f:
            update(Path(filename))
    except FileNotFoundError:
        raise HTTPException(status_code=403)
