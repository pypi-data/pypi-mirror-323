def gold_optimizers():
    """
    Набор данных: regression/gold.csv. Используя библиотеку PyTorch, решите задачу одновременного предсказания столбцов 'Gold_T-7', 'Gold_T-14', 'Gold_T-22' и 'Gold_T+22' (задача регрессии). Разделите набор данных на обучающее и тестовое множество. Выполните предобработку данных (корректно обработайте случаи категориальных и нечисловых столбцов, при наличии). Сравните несколько различных оптимизаторов и графически продемонстрируйте, как выбор оптимизатора влияет на процесс обучения и результаты на тестовом множестве. (20 баллов)
    """
    data = pd.read_csv("gold.csv")

    data = pd.read_csv("gold.csv")

    X = data.drop(['Gold_T-7', 'Gold_T-14', 'Gold_T-22', 'Gold_T+22'], axis=1)
    y = data[['Gold_T-7', 'Gold_T-14', 'Gold_T-22', 'Gold_T+22']]

    numerical_cols = X.columns

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
        ])

    X_processed = preprocessor.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train.values, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test.values, dtype=torch.float32)

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    class Model(nn.Module):
        def __init__(self, input_size, dropout_rate=0.5):
            super(Model, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)
            self.fc2 = nn.Linear(128, 64)
            self.fc3 = nn.Linear(64, 4)
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
        
    batch_size = 64
    epochs = 100
    print_every = 10

    model_sgd = Model(X_train.size(1))
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model_sgd.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_sgd = []
    test_losses_sgd = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_sgd.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_sgd(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_sgd.eval()
        with torch.no_grad():
            test_outputs = model_sgd(X_test)
            test_loss = criterion(test_outputs, y_test)

        train_losses_sgd.append(epoch_loss/batch_size)
        test_losses_sgd.append(test_loss.item())

        if (epoch+1) % print_every == 0:
            print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

    # RMSprop
    batch_size = 64
    epochs = 100
    print_every = 10

    model_rms = Model(X_train.size(1))
    criterion = nn.MSELoss()
    optimizer = optim.RMSprop(model_rms.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_rms = []
    test_losses_rms = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_rms.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_rms(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_rms.eval()
        with torch.no_grad():
            test_outputs = model_rms(X_test)
            test_loss = criterion(test_outputs, y_test)

        train_losses_rms.append(epoch_loss/batch_size)
        test_losses_rms.append(test_loss.item())

        if (epoch+1) % print_every == 0:
            print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')
    
    # Adam

    batch_size = 64
    epochs = 100
    print_every = 10

    model_adam = Model(X_train.size(1))
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model_adam.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_adam = []
    test_losses_adam = []

    for epoch in range(epochs):
        epoch_loss = 0
        model_adam.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model_adam(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        model_adam.eval()
        with torch.no_grad():
            test_outputs = model_adam(X_test)
            test_loss = criterion(test_outputs, y_test)

        train_losses_adam.append(epoch_loss/batch_size)
        test_losses_adam.append(test_loss.item())

        if (epoch+1) % print_every == 0:
            print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss/batch_size:.4f}, Test Loss: {test_loss:.4f}')

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

    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    model_sgd.eval()
    with torch.no_grad():
        y_pred = model_sgd(X_test).numpy()

    y_test_n = y_test.numpy()

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)

    print('SGD')
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")

    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    model_rms.eval()
    with torch.no_grad():
        y_pred = model_rms(X_test).numpy()

    y_test_n = y_test.numpy()

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)

    print('RMSprop')
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")

    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    model_adam.eval()
    with torch.no_grad():
        y_pred = model_adam(X_test).numpy()

    y_test_n = y_test.numpy()

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)

    print('Adam')
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")

def bike_cnt_batchnorm():
    """
    2 Набор данных: regressionbike cntcsv. Используя библиотеку PyTorch, решите залачу предсказания столбца cnt (залача регрессни). Разделите набор данных на обучающее тестовое множество. Выполните предобработку данных (корректно обработайте случаи категорнальных и нечисловых столбцов, при наличии). Отобразите графики значений функции потерь и метрики R^2 на обучающем множестве по эпохам. Рассчитайте значенне метрики R^2 на тестовом множестве. Добавье в модель слои BatchNomldи графически продемонстрируйте, как это влняет на процесс обучення н результаты на тестовом множестве. (20 баллов)
    """

    data = pd.read_csv("bike_cnt.csv")

    X = data.drop(['dteday', 'cnt'], axis=1)
    y = data['cnt']

    numerical_cols = X.columns

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
        ])

    X_processed = preprocessor.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train.values, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test.values, dtype=torch.float32)

    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    class Model(nn.Module):
        def __init__(self, input_size, dropout_rate=0.5):
            super(Model, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)
            self.fc2 = nn.Linear(128, 64)
            self.fc3 = nn.Linear(64, 1)
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
    
    class Model_n(nn.Module):
        def __init__(self, input_size, dropout_rate=0.5):
            super(Model_n, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)
            self.bn1 = nn.BatchNorm1d(128)
            self.fc2 = nn.Linear(128, 64)
            self.bn2 = nn.BatchNorm1d(64)
            self.fc3 = nn.Linear(64, 1)
            self.dropout = nn.Dropout(dropout_rate)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = self.fc1(x)
            x = self.bn1(x)
            x = self.relu(x)
            x = self.dropout(x)
            x = self.fc2(x)
            x = self.bn2(x)
            x = self.relu(x)
            x = self.dropout(x)
            x = self.fc3(x)
            return x
        
    from sklearn.metrics import r2_score
    batch_size = 64
    epochs = 100
    print_every = 10

    model = Model(X_train.shape[1])
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses = []
    train_r2 = []

    for epoch in range(epochs):
        running_loss = 0.0
        model.train()
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs.flatten(), y_batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model.eval()
        with torch.no_grad():
            y_pred = model(X_train).flatten().numpy()
            r2 = r2_score(y_train.numpy(), y_pred)

        train_losses.append(running_loss / len(train_loader))
        train_r2.append(r2)

        if (epoch+1) % print_every == 0:
            print(f'Epoch {epoch+1}/{epochs}, Loss: {running_loss / len(train_loader):.4f}, R^2: {r2:.4f}')
        
    from sklearn.metrics import r2_score

    batch_size = 64
    epochs = 100
    print_every = 10

    model_n = Model_n(X_train.shape[1])
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model_n.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    train_losses_n = []
    train_r2_n = []

    for epoch in range(epochs):
        running_loss = 0.0
        model_n.train()
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model_n(X_batch)
            loss = criterion(outputs.flatten(), y_batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model_n.eval()
        with torch.no_grad():
            y_pred = model_n(X_train).flatten().numpy()
            r2 = r2_score(y_train.numpy(), y_pred)

        train_losses_n.append(running_loss / len(train_loader))
        train_r2_n.append(r2)

        if (epoch+1) % print_every == 0:
            print(f'Epoch {epoch+1}/{epochs}, Loss: {running_loss / len(train_loader):.4f}, R^2: {r2:.4f}')

    plt.plot(range(1, epochs + 1), train_losses, label="Training Loss без batchnorm")
    plt.plot(range(1, epochs + 1), train_losses_n, label="Training Loss с batchnorm")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Training Loss over Epochs")
    plt.legend()
    plt.show()

    plt.plot(range(1, epochs + 1), train_r2, label="Test Loss без batchnorm")
    plt.plot(range(1, epochs + 1), train_r2_n, label="Test Loss с batchnorm")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("R^2 over Epochs")
    plt.legend()
    plt.show()

    model.eval()
    with torch.no_grad():
        y_pred = model(X_train).flatten().numpy()
        r2 = r2_score(y_train.numpy(), y_pred)

    print(f'R^2 без batchnorm1d: {r2:.4f}')

    model_n.eval()
    with torch.no_grad():
        y_pred = model_n(X_train).flatten().numpy()
        r2 = r2_score(y_train.numpy(), y_pred)

    print(f'R^2 с batchnorm1d: {r2:.4f}')