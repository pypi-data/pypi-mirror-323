"""
:authors: KingsFrown
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2025 KingsFrown
"""

from pyperclip import copy

def I():
    copy('''
b() - библиотеки
r(n) - регрессия
c(n) - классификация
i(n) - картинки
1. Загрузка и предобработка
2. Модель
3. Обучение
4. Метрики
5. График
''')
    
def b():
    copy('''
import pandas as pd
import numpy as np

import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader, TensorDataset

from torchvision import transforms
from torchvision.datasets import ImageFolder

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

import matplotlib.pyplot as plt         
''')
    
def r(n):
    if n==1:
        copy('''
df = pd.read_csv('bike_cnt.csv')
df.drop(['instant', 'dteday', 'hr'], axis=1, inplace=True)
X = df.drop(['cnt'], axis=1)
y = df['cnt']
categorical_cols = ['season','yr','mnth','holiday','weekday','workingday','weathersit']
numerical_cols = ['temp','atemp','hum','windspeed']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(), categorical_cols)
    ])

X_processed = preprocessor.fit_transform(X).toarray()

X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train.values, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.float32)

train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)

#################################################

df = pd.read_csv('gold.csv')
y_col = 'название колонки Y'
X = df.drop([y_col], axis=1)
y = df[y_col]
numerical_cols = list(df.columns)
numerical_cols.remove(y_col)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols)
    ])

X_processed = preprocessor.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train.values, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.float32)

train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)
''')
    elif n==2:
        copy('''
hidden_dim = 32
model = nn.Sequential(nn.Linear(X_train.shape[1],hidden_dim),
                      nn.BatchNorm1d(hidden_dim),
                      nn.ReLU(),
                      nn.Dropout(0.5),
                      nn.Linear(hidden_dim,hidden_dim),
                      nn.BatchNorm1d(hidden_dim),
                      nn.ReLU(),
                      nn.Dropout(0.5),
                      nn.Linear(hidden_dim,1)
                     )

batch_size = 64
epochs = 100
print_every = 10

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
''')
    elif n==3:
        copy('''
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

train_losses = []
val_losses = []

for epoch in range(epochs):
    model.train()
    train_loss = 0
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs.squeeze(), batch_y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    train_losses.append(train_loss / len(train_loader))

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            outputs = model(batch_X)
            loss = criterion(outputs.squeeze(), batch_y)
            val_loss += loss.item()

    val_losses.append(val_loss / len(test_loader))

    if (epoch+1) % print_every == 0:
        print(f'Epoch {epoch+1}/{epochs}, Train Loss: {train_losses[-1]:.4f}, Val Loss: {val_losses[-1]:.4f}')
''')
    elif n==4:
        copy('''
# через sklearn
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
model.eval()
predictions = []
actuals = []
with torch.no_grad():
    for batch_X, batch_y in test_loader:
        outputs = model(batch_X)
        predictions.extend(outputs.squeeze().numpy())
        actuals.extend(batch_y.numpy())

mse = mean_squared_error(actuals, predictions)
mae = mean_absolute_error(actuals, predictions)
r2 = r2_score(actuals, predictions)

# через torchmetrics
# import torchmetrics
# model.eval()
# mse_metric = torchmetrics.MeanSquaredError()
# mae_metric = torchmetrics.MeanAbsoluteError()
# r2_metric = torchmetrics.R2Score()

# with torch.no_grad():
#     for batch_X, batch_y in test_loader:
#         outputs = model(batch_X)
#         mse_metric.update(outputs.squeeze(), batch_y)
#         mae_metric.update(outputs.squeeze(), batch_y)
#         r2_metric.update(outputs.squeeze(), batch_y)

# mse = mse_metric.compute().item()
# mae = mae_metric.compute().item()
# r2 = r2_metric.compute().item()
''')
    elif n==5:
        copy('''
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
print(f'MSE: {mse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}')
''')
        
def c(n):
    if n==1:
        copy('''
df = pd.read_csv('bank.csv')
X = df.drop(['deposit'], axis=1)
y = np.array(df.deposit=='yes',dtype=np.float32)
categorical_cols = ['job','marital','education','default','housing','loan','contact','poutcome','month']
numerical_cols = ['age','balance' , 'day','duration','campaign','pdays','previous']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(), categorical_cols)
    ])

X_processed = preprocessor.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32)

train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)
''')
    elif n==2:
        copy('''
from sklearn.utils.class_weight import compute_class_weight

hidden_dim = 32
model = nn.Sequential(nn.Linear(X_train.shape[1],hidden_dim),
                      nn.BatchNorm1d(hidden_dim),
                      nn.ReLU(),
                      nn.Dropout(0.5),
                      nn.Linear(hidden_dim,hidden_dim),
                      nn.BatchNorm1d(hidden_dim),
                      nn.ReLU(),
                      nn.Dropout(0.5),
                      nn.Linear(hidden_dim,2)
                     )

batch_size = 64
epochs = 100
print_every = 10

classes = np.array([0, 1])  
class_weights = compute_class_weight(class_weight='balanced', classes=classes, y=y)
weights = []
for i, weight in enumerate(class_weights):
    weights.append(weight)
weight = torch.tensor(class_weights,dtype=torch.float32)

criterion = nn.CrossEntropyLoss(weight=weight)
optimizer = optim.Adam(model.parameters(),lr = 0.01)
''')
    elif n==3:
        copy('''
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

train_losses = []
val_losses = []

for epoch in range(epochs):
    model.train()
    train_loss = 0
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y.long())
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    train_losses.append(train_loss / len(train_loader))

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y.long())
            val_loss += loss.item()

    val_losses.append(val_loss / len(test_loader))

    if (epoch+1) % print_every == 0:
        print(f'Epoch {epoch+1}/{epochs}, Train Loss: {train_losses[-1]:.4f}, Val Loss: {val_losses[-1]:.4f}') 
''')
    elif n==4:
        copy('''
# через sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
model.eval()
predictions = []
actuals = []
with torch.no_grad():
    for batch_X, batch_y in test_loader:
        outputs = torch.argmax(model(batch_X),dim=1)
        predictions.extend(outputs.numpy())
        actuals.extend(batch_y.numpy())

accuracy = accuracy_score(actuals, predictions)
precision = precision_score(actuals, predictions)
recall = recall_score(actuals, predictions)
f1 = f1_score(actuals, predictions)
print(classification_report(actuals, predictions))

# через torchmetrics
# import torchmetrics
# model.eval()
# accuracy_metric = torchmetrics.Accuracy(task="binary")
# precision_metric = torchmetrics.Precision(task="binary")
# recall_metric = torchmetrics.Recall(task="binary")
# f1_metric = torchmetrics.F1Score(task="binary")
# with torch.no_grad():
#     for batch_X, batch_y in test_loader:
#         outputs = torch.argmax(model(batch_X),dim=1)
#         accuracy_metric.update(outputs, batch_y.long())
#         precision_metric.update(outputs, batch_y.long())
#         recall_metric.update(outputs, batch_y.long())
#         f1_metric.update(outputs, batch_y.long())

# accuracy = accuracy_metric.compute().item()
# precision = precision_metric.compute().item()
# recall = recall_metric.compute().item()
# f1 = f1_metric.compute().item()
''')
    elif n==5:
        copy('''
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
print(f'Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}')
''')
        
def i(n):
    if n==1:
        copy('''
import copy
data_dir = "eng_handwritten"

train_transform = transforms.Compose([
    transforms.Resize((64,64)),
#     transforms.RandomHorizontalFlip(),
#     transforms.RandomVerticalFlip(),
#     transforms.RandomRotation(degrees=15),
#     transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
    transforms.ToTensor()
])

test_transform = transforms.Compose([
    transforms.Resize((64,64)),
    transforms.ToTensor()
])

full_dataset = ImageFolder(data_dir, transform=test_transform)
n_classes = len(full_dataset.classes)
train_ds, test_dataset = torch.utils.data.random_split(full_dataset, [0.8, 0.2])
train_dataset = copy.deepcopy(train_ds)
train_dataset.transform = train_transform
''')
    elif n==2:
        copy('''
model = nn.Sequential(
    nn.Conv2d(3,16,3),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(16,32,3),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32,64,3),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.LazyLinear(128),
    nn.ReLU(),
    nn.Linear(128,n_classes)
)

batch_size = 64
epochs = 5
print_every = 1

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr = 0.01)
''')
    elif n==3:
        copy('''
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

train_losses = []
val_losses = []

for epoch in range(epochs):
    model.train()
    train_loss = 0
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y.long())
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    train_losses.append(train_loss / len(train_loader))

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y.long())
            val_loss += loss.item()

    val_losses.append(val_loss / len(test_loader))

    if (epoch+1) % print_every == 0:
        print(f'Epoch {epoch+1}/{epochs}, Train Loss: {train_losses[-1]:.4f}, Val Loss: {val_losses[-1]:.4f}')
''')
    elif n==4:
        copy('''
# через sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
model.eval()
predictions = []
actuals = []
with torch.no_grad():
    for batch_X, batch_y in test_loader:
        outputs = torch.argmax(model(batch_X), dim=1)
        predictions.extend(outputs.numpy())
        actuals.extend(batch_y.numpy())

accuracy = accuracy_score(actuals, predictions)
precision = precision_score(actuals, predictions, average='weighted')
recall = recall_score(actuals, predictions, average='weighted')
f1 = f1_score(actuals, predictions, average='weighted')
print(classification_report(actuals, predictions))

# через torchmetrics
# import torchmetrics
# model.eval()
# accuracy_metric = torchmetrics.Accuracy(task="multiclass", num_classes=n_classes)
# precision_metric = torchmetrics.Precision(task="multiclass", num_classes=n_classes, average='weighted')
# recall_metric = torchmetrics.Recall(task="multiclass", num_classes=n_classes, average='weighted')
# f1_metric = torchmetrics.F1Score(task="multiclass", num_classes=n_classes, average='weighted')

# with torch.no_grad():
#     for batch_X, batch_y in test_loader:
#         outputs = torch.argmax(model(batch_X), dim=1)
#         accuracy_metric.update(outputs, batch_y.long())
#         precision_metric.update(outputs, batch_y.long())
#         recall_metric.update(outputs, batch_y.long())
#         f1_metric.update(outputs, batch_y.long())

# accuracy = accuracy_metric.compute().item()
# precision = precision_metric.compute().item()
# recall = recall_metric.compute().item()
# f1 = f1_metric.compute().item()
''')
    elif n==5:
        copy('''
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
print(f'Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}')
''')