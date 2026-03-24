from sklearn.ensemble import RandomForestClassifier
import json

X = []
y = []

with open("data/real_vaults.json") as f:
    real = json.load(f)

with open("generated_fake.json") as f:
    fake = json.load(f)

for v in real:
    X.append([len(v["password"])])
    y.append(1)

for v in fake:
    X.append([len(v["password"])])
    y.append(0)

clf = RandomForestClassifier()
clf.fit(X,y)
print("Accuracy:", clf.score(X,y))
