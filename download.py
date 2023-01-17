import numpy as np
from contextlib import closing
import requests

requests.packages.urllib3.disable_warnings()

def download(url, name):
    with closing(requests.get(url=url, verify=False, stream=True)) as res:
        with open('./junxun/{}.mp4'.format(name),'wb') as fd:   
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    fd.write(chunk)

if __name__ == '__main__':
    store_video = np.load('video_link.npy')
    store_video = store_video.tolist()
    print('Successfully get {},Start to download'.format(len(store_video)))
    index = 1
    for video in store_video:
        print('Currently downloading {}/{}'.format(len(store_video),index))
        download(video, index)
        index += 1
    print('Download Completed')