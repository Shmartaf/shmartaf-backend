import crud
import pandas as pd
from database import SessionLocal
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

db = SessionLocal()
parents = crud.get_parents(db)
parent_children = crud.get_all_parents_childrens(db)
babysitters = crud.get_babysitters(db)
contacted = crud.get_all_contacted(db)

allskils = crud.get_specialskills(db)
allneeds = crud.get_specialneeds(db)
need_names = [need.needname for need in allneeds]
skill_names = [skill.skillname for skill in allskils]


# DataFrame for babysitters' skills

babysitters_skills_df = pd.DataFrame(columns=skill_names, index=[babysitter.babysitterid for babysitter in babysitters])
for babysitter in babysitters:
    for babysitter_skill in babysitter.skills:
        babysitters_skills_df.at[babysitter.babysitterid, babysitter_skill.skill.skillname] = 1
    babysitters_skills_df = babysitters_skills_df.fillna(0)
print(babysitters_skills_df)

# DataFrame for parents' childrens' needs
parent_needs_df = pd.DataFrame(columns=skill_names, index=need_names)
for skill in allskils:
    for skill_need in skill.skill_needs:
        if skill_need.need.needname in parent_needs_df.index:
            parent_needs_df.at[skill_need.need.needname, skill.skillname] = 1
parent_needs_df = parent_needs_df.fillna(0)
print(parent_needs_df)

# DataFrame for contacted
contacted_df = pd.DataFrame(
    columns=skill_names, index=[(contacted.parentid, contacted.babysitterid) for contacted in contacted]
)
for contact in contacted:
    for babysitter_skill in contact.babysitter.skills:
        contacted_df.at[(contact.parentid, contact.babysitterid), babysitter_skill.skill.skillname] = 1
    contacted_df = contacted_df.fillna(0)
print(contacted_df)


df = pd.DataFrame(columns=skill_names, index=need_names)

for skill in allskils:
    for skill_need in skill.skill_needs:
        if skill_need.need.needname in df.index:
            df.at[skill_need.need.needname, skill.skillname] = 1
df = df.fillna(0)
print(df)

babysitters_skills_df = pd.DataFrame(columns=skill_names, index=[babysitter.babysitterid for babysitter in babysitters])
for babysitter in babysitters:
    for babysitter_skill in babysitter.skills:
        babysitters_skills_df.at[babysitter.babysitterid, babysitter_skill.skill.skillname] = 1
    babysitters_skills_df = babysitters_skills_df.fillna(0)
print(babysitters_skills_df)

contacted_df = pd.DataFrame(
    columns=skill_names, index=[(contacted.parentid, contacted.babysitterid) for contacted in contacted]
)
for contact in contacted:
    for babysitter_skill in contact.babysitter.skills:
        contacted_df.at[(contact.parentid, contact.babysitterid), babysitter_skill.skill.skillname] = 1
    contacted_df = contacted_df.fillna(0)
print(contacted_df)

# Prepare the features matrix (X) and the target vector (y)

X = babysitters_skills_df
y = pd.Series(index=X.index)

for idx in X.index:
    y[idx] = 1 if idx in contacted_df.index else 0

y = y.fillna(0)

# Split the data into a training set and a test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = GaussianNB()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")


# df = pd.DataFrame(columns=skill_names, index=need_names)
# #

# for skill in allskils:
#     for skill_need in skill.skill_needs:
#         if skill_need.need.needname in df.index:
#             df.at[skill_need.need.needname, skill.skillname] = 1
# df = df.fillna(0)
# print(df)

# babysitters_skills_df = pd.DataFrame(columns=skill_names, index=[babysitter.babysitterid for babysitter in babysitters])
# for babysitter in babysitters:
#     for babysitter_skill in babysitter.skills:
#         babysitters_skills_df.at[babysitter.babysitterid, babysitter_skill.skill.skillname] = 1
#     babysitters_skills_df = babysitters_skills_df.fillna(0)
# print(babysitters_skills_df)

# for contact in contacted:
#     for babysitter_skill in contact.babysitter.skills:
#         contacted_df.at[(contact.parentid, contact.babysitterid), babysitter_skill.skill.skillname] = 1
#     contacted_df = contacted_df.fillna(0)
# print(contacted_df)


# pass
