# need to import ↓↓
import pandas as pd
from database import engine
from models import (  # Parent,
    Babysitter,
    BabysitterSkill,
    Children,
    ChildrensNeeds,
    Contacted,
    NeedSkill,
    ParentsChildrens,
    SpecialNeed,
    SpecialSkill,
)
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Assuming you have relationships set up in your SQLAlchemy models that allow you to traverse
# from skills to babysitters and from needs to parents (or children to parents)
query = (
    session.query(
        BabysitterSkill.babysitterid,
        ChildrensNeeds.childid,
        SpecialSkill.skillname,
        SpecialNeed.needname,
        ParentsChildrens.parentid,
    )
    .join(Babysitter, BabysitterSkill.babysitterid == Babysitter.babysitterid)
    .join(SpecialSkill, BabysitterSkill.skillid == SpecialSkill.skillid)
    .join(NeedSkill, SpecialSkill.skillid == NeedSkill.skillid)
    .join(SpecialNeed, NeedSkill.needid == SpecialNeed.needid)
    .join(ChildrensNeeds, SpecialNeed.needid == ChildrensNeeds.needid)
    .join(Children, ChildrensNeeds.childid == Children.childid)
    .join(ParentsChildrens, Children.childid == ParentsChildrens.childid)
)

results = []
for babysitter_id, child_id, skill_name, need_name, parent_id in query.all():
    results.append(
        {
            "babysitter_id": babysitter_id,
            "parent_id": parent_id,
            "skill_name": skill_name,
            "need_name": need_name,
        }
    )


print(results)


# איסוף כל הכישורים והצרכים מהדאטה בייס
all_skills = session.query(SpecialSkill.skillname).distinct().all()
all_needs = session.query(SpecialNeed.needname).distinct().all()

# המרה לרשימות
all_skills = [skill[0] for skill in all_skills]
all_needs = [need[0] for need in all_needs]

# המרת התוצאות ל-DataFrame
df = pd.DataFrame(results)

# יצירת תכונות בינאריות
for skill in all_skills:
    df[f"skill_{skill}"] = df["skill_name"].apply(lambda x: 1 if x == skill else 0)

for need in all_needs:
    df[f"need_{need}"] = df["need_name"].apply(lambda x: 1 if x == need else 0)

contacted_records = session.query(Contacted).all()
# הנחה שלכל רשומה יש מאפיינים parentid ו babysitterid
contacted_pairs = {(record.parentid, record.babysitterid) for record in contacted_records}
# נניח שיש לנו עמודות parentid ו babysitterid ב-DataFrame שלנו
df["contacted"] = df.apply(
    lambda row: 1 if (row["parent_id"], row["babysitter_id"]) in contacted_pairs else 0,
    axis=1,
)

# Assuming 'df' is your DataFrame after fetching the results
# Convert 'skill_name' and 'need_name' to a one-hot encoded format
df_skills_needs = pd.get_dummies(df[["skill_name", "need_name"]])

# Include the 'babysitter_id' and 'parent_id' in the DataFrame if you plan to use them as features
# Otherwise, ensure they are not included in the features DataFrame if they are only identifiers
df_final = pd.concat([df_skills_needs, df["contacted"]], axis=1)

# Now 'df_final' is ready for machine learning models

# Splitting the data for training and testing
X = df_final.drop("contacted", axis=1)  # Features
y = df_final["contacted"]  # Target variable

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=16)

# Training the model
model = GaussianNB()
model.fit(X_train, y_train)

# Making predictions
y_pred = model.predict(X_test)

# Evaluating the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")


# יצירת DataFrame חדש שמכיל את התחזיות והערכים האמיתיים
predictions_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})

# הוספת אינדקס מחדש לקלות השוואה
predictions_df.reset_index(drop=True, inplace=True)

# הצגת ה-DataFrame
print(predictions_df)
