import os
try:
	import requests
except:
	os.system("pip install requests")
try:
	from user_agent import generate_user_agent
except:
	os.system("pip install user-agent")

def Audio_Url(Link:str):
	if Link.startswith('https://www.youtube.com/watch?v='):
		url = "https://api.fabdl.com/youtube/get-cw"
		params = {'url': Link}
		headers={
      'User-Agent': generate_user_agent(),
      'Accept': "application/json, text/plain, */*",
    #  'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua-platform': "\"Windows\"",
      'sec-ch-ua': "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Brave\";v=\"132\"",
      'sec-ch-ua-mobile': "?0",
      'sec-gpc': "1",
      'accept-language': "en-US,en;q=0.8",
      'origin': "null",
      'sec-fetch-site': "cross-site",
      'sec-fetch-mode': "cors",
      'sec-fetch-dest': "empty",
      'referer': "https://en.listentoyoutube.ch/",
      'priority': "u=1, i"
    }
		response = requests.get(url, params=params, headers=headers)
		aud = response.json()['result']['audios'][0]['url']
		#rint(aud)
		return {'link_audio':aud}
	else:
		return 'Faild , try again later ..'


def Video_Url(Link:str):
	if Link.startswith('https://www.youtube.com/watch?v='):
		url = "https://api.fabdl.com/youtube/get-cw"
		params = {'url': Link}
		headers={
      'User-Agent': generate_user_agent(),
      'Accept': "application/json, text/plain, */*",
    #  'Accept-Encoding': "gzip, deflate, br, zstd",
      'sec-ch-ua-platform': "\"Windows\"",
      'sec-ch-ua': "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Brave\";v=\"132\"",
      'sec-ch-ua-mobile': "?0",
      'sec-gpc': "1",
      'accept-language': "en-US,en;q=0.8",
      'origin': "null",
      'sec-fetch-site': "cross-site",
      'sec-fetch-mode': "cors",
      'sec-fetch-dest': "empty",
      'referer': "https://en.listentoyoutube.ch/",
      'priority': "u=1, i"
    }
		response = requests.get(url, params=params, headers=headers)
		vid =response.json()['result']['videos'][0]['url']
		return {'link_video':vid}
	else:
		return 'Faild , try again later ..'
	


 