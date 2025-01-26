import os
try:
	import requests
except:
	os.system("pip install requests")
try:
	from youtube_search import YoutubeSearch
except:
	os.system("pip install youtube-search")
try:
	from user_agent import generate_user_agent
except:
	os.system("pip install user-agent")

def Audio_Url(Link:str):
	if Link.startswith('https://youtu.be/') or Link.startswith('https://www.youtube.com/watch?v='):
		j = YoutubeSearch(Link).videos
	#print)
		url = "https://v.ymcdn.org/api/v3/init"
		payload = {'id': j[0]['id']}
		headers = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua-platform': "\"Windows\"",
  'sec-ch-ua': "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Brave\";v=\"132\"",
  'sec-ch-ua-mobile': "?0",
  'sec-gpc': "1",
  'accept-language': "en-US,en;q=0.5",
  'origin': "https://en.greenconvert.net",
  'sec-fetch-site': "cross-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://en.greenconvert.net/",
  'priority': "u=1, i"
}

		response = requests.post(url, data=payload, headers=headers)

#print(response.text)
		h = response.json()['hash']

#import requests

		url1 = "https://v.ymcdn.org/api/v3/detail"

		payload1 = {
  'id': h,
  'format': '192k',
  'type': 'sound',
  'readType': 'sound',
  'direct': 'direct'
}

		headers1 = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua-platform': "\"Windows\"",
  'sec-ch-ua': "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Brave\";v=\"132\"",
  'sec-ch-ua-mobile': "?0",
  'sec-gpc': "1",
  'accept-language': "en-US,en;q=0.5",
  'origin': "https://en.greenconvert.net",
  'sec-fetch-site': "cross-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://en.greenconvert.net/",
  'priority': "u=1, i"
}

		response1 = requests.post(url1, data=payload1, headers=headers1)
		rr = response1.json()['fileUrl'][0]
		return {'link_audio':rr}
	else:
		return 'Faild , try again later ..'
hi= Audio_Url('https://youtu.be/GUaQEphtxC4')
print(hi)

def Video_Url(Link:str):
	if Link.startswith('https://youtu.be/') or Link.startswith('https://www.youtube.com/watch?v='):
		j = YoutubeSearch(Link).videos
	#print)
		url = "https://v.ymcdn.org/api/v3/init"
		payload = {'id': j[0]['id']}
		headers = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua-platform': "\"Windows\"",
  'sec-ch-ua': "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Brave\";v=\"132\"",
  'sec-ch-ua-mobile': "?0",
  'sec-gpc': "1",
  'accept-language': "en-US,en;q=0.5",
  'origin': "https://en.greenconvert.net",
  'sec-fetch-site': "cross-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://en.greenconvert.net/",
  'priority': "u=1, i"
}

		response = requests.post(url, data=payload, headers=headers)

#print(response.text)
		h = response.json()['hash']
#		import requests

		url1 = "https://v.ymcdn.org/api/v3/detail"

		payload1 = {
  'id': h,
  'format': '136',
  'type': 'video',
  'readType': 'video',
  'direct': 'direct'
}

		headers1 = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua-platform': "\"Windows\"",
  'sec-ch-ua': "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Brave\";v=\"132\"",
  'sec-ch-ua-mobile': "?0",
  'sec-gpc': "1",
  'accept-language': "en-US,en;q=0.5",
  'origin': "https://en.greenconvert.net",
  'sec-fetch-site': "cross-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://en.greenconvert.net/",
  'priority': "u=1, i"
}

		response1 = requests.post(url1, data=payload1, headers=headers1)

		print(response.text)
		rr = response1.json()['fileUrl'][0]
		return {'link_video':rr}
	else:
		return 'Faild , try again later ..'
	
print(Video_Url(Link='https://www.youtube.com/watch?v=WGf4KxT7VSU'))

 