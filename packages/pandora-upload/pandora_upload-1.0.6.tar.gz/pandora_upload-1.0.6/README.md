# pandora-upload

pandora_upload is a commandline client for pan.do/ra.
You can use it to upload one or more files to your pandora instance.
No conversion is done on the client side.
To upload/sync large repositories use pandora_client

Upload a file from the command line:

``` sh
pandora-upload -p http://pandora/api/ -m "title=This is an example" -m "director=[Jane Doe]" -m "date=2021-11-15" /home/example/Videos/video.mp4
```

or you can use pandora-upload in a python script:

``` python
import pandora_upload
item_id = pandora_upload.upload(
    'http://pandora/api/',
    ['/home/example/Videos/video.mp4'],
    {
        'title': 'This is an example',
        'date': '2021-11-15'
    }
)
```
