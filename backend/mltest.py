import logging

# import crud
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# from database import SessionLocal
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

from backend.database import models
from backend.database.dal import DataAccessLayer

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start a session
# db = SessionLocal()
dal = DataAccessLayer()
# Fetch data (simplified examples, replace with actual data fetching and processing)
babysitters = dal.get_all(model=models.Babysitter, skip=0, limit=1000)
parents = dal.get_all(model=models.Parent, skip=0, limit=1000)
contacted_records = dal.get_all(model=models.Contacted, skip=0, limit=1000)

# Assuming you have functions or logic to extract skills as binary features
# and have a way to match these features to corresponding parents based on needs

# Placeholder for the feature matrix and target vector
features = []
target = []

# Simplified loop to construct features and target based on your needs
features = []
target = []

for parent in parents:
    # Collect all unique needs from the parent's children
    unique_needs = set()
    for child in parent.childrens:
        for need in child.needs_association:
            unique_needs.add(need.need.needname)

    for babysitter in babysitters:
        # Convert babysitter's skills to a set for easier comparison
        babysitter_skill_set = set([skill.skill.skillname for skill in babysitter.skills])

        # Construct the feature vector: 1 if the babysitter has a skill that matches a child's need, 0 otherwise
        features_vector = [1 if skill in babysitter_skill_set else 0 for skill in unique_needs]

        # Determine if this babysitter was contacted by this parent
        was_contacted = any(
            contact.parentid == parent.id and contact.babysitterid == babysitter.id for contact in contacted_records
        )

        # Append the constructed feature vector and contact status to the lists
        features.append(features_vector)
        target.append(1 if was_contacted else 0)

# Convert lists to DataFrame and Series for use in model

X = pd.DataFrame(features)
X.fillna(0, inplace=True)
y = pd.Series(target)

print(X)
print(y)
print(X.head())
print(y.head())
# Scale the feature matrix
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
# make plt here to visuliaze the current data
# Visualize the number of contacted records


# Splitting the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=16)

# Initializing and training the Gaussian Naive Bayes model
model = GaussianNB()
model.fit(X_train, y_train)

# Making predictions
y_pred = model.predict(X_test)

# Evaluating the model
accuracy = accuracy_score(y_test, y_pred)
logger.info(f"Model Accuracy: {accuracy}")

# Assuming the first plot of the distribution of each skill across all babysitters
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(
    data=X.melt(var_name="Skills", value_name="Presence"),
    x="Skills",
    hue="Presence",
    ax=ax,
)
plt.xticks(rotation=45, ha="right")
plt.title("Distribution of Skills Presence across Babysitters")
plt.tight_layout()

# Plot the distribution of contacted status
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(x=y, ax=ax)
plt.title("Distribution of Contacted Status")
plt.xticks([0, 1], ["Not Contacted", "Contacted"])

plt.show()


plt.figure(figsize=(12, 10))
sns.heatmap(X.corr(), annot=True, fmt=".2f")
plt.title("Feature Correlation Matrix")
plt.show()
