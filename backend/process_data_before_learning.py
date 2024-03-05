import logging

# from sklearn.preprocessing import OneHotEncoder
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
# Start a session
dal = DataAccessLayer()
# Fetch data (might need adjustments)


babysitters = dal.get_all(models.Babysitter)
skills = dal.get_all(models.BabysitterSkill)
needs = dal.get_all(models.ChildrensNeeds)
favorites = dal.get_all(models.Favorite)
reviews = dal.get_all(models.Review)
contacted = dal.get_all(models.Contacted)
parents = dal.get_all(models.Parent)
childrens = dal.get_all(models.ParentsChildrens)

data_for_training = []


def process_data_for_training(parents, babysitters, favorites, reviews, contacted):
    data_for_training = []
    for parent in parents:
        for babysitter in babysitters:
            babysitter_data = {}
            babysitter_data["Babysitterid"] = babysitter.id
            # babysitter_data['Babysitter_Gender'] = babysitter.user.gender
            babysitter_data["Babysitter_Skills_Totalnum"] = len(babysitter.skills)
            Childs_Needs_Totalnum = 0
            for children in parent.childrens:
                Childs_Needs_Totalnum += len(children.needs)
            babysitter_data["Child_Needs_Totalnum"] = Childs_Needs_Totalnum
            babysitter_needs_answers = []
            Babysitter_Relevant_Skills_num = 0
            for skill in babysitter.skills:
                for need in skill.skill.skill_needs:
                    babysitter_needs_answers.append(need.needid)

            for child in parent.childrens:
                for need in child.needs:
                    if need.needid in babysitter_needs_answers:
                        Babysitter_Relevant_Skills_num += 1

            babysitter_data["Babysitter_Relevant_Skills_num"] = Babysitter_Relevant_Skills_num
            babysitter_data["Favorites_totalnum"] = sum(
                1 for favorite in favorites if favorite.babysitterid == babysitter.id
            )
            babysitter_data["Babysitter_Total_Reviews_got"] = sum(
                1 for review in reviews if review.reviewedid == babysitter.id
            )
            babysitter_data["Contacted"] = (
                1
                if (parent.id, babysitter.id) in [(contact.parentid, contact.babysitterid) for contact in contacted]
                else 0
            )

            data_for_training.append(babysitter_data)

    df = pd.DataFrame(data_for_training)
    return df


df = process_data_for_training(parents, babysitters, favorites, reviews, contacted)
print(df)


# Encoding categorical data
# encoder = OneHotEncoder()
# encoded_features = encoder.fit_transform(df[['Babysitter_Gender']]).toarray()
# encoded_feature_labels = encoder.get_feature_names(['Babysitter_Gender'])
# encoded_df = pd.DataFrame(encoded_features, columns=encoded_feature_labels)

# Combine the original DataFrame with the encoded features
# df = pd.concat([df, encoded_df], axis=1).drop(['Babysitter_Gender'], axis=1)

# Define features X and labels y
X = df.drop(["Contacted", "Babysitterid"], axis=1)  # Drop 'Contacted' and 'Babysitterid' columns
y = df["Contacted"]

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Initialize and train the Naive Bayes model
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)

# Test the model
y_pred = nb_model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

print(accuracy)


# Save the model for later use
joblib.dump(nb_model, "naive_bayes_model.joblib")

# Close the database session
