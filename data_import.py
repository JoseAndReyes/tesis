from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import os
import pickle
import re
import io
import numpy as np
from PIL import Image

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def create_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def get_data(service, folder_name):
    # Replace 'your_folder_id' with the ID of the folder you want to access.
    folder_id = '1e_a28QWF9AYAT3UrdCNoaLy2Ci6_Knjg'
    query = f"'{folder_id}' in parents and name='{folder_name}'"

    results = service.files().list(q=query, 
                                   pageSize=100, 
                                   fields="nextPageToken, files(id, name)").execute()
    item = results.get('files', [])[0]
    
    if not item:
        print('No folders found.')
    else:
        images_list = []
        
    query_rgb = f"'{item['id']}' in parents and name='rgb' and mimeType='application/vnd.google-apps.folder'"
    results_rgb = service.files().list(q=query_rgb, 
                                       pageSize=10, 
                                       fields="nextPageToken, files(id, name)").execute()
    item_rgb = results_rgb.get('files', [])[0]

    
    query_files = f"'{item_rgb['id']}' in parents"
    results_files = service.files().list(q=query_files, 
                                         pageSize=1000, 
                                         fields="nextPageToken, files(id, name)").execute()
    items_files = results_files.get('files', [])
    
    for item_file in items_files:
        request = service.files().get_media(fileId=item_file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.seek(0)

        img = Image.open(fh)
        img_arr = np.array(img)
        images_list.append((img_arr, item_file['name']))

    return images_list