import joblib
import pandas as pd

from backend.database import models
from backend.database.dal import DataAccessLayer

dal = DataAccessLayer()
# Load the trained Naive Bayes model
model_path = "naive_bayes_model.joblib"
nb_model = joblib.load(model_path)


def create_input_data_for_parent(parentid):
    # Initialize a list to hold data for each babysitter
    data_for_prediction = []

    # Assuming these functions fetch data for the specified parent and all babysitters
    parent = dal.get(models.Parent, parentid)
    babysitters = dal.get_all(models.Babysitter)

    # Loop through each babysitter to create a feature set
    for babysitter in babysitters:
        babysitter_data = {}

        # Add babysitter-specific features
        babysitter_data["Babysitterid"] = babysitter.id
        babysitter_data["Babysitter_Skills_Totalnum"] = len(babysitter.skills)

        # Calculate the total number of children's needs for the parent
        Childs_Needs_Totalnum = sum(len(child.needs) for child in parent.childrens)
        babysitter_data["Child_Needs_Totalnum"] = Childs_Needs_Totalnum

        # Calculate how many of the babysitter's skills match the children's needs
        Babysitter_Relevant_Skills_num = 0
        babysitter_needs_answers = [need.needid for skill in babysitter.skills for need in skill.skill.skill_needs]
        for child in parent.childrens:
            for need in child.needs:
                if need.needid in babysitter_needs_answers:
                    Babysitter_Relevant_Skills_num += 1

        babysitter_data["Babysitter_Relevant_Skills_num"] = Babysitter_Relevant_Skills_num

        # Calculate the number of times this babysitter has been favorited
        babysitter_data["Favorites_totalnum"] = sum(
            1 for favorite in dal.get_all(models.Favorite) if favorite.babysitterid == babysitter.id
        )

        # Calculate the total number of reviews received by the babysitter
        babysitter_data["Babysitter_Total_Reviews_got"] = sum(
            1 for review in dal.get_all(models.Review) if review.reviewedid == babysitter.id
        )

        # Append the babysitter data to the list
        data_for_prediction.append(babysitter_data)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_for_prediction)

    # Here, we can include any preprocessing steps that were applied to the training data,
    # such as filling missing values, feature scaling, or encoding categorical variables if necessary.

    return df


def get_recommendations_for_parent(parentid):

    input_df = create_input_data_for_parent(parentid)

    # Since 'Babysitterid' was used for illustrative purposes, ensure it's in the DataFrame
    # to identify babysitters after predictions. Do not use it as a feature for prediction.
    babysitter_ids = input_df["Babysitterid"]
    input_df.to_csv("input_df.csv")
    # Drop 'Babysitterid' if it's not a feature used in your model training
    X = input_df.drop(["Babysitterid"], axis=1)

    # Predict the likelihood of contact
    probabilities = nb_model.predict_proba(X)
    if probabilities.shape[1] == 2:
        predicted_likelihood = probabilities[:, 1]
    else:
        predicted_likelihood = 0

    # Create a DataFrame with babysitter IDs and their corresponding likelihoods
    recommendations = pd.DataFrame({"Babysitterid": babysitter_ids, "Likelihood": predicted_likelihood})

    # Sort the babysitters by likelihood of being contacted
    recommendations_sorted = recommendations.sort_values(by="Likelihood", ascending=False)

    return recommendations_sorted
