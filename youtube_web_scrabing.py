from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import googleapiclient.discovery

import pandas as pd

app = Flask(__name__,template_folder='templates')

@app.route('/',methods=['POST','GET'])

def search():
    
    if request.method == 'POST':
        query=str(request.form['que'])
        num_results = int(request.form['num_results'])
        detail_list = fetch_results(num_results,query)
        return render_template('table.html', detail_list=detail_list)
    
    else:
        
        return render_template('search.html')

def fetch_results(num_results,query):
    
    detail_list=[]
    API_KEY = "AIzaSyAtmzAxs12I13ieOVLYIg0yFWKf_DQNISk"
    url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet&q={query}&maxResults={num_results}&type=video"
    
    try:
        response = requests.get(url)
        data = response.json()
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    
    for item in data["items"]:
        
        video_id = item["id"]["videoId"]
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnail=item["snippet"]["thumbnails"]["default"]["url"]
        title=item["snippet"]["title"]
        time=item["snippet"]['publishedAt']
        video_stat=video_detail(video_id, API_KEY)
        
        detail_list.append({"video_link":video_link,
                            "thumbnail":thumbnail,
                            "title":title,
                            "time":time,
                            "View_count":video_stat[0],
                            "Like_count":video_stat[1],
                            "Comment_count":video_stat[2]})
        
    df = pd.DataFrame.from_dict(detail_list) 
    df.to_csv (r'scrabed_data.csv', index=False, header=True) 
    return detail_list

def video_detail(video_id,API_KEY):
    api_service_name = "youtube"
    api_version = "v3"
    try:
        youtube = googleapiclient.discovery.build(serviceName=api_service_name, version=api_version, developerKey = API_KEY)
        request = youtube.videos().list(part = 'statistics', id = video_id)
        response = request.execute()
    except googleapiclient.errors.HttpError as err:
        print(f'An HTTP error occurred: {err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    
    statistics = response['items'][0]['statistics']
    return [statistics['viewCount'],statistics['likeCount'],statistics['commentCount'],statistics['favoriteCount']]

if __name__ == '__main__':
    app.run(debug=True)
