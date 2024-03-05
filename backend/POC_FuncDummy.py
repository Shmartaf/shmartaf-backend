import crud
import pandas as pd
from database import SessionLocal

# from sklearn.metrics import accuracy_score

# from sklearn.model_selection import train_test_split

# from sklearn.naive_bayes import GaussianNB


def recommend_babysitters_for_parent(parent_id):
    db = SessionLocal()

    # Fetch skills, needs, and babysitters
    # skills = crud.get_specialskills(db)
    babysitters = crud.get_babysitters(db)
    children_needs = crud.get_childrens_needs_by_parent_id(db, parent_id)
    # contacted_records = crud.get_contacted_by_parent_id(db, parent_id)

    results = []
    for babysitter in babysitters:
        for skill in babysitter.skills:
            for need in children_needs:
                for ns in need.need.need_skills:
                    if skill.skillid == ns.skillid:
                        results.append(
                            {
                                "babysitter_id": babysitter.babysitterid,
                                "skill_name": skill.skill.skillname,
                                "need_name": need.need.needname,
                            }
                        )

    # Convert results to DataFrame
    df = pd.DataFrame(results)
    if df.empty:
        return []
    print(df)
    # Apply one-hot encoding
    # df_skills_needs = pd.get_dummies(df[["skill_name", "need_name"]])
    # df_final = pd.concat([df_skills_needs, df["babysitter_id"]], axis=1)

    # Prepare features matrix X
    # X = df_final.drop("babysitter_id", axis=1)

    # Use a model to predict (dummy example, as prediction requires labels and a trained model)
    # For demonstration, randomly select babysitters as recommendation
    recommended_babysitters = df["babysitter_id"].sample(n=min(3, len(df))).tolist()

    return recommended_babysitters


# Example usage
parent_id = 7
recommended_babysitters = recommend_babysitters_for_parent(parent_id)
print(f"Recommended babysitters for parent {parent_id}: {recommended_babysitters}")
