import crud
import pandas as pd
from database import SessionLocal
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB


def recommend_babysitters_for_parent(parent_id):
    db = SessionLocal()

    # Fetch skills, needs, and babysitters
    # skills = crud.get_specialskills(db)
    babysitters = crud.get_babysitters(db)
    # children_needs = crud.get_childrens_needs_by_parent_id(db, parent_id)
    contacted_records = crud.get_all_contacted(db)
    parents_childrens = crud.get_parents(db)
    children_needs = crud.get_specialneeds(db)

    results = []
    contacted_labels = []
    for babysitter in babysitters:
        for skill in babysitter.skills:
            for need in children_needs:
                for need_skill in need.need_skills:
                    if need_skill.skillid == skill.skillid:
                        for parent_child in parents_childrens:
                            for children in parent_child.children:
                                for childneed in children.needs_association:
                                    if childneed.needid == need_skill.needid:
                                        results.append(
                                            {
                                                "babysitter_id": skill.babysitterid,
                                                "parent_id": parent_child.parentid,
                                                "skill_name": skill.skill.skillname,
                                                "need_name": need.needname,
                                            }
                                        )
        contacted_labels.append(1 if babysitter.babysitterid in [c.babysitterid for c in contacted_records] else 0)

    # Convert results to DataFrame
    df = pd.DataFrame(results)
    if df.empty:
        return []
    print(df)
    # Apply one-hot encoding
    df_skills_needs = pd.get_dummies(df[["skill_name", "need_name"]])
    df_final = pd.concat([df_skills_needs, df["babysitter_id"]], axis=1)
    print(df_final)
    # Prepare features matrix X and labels y
    X = df_final.drop("babysitter_id", axis=1)
    y = pd.Series(contacted_labels)

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the Naive Bayes model
    model = GaussianNB()
    model.fit(X_train, y_train)

    # Predict probabilities for the test set
    y_pred_prob = model.predict_proba(X_test)[:, 1]

    # Evaluate the model using accuracy
    accuracy = accuracy_score(y_test, y_pred_prob > 0.5)  # Threshold probability to get binary outcomes
    print(f"Accuracy: {accuracy}")

    # For new predictions, use the model to predict probabilities
    # Sort babysitters based on the predicted probabilities
    babysitters_prob = pd.Series(y_pred_prob, index=X_test.index)
    recommended_babysitters = babysitters_prob.sort_values(ascending=False).head(3).index.tolist()

    return recommended_babysitters


# Example usage
parent_id = 1
recommended_babysitters = recommend_babysitters_for_parent(parent_id)
print(f"Recommended babysitters for parent {parent_id}: {recommended_babysitters}")
