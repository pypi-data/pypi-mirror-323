def bank_dropout():
    """
    Haбор дaных; classifiention/bannk.csv. Используя библиотеку Рytorch, решите задачу классификании (столбец deposit). Разделите набор данных на обучаюшее и тестовое можесто. Выполиите предобработку данных (корректно обработайте случаи категорнальных и нечисловых столбиов, при наличии). Отобразите график значений функции потерь на обучющем миожестве по эпохам. Отобразите confusion matrix и classilication report, рассчитанные на основе тестового множества. Добавьте в модель слои drоpout и графически продемонстрируйте, как это влияет на процесс обучения и результаты на тестовом множестве. (20 баллон)
    """
    import pandas as pd
    import numpy as np

    import torch
    from torch import nn, optim
    from torch.utils.data import Dataset, DataLoader, TensorDataset

    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
    from sklearn.compose import ColumnTransformer

    import matplotlib.pyplot as plt

    data = pd.read_csv('bank.csv')

    data = pd.read_csv("bank.csv")

    X = data.drop('deposit', axis=1)
    y = data['deposit']

    categorical_cols = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
    numerical_cols = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(), categorical_cols)
        ])

    X_processed = preprocessor.fit_transform(X)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    # без dropout 
    class Model(nn.Module):
        def __init__(self, input_size, dropout_rate=0):
            super(Model, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)
            self.fc2 = nn.Linear(128, 64)
            self.fc3 = nn.Linear(64, 2)
            # self.dropout = nn.Dropout(dropout_rate)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = self.fc1(x)
            x = self.relu(x)
            # x = self.dropout(x)
            x = self.fc2(x)
            x = self.relu(x)
            # x = self.dropout(x)
            x = self.fc3(x)
            return x
    
    # с dropout
    class Model_d(nn.Module):
        def __init__(self, input_size, dropout_rate=0.5):
            super(Model_d, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)
            self.fc2 = nn.Linear(128, 64)
            self.fc3 = nn.Linear(64, 2)
            self.dropout = nn.Dropout(dropout_rate)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = self.fc1(x)
            x = self.relu(x)
            x = self.dropout(x)
            x = self.fc2(x)
            x = self.relu(x)
            x = self.dropout(x)
            x = self.fc3(x)
            return x

    # обучение модели без dropout
    batch_size = 64
    epochs = 10
    print_every = 10

    model = Model(X_train.size(1))
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses = []
    test_losses = []

    for epoch in range(epochs):
        epoch_loss = 0
        model.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y.long())
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model.eval()
        with torch.no_grad():
            test_outputs = model(X_test)
            test_loss = criterion(test_outputs, y_test.long())

        train_losses.append(epoch_loss/batch_size)
        test_losses.append(test_loss.item())

        print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

    # обучение модели с dropout
    batch_size = 64
    epochs = 10
    print_every = 10


    model_d = Model_d(X_train.size(1), dropout_rate = 0.5)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model_d.parameters(), lr = 0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_d = []
    test_losses_d = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_d.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_d(batch_X)
            loss = criterion(outputs, batch_y.long())
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_d.eval()
        with torch.no_grad():
            test_outputs = model_d(X_test)
            test_loss = criterion(test_outputs, y_test.long())

        train_losses_d.append(epoch_loss/batch_size)
        test_losses_d.append(test_loss.item())

        print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

    # сравнение графиков
    plt.plot(range(1, epochs + 1), train_losses, label="Training Loss без dropout")
    plt.plot(range(1, epochs + 1), test_losses, label="Test Loss без dropout")
    plt.plot(range(1, epochs + 1), train_losses_d, label="Training Loss с dropout")
    plt.plot(range(1, epochs + 1), test_losses_d, label="Test Loss с dropout")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Training and Test Loss over Epochs")
    plt.legend()
    plt.show()

    # confusion matrix и classification report без dropout
    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    model.eval()
    with torch.no_grad():
        y_pred = model(X_test)
        y_pred_classes = torch.argmax(y_pred, axis=1)

    cm = confusion_matrix(y_test, y_pred_classes)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix без dropout")
    plt.show()

    print("Classification Report:")
    print(classification_report(y_test, y_pred_classes))

    # confusion matrix и classification report с dropout

    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    model_d.eval()
    with torch.no_grad():
        y_pred = model_d(X_test)
        y_pred_classes = torch.argmax(y_pred, axis=1)

    cm = confusion_matrix(y_test, y_pred_classes)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix с dropout")
    plt.show()

    print("Classification Report:")
    print(classification_report(y_test, y_pred_classes))

def bank_optimizers():
    """
    2. Набор данных: classificationbank.csv. Используя библиотеку PуГorch, решите задачу классификации (столбец deposit). Разделите набор данных на обучающее и тестовоет множество. Выполните предобработку данных (корректно обработайте случаи категориальных и нечисловых столбцов, при наличии). Отобразите график значений функции потерь на обучающем множестве по эпохам. Отобразите confusion matrix h classification report, рассчитанные на основе тестового множества. Сравните несколько различных оптимизаторов и графически продемонстрируйте, как выбор оптимизатора влияет на процесс обучения и результаты на тестовом множестве. (20 баллов)
    """

    import pandas as pd
    import numpy as np

    import torch
    from torch import nn, optim
    from torch.utils.data import Dataset, DataLoader, TensorDataset

    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
    from sklearn.compose import ColumnTransformer

    import matplotlib.pyplot as plt

    data = pd.read_csv("bank.csv")

    X = data.drop('deposit', axis=1)
    y = data['deposit']

    categorical_cols = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
    numerical_cols = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(), categorical_cols)
        ])

    X_processed = preprocessor.fit_transform(X)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    class Model_d(nn.Module):
        def __init__(self, input_size, dropout_rate=0.5):
            super(Model_d, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)
            self.fc2 = nn.Linear(128, 64)
            self.fc3 = nn.Linear(64, 2)
            self.dropout = nn.Dropout(dropout_rate)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = self.fc1(x)
            x = self.relu(x)
            x = self.dropout(x)
            x = self.fc2(x)
            x = self.relu(x)
            x = self.dropout(x)
            x = self.fc3(x)
            return x
    
    # SGD
    batch_size = 64
    epochs = 10
    print_every = 10


    model_sgd = Model_d(X_train.size(1), dropout_rate = 0.5)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model_sgd.parameters(), lr = 0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_sgd = []
    test_losses_sgd = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_sgd.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_sgd(batch_X)
            loss = criterion(outputs, batch_y.long())
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_sgd.eval()
        with torch.no_grad():
            test_outputs = model_sgd(X_test)
            test_loss = criterion(test_outputs, y_test.long())

        train_losses_sgd.append(epoch_loss/batch_size)
        test_losses_sgd.append(test_loss.item())

        print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

    # RMSprop
    batch_size = 64
    epochs = 10
    print_every = 10


    model_rms = Model_d(X_train.size(1), dropout_rate = 0.5)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.RMSprop(model_rms.parameters(), lr = 0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_rms = []
    test_losses_rms = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_rms.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_rms(batch_X)
            loss = criterion(outputs, batch_y.long())
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_rms.eval()
        with torch.no_grad():
            test_outputs = model_rms(X_test)
            test_loss = criterion(test_outputs, y_test.long())

        train_losses_rms.append(epoch_loss/batch_size)
        test_losses_rms.append(test_loss.item())

        print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

    # Adam

    batch_size = 64
    epochs = 10
    print_every = 10


    model_adam = Model_d(X_train.size(1), dropout_rate = 0.5)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model_adam.parameters(), lr = 0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_adam = []
    test_losses_adam = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_adam.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_adam(batch_X)
            loss = criterion(outputs, batch_y.long())
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_adam.eval()
        with torch.no_grad():
            test_outputs = model_adam(X_test)
            test_loss = criterion(test_outputs, y_test.long())

        train_losses_adam.append(epoch_loss/batch_size)
        test_losses_adam.append(test_loss.item())

        print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

    # Сравнение графиков

    plt.plot(range(1, epochs + 1), train_losses_sgd, label="Training Loss SGD")
    plt.plot(range(1, epochs + 1), test_losses_sgd, label="Test Loss SGD")
    plt.plot(range(1, epochs + 1), train_losses_rms, label="Training Loss RMS")
    plt.plot(range(1, epochs + 1), test_losses_rms, label="Test Loss RMS")
    plt.plot(range(1, epochs + 1), train_losses_adam, label="Training Loss Adam")
    plt.plot(range(1, epochs + 1), test_losses_adam, label="Test Loss Adam")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Training and Test Loss over Epochs")
    plt.legend()
    plt.show()

    # Confusion matrix и classification report SGD
    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    model_sgd.eval()
    with torch.no_grad():
        y_pred = model_sgd(X_test)
        y_pred_classes = torch.argmax(y_pred, axis=1)

    cm = confusion_matrix(y_test, y_pred_classes)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix SGD")
    plt.show()

    print("Classification Report:")
    print(classification_report(y_test, y_pred_classes))

    # Confusion matrix и classification report RMS

    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    model_rms.eval()
    with torch.no_grad():
        y_pred = model_rms(X_test)
        y_pred_classes = torch.argmax(y_pred, axis=1)

    cm = confusion_matrix(y_test, y_pred_classes)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix RMS")
    plt.show()

    print("Classification Report:")
    print(classification_report(y_test, y_pred_classes))

    # Confusion matrix и classification report Adam

    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    model_adam.eval()
    with torch.no_grad():
        y_pred = model_adam(X_test)
        y_pred_classes = torch.argmax(y_pred, axis=1)

    cm = confusion_matrix(y_test, y_pred_classes)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix Adam")
    plt.show()

    print("Classification Report:")
    print(classification_report(y_test, y_pred_classes))