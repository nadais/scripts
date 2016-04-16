import codecs
import json
from urllib2 import urlopen
from datetime import timedelta,date
from operator import itemgetter
import time
import datetime
import requests
import os
import unicodedata
exportsDirectory="Replace this by the directory where you want to save your exports"; 
token="your_user_token";
usersRequest=urlopen("https://slack.com/api/users.list?token="+token);
users=json.loads(usersRequest.read())[unicode("members")];
def writeToFiles(filesArray,stringToWrite):
	for fileOutput in filesArray:
		fileOutput.write(stringToWrite);

user_ids={};
for i in users:
	if(i['profile']['real_name_normalized']==""):
		user_ids[i['id']]=i['name'];
	else:
		user_ids[i['id']] = i['profile']['real_name_normalized']
channelsRequest=urlopen("https://slack.com/api/channels.list?token="+token);
channels=json.loads(channelsRequest.read())[unicode("channels")];
limitdate=date.today() - timedelta(days=1);
dateString=limitdate.strftime('%d/%m/%Y')
todayString=date.today().strftime('%d/%m/%Y');
timestamp=time.mktime(datetime.datetime.strptime(dateString, "%d/%m/%Y").timetuple())
todaystamp=time.mktime(datetime.datetime.strptime(todayString, "%d/%m/%Y").timetuple())
api_data={};
#To send a message to your slack channel create an incoming webhook and set the value of link variable to the link of the webhook
firstMessage={"username":"historyBot","channel":"#notifications","text": "Starting to import history for "+dateString+"\n"}
link=""#webhook link value
requests.post(link,data=json.dumps(firstMessage));

for channel in channels:
	hasMore=True;
	while hasMore == True:
		url = urlopen("https://slack.com/api/channels.history?token="+token+"&channel="+channel[unicode("id")]+"&count=1000&latest="+str(todaystamp)+"&oldest="+str(timestamp));
		channelData=json.loads(url.read());
		hasMore=channelData[unicode("has_more")]
		if(len(channelData[unicode("messages")])>0):
			s=channel[unicode("name")];
			if hasattr(api_data,s):
				api_data[s].extend(sorted(channelData[unicode("messages")], key=itemgetter(unicode('ts')))); 
			else:
				api_data[s]=sorted(channelData[unicode("messages")], key=itemgetter(unicode('ts')));
			if hasMore==True:
				print channel[unicode("name")];
				timestamp=float(channelData[unicode("messages")][len(channelData[unicode("messages")])-1][unicode("ts")]);
for key,value in api_data.iteritems():
	if not os.path.exists(exportsDirectory+"/"+str(limitdate.year)):
		os.makedirs(exportsDirectory+"/"+str(limitdate.year))
	if not os.path.exists(exportsDirectory+"/"+str(limitdate.year)+"/"+str(limitdate.month)):
		os.makedirs(exportsDirectory+"/"+str(limitdate.year)+"/"+str(limitdate.month))
	backup = codecs.open(exportsDirectory+"/"+str(limitdate.year)+"/"+str(limitdate.month)+"/"+key+'.txt', mode='a', encoding ='utf-8');
	out = codecs.open(exportsDirectory+key+'.txt', mode='a', encoding ='utf-8')
	dateString="";
	for i in value:
		currentDateString=datetime.datetime.fromtimestamp(float(i[unicode("ts")])).strftime('%d-%m-%Y')
		if currentDateString != dateString:
			dateString=currentDateString;
			writeToFiles([out,backup],dateString+'\r\n');
		temp='';
		if("subtype" in i):
			if(i['subtype'] == 'channel_join'):
				temp="Joined the channel";
			elif (i['subtype']=='file_share'):
				temp='Has shared a file';
			elif (i['subtype']=='bot_message'):
				temp = i['text'];
		else:
			temp=i['text'];
		index = 0;
		while index < len(temp):
			index = temp.find('@', index)
			if index == -1:
				break;
			if temp[index-1]!='<':
				break;
			pre = temp[0:index+1];
			post = temp[index+10:len(temp)];
			if temp[index+1:index+10] in user_ids:
				temp = pre + user_ids[temp[index+1:index+10]] + post;
			index += 2;
		if i.get('user') in user_ids:
			writeToFiles([out,backup],user_ids[i['user']] + ': ' + temp + '\r\n');
		else:
			writeToFiles([out,backup],'Bot message: ' + temp + '\r\n');

lastMessage={"username":"historyBot","channel":"#notifications","text": "Channels history imported for "+dateString+"\n Content can be seen in blablabla"}
requests.post(link,data=json.dumps(lastMessage));
