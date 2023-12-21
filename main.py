import requests, json, ffmpeg, music_tag, os
from yt_dlp import YoutubeDL

client_token = "" #--add your genuis token

DataTitle = ''
DataArtist = ''
DataAlbumArt = ''
DataAlbum = ''

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

while True:
    InputTitle = input('enter the song title:\n')
    InputArtist = input('enter the song artist:\n')

    #--Song Data stuffs
    search = InputTitle + ' ' +InputArtist
    formattedSearch =  search.replace(' ', '%20')
    r = requests.get(f'https://api.genius.com/search?q={formattedSearch}', headers={"Authorization":"Bearer "+client_token})
    if r.status_code == 200:
        print('Found song!')
        Data = json.loads(r.text)

        DataTitle = Data['response']['hits'][0]['result']['title']
        DataArtist = Data['response']['hits'][0]['result']['primary_artist']['name']

        AlbumArt = requests.get(Data['response']['hits'][0]['result']['header_image_thumbnail_url'])
        if AlbumArt.status_code == 200:
            DataAlbumArt = AlbumArt.content
            file = open("Temp/album_art.jpg", 'wb')
            file.write(DataAlbumArt)
            file.close()
        AlbumGet = requests.get('https://api.genius.com'+Data['response']['hits'][0]['result']['api_path'], headers={"Authorization":"Bearer "+client_token})
        if AlbumGet.status_code == 200:
            song_data = json.loads(AlbumGet.text)
            albumValue = song_data['response']['song']['album']

            if albumValue is None:
                DataAlbum = DataTitle
            else:
                DataAlbum = albumValue['name']
    #-- end of Song Data stuffs
            
    #-- Download Music
    yt_opts = {'verbose': False,
            'quiet':True,
            'format':'bestaudio',
            'outtmpl':f'Temp/temp_song.mp4'}
    yt = YoutubeDL(yt_opts)
    yt.download("ytsearch:"+InputTitle+' '+InputArtist)
    print('Downloading finished')
    #-- end of downloading music

    #-- convert to mp3
    print('converting files to mp3!')
    stream = ffmpeg.input(f'Temp/temp_song.mp4')
    stream = ffmpeg.output(stream, f'Music/{DataTitle}.mp3', loglevel="quiet")
    ffmpeg.run(stream)


    os.remove(f'Temp/temp_song.mp4')
    #-- end of covertign

    #-- adding tags/data
    fileTmp = open("Temp/album_art.jpg", 'rb')
    fileData = fileTmp.read()
    fileTmp.close()

    f = music_tag.load_file(f'Music/{DataTitle}.mp3')
    f['artwork'] = fileData
    f['album artist'] = DataArtist
    f['title'] = DataTitle
    f['tracktitle'] = DataTitle
    f['album'] = DataAlbum
    f.save()
    #-- end of adding tags/data
    clear()

    print('-------------')
    print('Finished \n')
    print(f'{DataTitle} by {DataArtist}')
    print(f'album: {DataAlbum}')