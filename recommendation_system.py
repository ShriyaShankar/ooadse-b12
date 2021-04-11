# Recommender for Video Management Platform

# The recommendation system takes the link of the video as input and returns titles of top 10 most similar videos. This is done as a combination of two methods:
# 
# - Computing similarity based on titles using TfIdf Vectorization
# - Computing a score for each video based on number of views, likes and dislikes
# 
# The latter step is necessary so that there is some standard that the videos recommeded can be held to. 
# 
# The total score is weighted and computed as 0.7 * tfidf score + 0.3 * quality score.
# 
# Note: The quality score is not static and hence cannot be computed only at the very beginning of the system's functioning. It has to be calculated everytime a request is made to the recommendation system.

# ## Importing libraries and accessing data
import pandas as pd 
import numpy as np 
import matplotlib as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import sys
import time
import os

class recommendationSystem:

    def __init__(self, dataset):
        try:
            self.dataset = pd.read_csv(dataset)
            # self.dataset = pd.read_csv("test_videos1.csv")
        except Exception as e:
            self.error("Database of videos not found!", e)

# ## Helper functions
    def strip_views(self,string): # convert the string values to integers
        string = string.split(' ')[0]
        number = int(string.replace(",",""))
        return number

    def strip_likes(self,string): # convert string values to appropriate integers
        temp = string.split(' ')[0]
        try:
            if 'K' in temp:
                temp = temp.replace("K","")
                number = int(float(temp)*1000)
            elif 'M' in temp:
                temp = temp.replace("M","")
                number = int(float(temp)*1000000)
            else:
                number = int(temp)
            return number
    
        except Exception as e:
            print(string)
            print("Error:", e)

    def invert_dislikes(self,number): # This is to account for the decrease in quality when people dislike videos
        if number == 0:
            return number
        return -number

    # ## Function to preprocess data

    def preprocess(self,videos):
        # global videos
        try:
            videos = videos.drop(columns=["Comments"]) # dropping comments as inclusion leads to unneccesary complications
            videos = videos.dropna()
            videos = videos[videos['Likes on Video']!='LIKE'] # special case 
            videos['Views'] = videos['Views'].apply(self.strip_views)
            videos['Likes on Video'] = videos['Likes on Video'].apply(self.strip_likes)
            videos["Dislikes on Video"] = videos['Dislikes on Video'].apply(self.strip_likes)
            videos["Dislikes on Video"] = videos['Dislikes on Video'].apply(self.invert_dislikes)

            return videos
        except Exception as e:
            self.error("Preprocessing failed - atrribute mismatch!", e)

    def score_att(self, view, likes, dislikes): # to score based on quality of video
        return (likes + dislikes)/view

    def get_recommendations(self, title, dataset = None):
        if dataset is None:
            videos = self.preprocess(self.dataset)
        else:
            videos = self.preprocess(dataset)
        
        index = videos[videos['Video Title']==title].index.values
        if list(index) == []:
            self.error("Video not found!", None)
        # if index == None:
        #     self.error("Video not found!",None)
        # Title Similarity

        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(videos['Video Title'])  
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix) # cosine similarity used
        title_similarity = list(cosine_sim[index[0]]) 

        # Attribute Similarity - Views, Likes, Dislikes
        
        attributes = ['Views','Likes on Video','Dislikes on Video']
        video_att = videos[attributes]

        score = []

        for index, row in video_att.iterrows():
            score.append(self.score_att(row['Views'],row['Likes on Video'], row['Dislikes on Video']))
        
        # Combining Title as well as Attribute Similarity - Weighted
        similarity = enumerate([0.7*title_similarity[i] + 0.3*score[i] for i in range(len(score))])
        sorted_scores = sorted(similarity, key = lambda x: x[1], reverse=True)
        try:
            sim_scores = sorted_scores[1:12] # Top 10 recommended
            if sim_scores == []:
                self.error("No recommendations found!",None)

        except Exception as e:
            self.error("Recommendations not found!", e)
        
        video_titles = [i[0] for i in sim_scores]
        return list(videos['Video Title'].iloc[video_titles])

    def iterative_recommender(self, dataset, title):
        recommendations = self.get_recommendations(video)#, self.dataset)
        user_opinion = "Y" # Happy with recommendations
        if video in recommendations:
            recommendations.remove(video)
        os.system('cls')
        print("Video:",video)
        print("Recommendations: ")
        print("-----------------------------------------------")
        for video_title in recommendations: 
            print(video_title)

        user_opinion = input("\nAre you satisfied with the recommendations? (Y/N): ")
        
        while user_opinion != 'Y':
            bad_recs = input("Enter all unsatisfactory recommendation numbers (starting from 1) separated by comma: ").split(',')
            # print(bad_recs)
            
            for i in bad_recs:
                dataset = dataset[dataset['Video Title']!=recommendations[int(i)]]

            recommendations = self.get_recommendations(video, dataset)
            # user_opinion = "Y" # Happy with recommendations
            if video in recommendations:
                recommendations.remove(video)

            os.system('cls')
            print("Video:",video)
            print("Recommendations: ")
            print("-----------------------------------------------")
            for video_title in recommendations: 
                print(video_title)
            
            user_opinion = input("\nAre you satisfied with the recommendations? (Y/N): ")
            
    
    def error(self, error_text, e):
        print("\nError!", error_text)
        if e != None:
            print("---------------------")
            print("Python resulted in error:",e)
        print("Terminating Program...")
        time.sleep(3)
        print()
        exit(0)


if __name__=='__main__':
    try:
        dataset = "data/" + sys.argv[1]
        recommender = recommendationSystem(dataset)
        video = sys.argv[2]
    except Exception as e:
        print("No video title and/or dataset passed as command line arguments!")
        print("Terminating Program...")
        time.sleep(3)
        print()
        exit(0)
    
    recommender.iterative_recommender(recommender.dataset,video)
    
    
    print()



