import crud

# need to import ↓↓
import pandas as pd
from database import SessionLocal, engine
from models import (
    BabysitterSkill,
    ChildrensNeeds,
    Contacted,
    NeedSkill,
    SpecialNeed,
    SpecialSkill,
)
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sqlalchemy.orm import sessionmaker

db = SessionLocal()


Session = sessionmaker(bind=engine)
session = Session()
all_skills = crud.get_specialskills(session)
all_needs = crud.get_specialneeds(session)
Babysitters_skills = []
for skill in all_skills:
    Babysitters_skills.append(crud.get_babysitters_with_skill(session, skill.skillid))
query = (
    session.query(BabysitterSkill, ChildrensNeeds, SpecialSkill, SpecialNeed)
    .join(SpecialSkill, BabysitterSkill.skillid == SpecialSkill.skillid)
    .join(NeedSkill, SpecialSkill.skillid == NeedSkill.skillid)
    .join(SpecialNeed, NeedSkill.needid == SpecialNeed.needid)
    .join(ChildrensNeeds, SpecialNeed.needid == ChildrensNeeds.needid)
)

results = []
for babysitter_skill, children_need, special_skill, special_need in query.all():
    results.append({"babysitter_skill": special_skill.skillname, "child_need": special_need.needname})
    print(f"Babysitter Skill: {special_skill.skillname}, Child Need: {special_need.needname}")


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
    df[f"skill_{skill}"] = df["babysitter_skill"].apply(lambda x: 1 if x == skill else 0)

for need in all_needs:
    df[f"need_{need}"] = df["child_need"].apply(lambda x: 1 if x == need else 0)

contacted_records = session.query(Contacted).all()
# הנחה שלכל רשומה יש מאפיינים parentid ו babysitterid
contacted_pairs = {(record.parentid, record.babysitterid) for record in contacted_records}
# נניח שיש לנו עמודות parentid ו babysitterid ב-DataFrame שלנו
df["contacted"] = df.apply(lambda row: 1 if (row["parentid"], row["babysitterid"]) in contacted_pairs else 0, axis=1)


# מכאן מתחילים להשתמש בספריית scikit-learn
# הגדרת התכונות והתגית
# נניח שהתכונות הן כל העמודות פרט ל-'contacted', והתגית היא 'contacted'
X = df.drop(["contacted"], axis=1)  # יצירת סט התכונות על ידי הסרת עמודת התגית
y = df["contacted"]  # יצירת סט התגיות

# חלוקה לסטי אימון ובדיקה
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# מכאן נוכל להמשיך ולאמן את המודל שלנו על סט האימון
# ולהעריך את ביצועיו על סט הבדיקה


# יצירת המודל
model = GaussianNB()

# אימון המודל
model.fit(X_train, y_train)

# חיזוי על סט הבדיקה
y_pred = model.predict(X_test)

# הערכת המודל
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")


# ###############################################################!
# יצירת DataFrame חדש שמכיל את התחזיות והערכים האמיתיים
# """
# predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})

# # הוספת אינדקס מחדש לקלות השוואה
# predictions_df.reset_index(drop=True, inplace=True)

# # הצגת ה-DataFrame
# print(predictions_df)"""
# ###############################################################!
