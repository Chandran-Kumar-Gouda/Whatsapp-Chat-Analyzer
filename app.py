import streamlit as st
import preprocessor
import pandas as pd
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()  # Read file content as bytes because it is default
    data = bytes_data.decode("utf-8")  # converting byte data to string
    
    df = preprocessor.preprocess(data)  # preprocess text to DataFrame
    st.dataframe(df)

    # fetch unique user

    user_list  = df['user'].unique().tolist()    # getting unique user because analysis is done on group level and user level
    user_list.remove('group_notification')       # removing group_notification to insert a new name
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt" ,user_list)  # Dropdown in sidebar to select a user for analysis

    if st.sidebar.button("show analysis"):
        num_messages , total_words ,total_media , total_links ,avg_msgs_per_day  ,avg_words_per_msg  ,most_active_date ,total_emojis  = helper.fetch_stats(selected_user ,df)
        st.title("Top Statictics")
        col1 ,col2 ,col3, col4 = st.columns(4)  #Splits the Streamlit layout into 4 horizontal columns side-by-side.

        with col1:
            st.header("Total messages")
            st.title(num_messages)
        with col2:
            st.header("Total words")
            st.title(total_words)
        
        with col3:
            st.header("Media shared")
            st.title(total_media)
        
        with col4:
            st.header("Total links")
            st.title(total_links)
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.header("Avg Msgs per Day")
            st.title(avg_msgs_per_day)
        with col6:
            st.header("Avg Words per Msg")
            st.title(avg_words_per_msg)
        with col7:
            st.header("Most Active Date")
            st.title(str(most_active_date))
        with col8:
            st.header("Total Emojis Used")
            st.title(total_emojis)
        
        # monthly timeline
        st.title("Monthly Timeline")
        monthly_timeline = helper.monthly_timeline(selected_user ,df)
        fig ,ax = plt.subplots()
        ax.plot(monthly_timeline['time'] , monthly_timeline['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        
        # daily timeline
        st.title("Daily Timeline")
        Daily_timeline = helper.daily_timeline(selected_user ,df)
        fig ,ax = plt.subplots()
        ax.plot(Daily_timeline['only_date'] , Daily_timeline['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        
        # activity map
        st.title('Activity map')
        col1, col2 = st.columns(2)
        
        with col1:
            st.title("Most busy day")
            weekly_user = helper.weekely_activity_map(selected_user,df)
            fig ,ax = plt.subplots()
            ax.plot(weekly_user.index ,weekly_user.values ,color ='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        
        with col2:
            st.title("Most busy month")
            monthly_user = helper.monthly_activity_map(selected_user,df)
            fig ,ax = plt.subplots()
            ax.plot(monthly_user.index ,monthly_user.values ,color ='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # weekly heatmap 
        st.title("Weekly Heatmap")
        user_heatmap = helper.weekly_heatmap(selected_user,df)
        fig ,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # Findind the busiest user in the group

        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x  ,new_df= helper.most_busiest_users(df)

            fig ,ax = plt.subplots()

            col1 ,col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color="green")
                ax.set_xlabel("Users")
                ax.set_ylabel("Number of Messages")
                ax.set_title("Top Active Users")
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            
            with col2:
                st.dataframe(new_df)
        
        # Word Cloud
        st.title("Word Cloud")
        df_wc = helper.create_wordCloud(selected_user, df)
        fig ,ax = plt.subplots()
        ax.imshow(df_wc.to_array(), interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # most common words 
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)

        if most_common_df.empty:
            st.warning("No common words found for the selected user.")
        else:
            fig, ax = plt.subplots()
            ax.barh(most_common_df.iloc[:, 0], most_common_df.iloc[:, 1], color='skyblue') 
            plt.xticks(rotation="vertical")
            st.pyplot(fig)
        
        # emoji Analysis

        plt.rcParams['font.family'] = 'Segoe UI Emoji'

        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1 ,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        
        with col2:
            emoji_df =emoji_df.head(10)
            fig ,ax = plt.subplots()
            ax.pie(emoji_df.iloc[:,1] ,labels=emoji_df.iloc[:,0] , autopct="%0.2f" ,startangle=90 ) # displaying a pie chart for top 10 emojis
            ax.axis("equal")  # Make pie chart circular
            st.pyplot(fig)
    
        

            

