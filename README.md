# Recommender System for Academic Papers
This project is a recommender system for research papers. Util the time this README is written, it contains 10,000
papers in the field of "Machine Learning", that are pulled from Semantic Scholar.

## Authors
The author of this project is Hsin-Chun Yin, under the instruction of professor Aviv Zohar and professor Katrina Ligett.
All the data have been saved under Hebrew University's Computer, under path:
cs/labs/avivz/hsiny/recommender_system

## Project Description
a description for the the project is on google docs:

    https://docs.google.com/document/d/1EK_9QxUY9jT1OrBiUZj2YqFGdfNEF67ETcktzGHHUDA/edit?usp=sharing
as well as instruction video for the project:  

    https://www.youtube.com/watch?v=4E4XfvXzOOo&ab_channel=Hsin-ChuYin

## How to run
If you wishes to run this project on your own computer here are the steps to follow:

**Step 1:** Clone the git repo and download the requirements.txt.  

**Step 2:** Set up environment variables  
You should add your Semantic Scholar API key under the environment variable name S2_API_KEY

You should add your OpenAI API key under the environment variable name OPENAI_API_KEY

**Step 3:** Download data source
To initialize the project, you needs to download all the papers from Semantic Scholar, and put them under path:
    
    ContentBasedRS/RawSource/papers

You may download papers of any field, but the papers must contain the following fields:
    
    paperId,title,authors,abstract,references.paperId,year,referenceCount,citationCount,influentialCitationCount

A sample code of requesting from Semantic Scholar is in (remember to add S2_API_KEY to $PATH):
    
    ContentBasedRS/RawSource/download_requests.py

I also provide my 10,000 papers that I download, under the google drive:
    
    https://drive.google.com/drive/folders/1x2roMv-mMj2TURdzJJi9dpXAT6ODFMu4?usp=sharing
**Step 4:** Initialize the databases
To initialize the project, the next step is to initialize the databases, simply and run the script:
    
    ContentBasedRS/initialize_databases.py

This process might take about half an hour, and costs about half a dollar per 10,000 papers. Notice: this process won't work if you didn't input valid OpenAI API key. And if you successfully run the initialization, all the function calls of OpenAI will be cached, so it won't cost money next time.

**Step 5:** Run the project
At the content root directory (the root of the project), run the following script:
    
    streamlit run user_interface.py




## How to run on Hebrew University's computer:
Here is the instruction on how to run the project on Hebrew University aquarium computers:
**Step 1:** move to /cs/labs/avivz/hsiny/recommender_system
**Step 2:** Only if you haven't set up the virtual environment for your computer, then run the following command:
    
    python -m venv my_venv
    source my_venv/bin/activate.csh
    pip install -r requirements.txt
    deactivate
**Step 3:** run the following commands to start the program:
    
    source my_venv/bin/activate.csh
    streamlit run user_interface.py

Or alternatively for step 2 and 3: just run the following command:
    
    sh run_the_app.sh
Or run
    
    sh run_the_app.sh new_venv




## How does the project work:
I set up a database for the papers, using sqlite. And based on the paper database, I created a profile database, which
contains the author id and name of all the authors of all the papers. Then for each author, I add all the papers he
wrote and referenced to his profile. For each paper, I use it's title and abstract to create an vector embedding through
OpenAI's embedding service.

### How does it recommend to the users:
There are primarily 3 ways of recommending:

cosine similarity:
The user can search papers in a certain field using keywords. Then the program will embed the keywords into a vector through OpenAI's embedding service. And then we will sort the papers by the cosine similarity between the paper's embedding and the keyword's embedding, and recommend the top 10.
The user can also claim to be an author that's recorded in the profile database. Then we will take all the papers that author write and referenced, and calculate average of embeddings of those papers, and then we will sort the papers in the content database by the cosine similarity between the paper's embedding and the average embedding, and recommend the top 10.
Also one can chose papers he like, after the program recommended. Then the liked papers will also be used to calculate the average embedding that "represents" the author. So once the user add a new liked paper, the recommendation to him will change.

sort by field:
Simply sort all papers by a certain field, such as published date, and recommend the top 10.

ensemble:
We will take the weighted average (of the users choice), of ranks in cosine similarity, and other fields such as year, referenced number, cited number, influential citation number. And sort the papers base on the new rank.










