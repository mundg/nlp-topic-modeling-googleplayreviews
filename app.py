import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    st.set_page_config(layout="wide")
    data = pd.read_csv('./data/processed_streamlit/streamlit_app_data.csv', index_col=0).reset_index()

    page = st.selectbox("Navigate", ['Welcome',"Top Reviews! Influence Me!", "Data Insights (Developer, Community)"])

    if page == 'Welcome':
        st.title("🎯 Welcome to Influence Me!")
        st.markdown(
            """
            **An NLP Topic Modeling Dashboard Based on Google Play App Reviews**  
            ---
            📱 **Analyze app reviews effortlessly**  
            🧠 **Discover dominant topics and insights**  
            🎨 **Visualize trends with word clouds**  

            Get ready to dive into the world of app reviews and uncover the hidden patterns shaping user feedback. Explore genres, developers, ad impact, and more in one comprehensive platform.
            """
        )
        st.image("images/welcome_screen.png")


    elif page == "Top Reviews! Influence Me!":
        with st.sidebar:
            st.title('🎮 Influence me! \nGoogle Play Application Reviews')
            
            # Genre
            genre_list = list(data['genre'].unique())
            selected_genre = st.selectbox('Select a Genre', genre_list)
            # Likes
            likes_list = range(data['thumbsUpCount'].max() + 1)
            selected_likes = st.select_slider('Minimum Number of Likes', likes_list)
            # Topics
            nlp_topic_list = list(data['dominant_topic_meaning'].unique())
            selected_nlp_topic = st.selectbox('Select a Topic', nlp_topic_list)

            topics = {
                'Payment and Ads': 'images/topic_0.png',
                'Praise and Comparisons': 'images/topic_1.png',
                'Issues Concerns': 'images/topic_2.png',
                'Graphics & Gameplay': 'images/topic_3.png'

            }
                
            st.image(topics[selected_nlp_topic])
            
        filtered_data = data.copy()
        filtered_data = filtered_data.loc[(filtered_data['thumbsUpCount'] >= selected_likes) & (filtered_data['genre'] == selected_genre) & (filtered_data['dominant_topic_meaning'] == selected_nlp_topic)
                                        ,['content','title','thumbsUpCount','userName']].sort_values(by = 'thumbsUpCount', ascending=False)
        st.table(filtered_data.rename(columns={'dominant_topic_meaning':'Dominant Topic', 'content': 'Review Content', 'title': 'App Title'}))


    elif page == 'Data Insights (Developer, Community)':
        with st.sidebar:

            st.title('🎮 Find your Insights!')
            st.image('images/topic_0.png', caption='Payment and Ads')
            st.image('images/topic_1.png', caption='Praise and Comparisons')
            st.image('images/topic_2.png', caption='Issues Concerns' )
            st.image('images/topic_3.png', caption='Graphics & Gameplay')
        
        filtered_data = data.copy()
        sub_page = st.segmented_control('Choose Your Topic of Interest', ["Bug/Issues Topics - Developers", "Ads? Topics", "Game Topics Info (For Developers)"])

        if sub_page == "Bug/Issues Topics - Developers":
            st.title('Issues Concerns Topic Distribution per Developer')
            bug_topics_plot = filtered_data.loc[filtered_data['dominant_topic'] == 2, 'developer'].value_counts().reset_index()
            fig, ax = plt.subplots(figsize = (7, 10))
            sns.barplot(bug_topics_plot, x = 'count', y = 'developer',  alpha = 0.2, color = 'blue')
            ax.set_xlabel('Review Counts')
            ax.set_ylabel('Game Developer Name')
            st.pyplot(fig)
        elif sub_page == 'Ads? Topics':
            st.title('Ad-Free or Not? Topics')
            ads_plot = filtered_data[['containsAds','dominant_topic_meaning']].value_counts().reset_index()
            fig, ax = plt.subplots(1,2,figsize = (11,5))
            for ads_flag, axis in zip(ads_plot['containsAds'].unique(), ax.flatten()):
                filter_plot_contains = ads_plot[ads_plot['containsAds'] == ads_flag]
                sns.barplot(filter_plot_contains, x = 'dominant_topic_meaning', y = 'count', ax = axis, alpha = 0.4, color = 'red')
                axis.set_title(f"{'Games with ADS' if ads_flag == True else 'Games without ADS'}")
                axis.set_xlabel('Dominant Topic')
                axis.set_ylabel('Review Counts')
                axis.set_facecolor('white')
                axis.tick_params(axis='x', labelrotation=45)
                axis.grid(True, alpha = 0.05)
            fig.tight_layout()
            st.pyplot(fig)
        elif sub_page == 'Game Topics Info (For Developers)':
            st.title('Check your Game/s! 🎮🕹️')
            games_list = list(data['title'].unique())
            selected_game = st.selectbox('Game List', games_list)
            filtered_data = filtered_data.loc[(filtered_data['title'] == selected_game), ['dominant_topic_meaning','content','title','thumbsUpCount','userName']]
            dominant_topics_dist = 100*filtered_data['dominant_topic_meaning'].value_counts()/filtered_data.shape[0]
            fig, ax = plt.subplots(figsize = (8,8))
            plt.pie(dominant_topics_dist, labels = dominant_topics_dist.index, autopct='%0.2f%%', colors=sns.color_palette('Set2')) 
            plt.title('Topics Distribution of Influential Users')
            fig.tight_layout()
            st.pyplot(fig)
            st.text('Your Top Review!')
            st.table(filtered_data.rename(columns={'dominant_topic_meaning':'Dominant Topic', 'content': 'Review Content', 'title': 'App Title'}).sort_values(by = 'thumbsUpCount', ascending=False).head(1))

if __name__ == '__main__':
    main()