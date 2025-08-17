import streamlit as st
import preprocessor
import pandas as pd
import helper
import matplotlib.pyplot as plt
import seaborn as sns
from bertopic import BERTopic
import sys
import base64      
import tempfile 

sys.stdout.reconfigure(encoding='utf-8')
st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()  # Read file content as bytes because it is default
    data = bytes_data.decode("utf-8-sig") # converting byte data to string
    
    df = preprocessor.preprocess(data)  # preprocess text to DataFrame
    st.dataframe(df)

    # fetch unique user

    user_list  = df['user'].unique().tolist()    # getting unique user because analysis is done on group level and user level
    user_list.remove('group_notification')       # removing group_notification to insert a new name
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt" ,user_list)  # Dropdown in sidebar to select a user for analysis

    if st.sidebar.button("show analysis"):
        num_messages , total_words ,inactive_days , total_links ,avg_msgs_per_day  ,avg_words_per_msg  ,most_active_date ,total_emojis  = helper.fetch_stats(selected_user ,df)
        st.title("Top Statictics")
        col1 ,col2 ,col3, col4 = st.columns(4)  #Splits the Streamlit layout into 4 horizontal columns side-by-side.

        with col1:
            st.header("Total messages")
            st.title(num_messages)
        with col2:
            st.header("Total words")
            st.title(total_words)
        
        with col3:
            st.header("Inactive days")
            st.title(inactive_days)
        
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
        
        # USER PROFILING
        st.title("User Profiling")
        profiles = helper.user_profiling(df)
        st.dataframe(profiles)

        # FORECASTING 
        st.title("Message Forecasting")
        forecast = helper.forecast_activity(df, periods=7)
        fig, ax = plt.subplots()
        ax.plot(forecast['ds'], forecast['yhat'], label="Predicted")
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], alpha=0.2)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # CHATBOT SUMMARY 
        st.title("Chatbot Summary")
        summary = helper.generate_summary(df, selected_user)
        st.success(summary)

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

        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1 ,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
                
        with col2:
            fig = helper.emoji_pie_chart(df, selected_user)
            if fig:
                st.pyplot(fig)

                img_path = helper.save_plot(fig)

    
        # Sentiment Analysis
        st.title("Sentiment Analysis")
        sentiment_count = helper.get_Sentiment(selected_user ,df)
        
        fig ,ax = plt.subplots()
        ax.bar(sentiment_count.index , sentiment_count.values )
        st.pyplot(fig)

         # REPORT DOWNLOAD 
        st.title("Download Full Report")

        # Dictionary to store images
        plot_images = {}

        # 1. Monthly Timeline
        fig, ax = plt.subplots()
        ax.plot(helper.monthly_timeline(selected_user, df)['time'], helper.monthly_timeline(selected_user, df)['message'])
        plt.xticks(rotation='vertical')
        plot_images['monthly_timeline'] = helper.save_plot(fig)

        # 2. Daily Timeline
        fig, ax = plt.subplots()
        ax.plot(helper.daily_timeline(selected_user, df)['only_date'], helper.daily_timeline(selected_user, df)['message'])
        plt.xticks(rotation='vertical')
        plot_images['daily_timeline'] = helper.save_plot(fig)

        # 3. Weekly Heatmap
        fig, ax = plt.subplots()
        sns.heatmap(helper.weekly_heatmap(selected_user, df), ax=ax)
        plot_images['weekly_heatmap'] = helper.save_plot(fig)

        # 4. Busiest Users (if Overall)
        if selected_user == "Overall":
            x, new_df = helper.most_busiest_users(df)
            fig, ax = plt.subplots()
            ax.bar(x.index, x.values, color="green")
            plt.xticks(rotation='vertical')
            plot_images['busiest_users'] = helper.save_plot(fig)

        # 5. Word Cloud
        df_wc = helper.create_wordCloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc.to_array(), interpolation='bilinear')
        ax.axis("off")
        plot_images['wordcloud'] = helper.save_plot(fig)

        # 6. Emoji Pie Chart
        fig = helper.emoji_pie_chart(df, selected_user)
        if fig:
            plot_images['emoji_pie'] = helper.save_plot(fig)

        # 7. Sentiment Analysis
        sentiment_count = helper.get_Sentiment(selected_user, df)
        fig, ax = plt.subplots()
        ax.bar(sentiment_count.index, sentiment_count.values)
        plot_images['sentiment'] = helper.save_plot(fig)

        # Convert all plots to base64
        plot_base64 = {}
        for key, path in plot_images.items():
            with open(path, "rb") as f:
                plot_base64[key] = base64.b64encode(f.read()).decode()

        # Build HTML for PDF report
        report_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: "Segoe UI Emoji", "Noto Color Emoji", Arial, sans-serif; }}
                h1 {{ color: #2E86C1; }}
                h2 {{ color: #117864; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>WhatsApp Chat Analysis Report</h1>

            <h2>Chatbot Summary</h2>
            <p>{helper.generate_summary(df, selected_user)}</p>

            <h2>Top Statistics</h2>
            <ul>
                <li>Total Messages: {num_messages}</li>
                <li>Total Words: {total_words}</li>
                <li>Inactive days: {inactive_days}</li>
                <li>Total Links: {total_links}</li>
                <li>Avg Messages/Day: {avg_msgs_per_day}</li>
                <li>Avg Words/Message: {avg_words_per_msg}</li>
                <li>Most Active Date: {most_active_date}</li>
                <li>Total Emojis: {total_emojis}</li>
            </ul>

            <h2>Monthly Timeline</h2>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{plot_base64['monthly_timeline']}" width="600"/>
            </div>

            <h2>Daily Timeline</h2>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{plot_base64['daily_timeline']}" width="600"/>
            </div>

            <h2>Weekly Heatmap</h2>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{plot_base64['weekly_heatmap']}" width="600"/>
            </div>
        """

        if selected_user == "Overall":
            report_html += f"""
            <h2>Busiest Users</h2>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{plot_base64['busiest_users']}" width="600"/>
            </div>
            {new_df.to_html(index=False)}
            """

        report_html += f"""
        <h2>Word Cloud</h2>
        <div style="text-align:center;">
            <img src="data:image/png;base64,{plot_base64['wordcloud']}" width="600"/>
        </div>

        <h2>Emoji Analysis (Top 10)</h2>
        <div style="text-align:center;">
            <img src="data:image/png;base64,{plot_base64.get('emoji_pie', '')}" width="400"/>
        </div>
        {helper.emoji_helper(selected_user, df).head(10).to_html(index=False)}

        <h2>Sentiment Analysis</h2>
        <div style="text-align:center;">
            <img src="data:image/png;base64,{plot_base64['sentiment']}" width="600"/>
        </div>

        <h2>User Profiling</h2>
        {helper.user_profiling(df).to_html()}

        <h2>Topics in Chat</h2>
        {pd.DataFrame(helper.extract_topics(selected_user, df)).to_html()}

        </body>
        </html>
        """

        # Generate PDF
        from utils.report_generator import generate_report
        pdf_file = generate_report(report_html)

        # Download button
        with open(pdf_file, "rb") as f:
            st.download_button(
                "📄 Download Full Report",
                f,
                file_name="chat_report.pdf",
                mime="application/pdf"
            )



