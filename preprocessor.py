import re
import pandas as pd
from textblob import TextBlob

def preprocess(data):
    data = data.replace('\u202f', ' ')
    
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:am|pm|[apAP]\u202f?[mM])\s-\s'

    messages = re.split(pattern,data)[1:]

    dates = re.findall(pattern,data)
    
    df =pd.DataFrame({'user_message':messages, 'message_date':dates})
    # Clean message_date strings by removing ' - ' at the end
    df['message_date'] = df['message_date'].str.replace(' - ', '', regex=False)

    # Convert to datetime format
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # seperate user and message

    users =[]
    messages =[]

    for message in df['user_message']:
        # Remove HTML-like tags
        message = re.sub(r'<[^>]+>', '', message)

        # Remove code-like variable assignments or function calls
        message = re.sub(r'\w+\s*=\s*[^,\s]+', '', message)  # e.g., x = 5
        message = re.sub(r'\w+\([^)]*\)', '', message) 
        entry = re.split('([\w\W]+?):\s',message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:         # plain message
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] =users
    df['message'] =messages
    df.drop(columns =['user_message'] ,inplace =True)
    
    df['Year']=df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] =df['date'].dt.day
    df['hour'] =df['date'].dt.hour
    df['minute'] =df['date'].dt.minute
    df['only_date'] = df['date'].dt.date
    df['dayname'] = df['date'].dt.day_name()
    df['month_peroid'] = pd.to_datetime(df['date']).dt.to_period('M')
    peroids =[]

    for hour in df[['dayname' ,'hour']]['hour']:
        if hour == 23:
            peroids.append(str(hour) + "-" +str('00'))
        elif hour == 0:
            peroids.append(str('00') + "-" +str(hour +1))
        else:
            peroids.append(str(hour) + "-" +str(hour+1))
    df['peroids'] =peroids 

    def get_sentiment(message):
        try:
            blob = TextBlob(message)
            polarity = blob.sentiment.polarity
            if polarity > 0.2:
                return 'Positive'
            elif polarity < -0.2:
                return 'Negative'
            else:
                return 'Neutral'
        except:
            return 'Neutral' 
    df['Sentiment'] = df['message'].apply(get_sentiment) 

    all_dates = pd.date_range(start=df['only_date'].min(), end=df['only_date'].max())
    active_dates = df['only_date'].unique()
    inactive_days = [d.date() for d in all_dates if d.date() not in active_dates]
    df.attrs['num_inactive_days'] = len(inactive_days)  # store as attribute
     
    return df

    
   

    
