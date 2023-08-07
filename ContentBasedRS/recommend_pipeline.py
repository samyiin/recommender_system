from ContentBasedRS.ContentAnalyzer import *
from ContentBasedRS.ProfileLearner import *
from ContentBasedRS.FilteringComponent import *
from ContentBasedRS.Utils import *



def order_by_numerical_field():
    """Task two: recommend by citation/referenced number"""
    # connect to contentDB and profile db
    profileDB = ProfileDB()
    contentDB = ContentDB()

    # recommend papers based on cosine similarity of user and paper
    recommender = Recommender(contentDB, profileDB)
    recommend = recommender.order_by_number(contentDB.COL_YEAR)
    print(recommend)
    print("---------------------------------------")

    recommend = recommender.order_by_number(contentDB.COL_REF_COUNT)
    print(recommend)
    print("---------------------------------------")

    recommend = recommender.order_by_number(contentDB.COL_CITE_COUNT)
    print(recommend)
    print("---------------------------------------")

    recommend = recommender.order_by_number(contentDB.COL_INFLUENTIAL_CITE_COUNT)
    print(recommend)
    print("---------------------------------------")


def ensemble(author_id=4565995):
    """task three: take many factor into consideration -> weighted linear combination ranking
    """
    # connect to contentDB and profile db
    profileDB = ProfileDB()
    contentDB = ContentDB()

    # select an author from profile database
    known_papers = profileDB.get_author_known_papers(author_id)
    author_embedding = profileDB.get_author_embedding(author_id, contentDB)
    exclude_known_papers = []
    for paper_set in known_papers.values():
        exclude_known_papers += list(paper_set)

    # recommend papers based on cosine similarity of user and paper
    recommender = Recommender(contentDB, profileDB)
    recommend = recommender.weighted_linear_combination_ranking(author_embedding, exclude_known_papers, 0.7, 0.1, 0.1, 0.05, 0.05)
    print(recommend)
    print("---------------------------------------")


def recommend_after_feedback(author_id=4565995):
    """Task one: recommend by cosine similarity"""
    # connect to contentDB and profile db
    profileDB = ProfileDB()
    contentDB = ContentDB()

    # reset the selected author
    profileDB.clear_liked_papers(author_id)
    profileDB.commit_change()

    # select an author from profile database
    known_papers = profileDB.get_author_known_papers(author_id)
    author_embedding = profileDB.get_author_embedding(author_id, contentDB)
    exclude_known_papers = []
    for paper_set in known_papers.values():
        exclude_known_papers += list(paper_set)

    # recommend papers based on cosine similarity of user and paper
    recommender = Recommender(contentDB, profileDB)
    recommend = recommender._sort_by_vector_similarity(author_embedding, exclude_known_papers)
    print(recommend)
    print("---------------------------------------")

    # # assume the user really likes the first 5 papers
    # liked_papers = set(recommend[:5][contentDB.COL_PAPER_ID].tolist())
    # new_known_papers = {profileDB.PAPER_KIND_LIKED: liked_papers}
    # author_name = result[0][profileDB.get_col_index(profileDB.COL_NAME)]
    # profileDB.update_author(4565995, author_name, new_known_papers)
    # profileDB.commit_change()
    print("---------------------------------------")

    # give the second recommender
    # select an author from profile database
    result, _ = profileDB.query_database(
        f"select * from {profileDB.MAIN_TABLE_NAME} where {profileDB.COL_AUTHOR_ID} = {author_id}")
    known_papers = BLOB_to_info(result[0][profileDB.get_col_index(profileDB.COL_KNOWN_PAPERS)])
    author_embedding = profileDB.get_author_embedding(known_papers, contentDB)
    exclude_known_papers = []
    for paper_set in known_papers.values():
        exclude_known_papers += list(paper_set)

    # recommend papers based on cosine similarity of user and paper
    recommender = Recommender(contentDB, profileDB)
    recommend = recommender._sort_by_vector_similarity(author_embedding, exclude_known_papers)
    print(recommend)
    print("---------------------------------------")

def recommend_by_search(keywords="medical images"):
    # connect to contentDB and profile db
    profileDB = ProfileDB()
    contentDB = ContentDB()

    # search the keyword
    recommender = Recommender(contentDB, profileDB)
    keyword_embedding = OpenAIEmbedding.embed_short_text(keywords)

    recommend = recommender.search_engine(keyword_embedding)

    return recommend

def search_author_by_name(name="Kevin"):
    profileDB = ProfileDB()
    contentDB = ContentDB()
    recommender = Recommender(contentDB, profileDB)
    result = profileDB.search_author_by_name(name)
    return result
if __name__ == "__main__":
    profileDB = ProfileDB()
    contentDB = ContentDB()
    recommender = Recommender(contentDB, profileDB)
    # recommender.recommend_to_author("11819898")

    order_by_numerical_field()
    # #
    # ensemble()
    # #
    # recommend_after_feedback()
    #
    # recommend_by_search()
    # search_author_by_name()