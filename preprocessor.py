import re
import pandas as pd
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
    df['day'] =df['date'].dt.day
    df['hour'] =df['date'].dt.hour
    df['minute'] =df['date'].dt.minute
    
    return df

    
