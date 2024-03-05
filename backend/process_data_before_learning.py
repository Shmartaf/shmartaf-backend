import logging

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

from backend.database import models
from backend.database.dal import DataAccessLayer

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
dal = DataAccessLayer()


def load_data(dal):
    babysitters = dal.get_all(models.Babysitter)
    # skills = dal.get_all(models.BabysitterSkill)
    # needs = dal.get_all(models.ChildrensNeeds)
    favorites = dal.get_all(models.Favorite)
    reviews = dal.get_all(models.Review)
    contacted = dal.get_all(models.Contacted)
    parents = dal.get_all(models.Parent)
    # childrens = dal.get_all(models.ParentsChildrens)

    return parents, babysitters, favorites, reviews, contacted


def process_data_for_training(parents, babysitters, favorites, reviews, contacted):
    data_for_training = []
    for parent in parents:
        for babysitter in babysitters:
            babysitter_data = {}
            babysitter_data["Babysitterid"] = babysitter.id
            try:
                babysitter_data["Babysitter_Skills_Totalnum"] = len(babysitter.skills)
            except Exception:
                babysitter_data["Babysitter_Skills_Totalnum"] = 0
            try:
                Childs_Needs_Totalnum = sum(len(children.needs) for children in parent.childrens)
            except Exception:
                Childs_Needs_Totalnum = 0
            babysitter_data["Child_Needs_Totalnum"] = Childs_Needs_Totalnum
            try:
                babysitter_needs_answers = [
                    need.needid for skill in babysitter.skills for need in skill.skill.skill_needs
                ]
                Babysitter_Relevant_Skills_num = sum(
                    1 for child in parent.childrens for need in child.needs if need.needid in babysitter_needs_answers
                )
                babysitter_data["Babysitter_Relevant_Skills_num"] = Babysitter_Relevant_Skills_num
                babysitter_data["Favorites_totalnum"] = sum(
                    1 for favorite in favorites if favorite.babysitterid == babysitter.id
                )
            except Exception:
                babysitter_data["Babysitter_Relevant_Skills_num"] = 0
                babysitter_data["Favorites_totalnum"] = 0
            try:
                babysitter_data["Babysitter_Total_Reviews_got"] = sum(
                    1 for review in reviews if review.reviewedid == babysitter.id
                )
                babysitter_data["Contacted"] = int(
                    (parent.id, babysitter.id) in {(contact.parentid, contact.babysitterid) for contact in contacted}
                )
            except Exception:
                babysitter_data["Babysitter_Total_Reviews_got"] = 0
                babysitter_data["Contacted"] = 0
            data_for_training.append(babysitter_data)

    df = pd.DataFrame(data_for_training)
    return df


def train_model(df):
    X = df.drop(["Contacted", "Babysitterid"], axis=1)
    y = df["Contacted"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    nb_model = GaussianNB()
    nb_model.fit(X_train, y_train)

    y_pred = nb_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("Model Accuracy:", accuracy)

    joblib.dump(nb_model, "naive_bayes_model.joblib")
