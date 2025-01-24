class zadachki():
    def__init__(self, number):
        self.number = number
    def write(self):
        if self.number == 0:
            return '''import pandas as pd
import numpy as np

import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Загрузка данных
data = pd.read_csv("/content/bank.csv")

# Определяем признаки и целевую переменную
X = data.drop("deposit", axis=1)
y = data["deposit"]

# Определяем категориальные и числовые столбцы
categorical_cols = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']
numerical_cols = ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']

# Предобработка данных
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(), categorical_cols)
    ]
)

X_processed = preprocessor.fit_transform(X)
y = (y == 'yes').astype(int)  # Преобразуем целевую переменную в бинарный формат (0 и 1)

# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

# Преобразование данных в тензоры
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.float32)

train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)

# Определение модели
class Model(nn.Module):
    def __init__(self, input_dim):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)  # Один выходной нейрон для бинарной классификации
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return self.sigmoid(x)

# Гиперпараметры
batch_size = 64
epochs = 20

# Функция обучения модели
def train_model(model, optimizer, criterion, train_loader):
    loss_history = []
    for epoch in range(epochs):
        epoch_loss = 0
        model.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X).squeeze()
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        loss_history.append(epoch_loss / len(train_loader))
    return loss_history

# Сравнение оптимизаторов
optimizers = {
    "Adam": optim.Adam,
    "SGD": optim.SGD,
    "RMSprop": optim.RMSprop
}

loss_histories = {}

for name, optimizer_class in optimizers.items():
    print(f"\n--- Training with {name} optimizer ---")
    model = Model(X_train.shape[1])
    optimizer = optimizer_class(model.parameters(), lr=0.01)
    criterion = nn.BCELoss()
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    loss_history = train_model(model, optimizer, criterion, train_loader)
    loss_histories[name] = loss_history

    # Оценка на тестовом множестве
    model.eval()
    with torch.no_grad():
        y_pred = model(X_test).squeeze()
        y_pred_classes = (y_pred >= 0.5).int()

    # Матрица ошибок и отчет классификации
    print(f"Confusion Matrix for {name}:")
    conf_matrix = confusion_matrix(y_test, y_pred_classes)
    print(conf_matrix)

    print(f"\nClassification Report for {name}:\n")
    print(classification_report(y_test, y_pred_classes))

    # Отображение матрицы ошибок
    disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=['no', 'yes'])
    disp.plot(cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix ({name})")
    plt.show()

# Построение графика сравнения функции потерь
plt.figure(figsize=(10, 6))
for name, loss_history in loss_histories.items():
    plt.plot(range(1, epochs + 1), loss_history, label=name)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss Comparison of Optimizers')
plt.legend()
plt.grid()
plt.show()'''
    # Добавьте другие варианты