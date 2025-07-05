import pickle
from sklearn.linear_model import LinearRegression

# Example training data
X = [[75, 85], [80, 90], [60, 70], [90, 95]]  # [attendance, internal_marks]
y = [78, 88, 65, 92]  # Final marks

model = LinearRegression()
model.fit(X, y)

# Save the model
with open('src/models/student_model.pkl', 'wb') as f:
    pickle.dump(model, f)
