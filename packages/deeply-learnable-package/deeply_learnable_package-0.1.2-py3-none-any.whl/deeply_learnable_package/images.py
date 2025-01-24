def sign_language_close_images():
    """
    Набор данных: images/sign_language.zip. Реализовав сверточную нейронную сеть при помощи библиотеки Ру Torch, решите задачу классификации изображений. Разделите набор данных на обучающее и тестовое множество. Выполните предобработку данных (приведите изображения к одному размеру, нормализуйте и преобразуйте изображения в тензоры). Отобразите confusion matrix и classification report, рассчитанные на основе тестового множества. Выберите один пример из тестового множества, для которого модель ошиблась. Найдите несколько наиболее похожих на данное изображений на основе векторов скрытых представлений, полученных сетью. Визуализируйте оригинальное изображение и найденные похожие изображения. (20 баллов)
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim

    from torch.utils.data import DataLoader
    from torchvision import transforms
    from torchvision.datasets import ImageFolder

    import zipfile
    import os

    zip_file_path = 'sign_language.zip'

    extract_folder = 'sign_language'

    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    print(f"Файлы успешно распакованы в {extract_folder}")

    # Указываем путь к данным (папка, где лежат изображения с подкатегориями)
    data_dir = 'sign_language/sign_language'

    # Проверим, что путь существует
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Папка с данными не найдена по пути: {data_dir}")

    print("Путь к данным:", data_dir)

    from torchvision import transforms

    # Создаем цепочку преобразований для предобработки изображений
    transform = transforms.Compose([
        transforms.Resize((64, 64)),  # Приводим изображения к размеру 64x64
        transforms.ToTensor(),  # Преобразуем изображения в тензоры
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Нормализуем
    ])

    # Загружаем данные с применением преобразований
    full_dataset = ImageFolder(data_dir, transform=transform)

    # Проверим, что данные загружены
    print(f"Количество классов: {len(full_dataset.classes)}")
    print(f"Классы: {full_dataset.classes}")

    from torch.utils.data import random_split

    # Разделяем набор данных на обучающую (70%) и тестовую (30%) выборки
    train_size = int(0.7 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = random_split(full_dataset, [train_size, test_size])

    # Проверим размеры выборок
    print(f"Размер обучающей выборки: {len(train_dataset)}")
    print(f"Размер тестовой выборки: {len(test_dataset)}")

    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    # Создаем класс модели
    class CNN(nn.Module):
        def __init__(self, num_classes):
            super(CNN, self).__init__()
            # Сверточные слои
            self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
            self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

            # Пулинг
            self.pool = nn.MaxPool2d(2, 2)

            # Полносвязные слои
            self.fc1 = nn.Linear(128 * 8 * 8, 512)
            self.fc2 = nn.Linear(512, num_classes)

        def forward(self, x):
            # Прогоняем через сверточные слои и пулинг
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))
            x = self.pool(F.relu(self.conv3(x)))

            # Плоское представление
            x = x.view(-1, 128 * 8 * 8)

            # Проходим через полносвязные слои
            x = F.relu(self.fc1(x))
            x = self.fc2(x)

            return x

    # Число классов (по количеству папок с изображениями)
    num_classes = len(full_dataset.classes)

    # Инициализируем модель
    model = CNN(num_classes)

    import torch.optim as optim
    from torch.utils.data import DataLoader

    # Настройки обучения
    batch_size = 64
    num_epochs = 20

    # Создаем загрузчики данных для обучения и тестирования
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Определяем функцию потерь и оптимизатор
    criterion = nn.CrossEntropyLoss()  # Для многоклассовой классификации
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Обучаем модель
    for epoch in range(num_epochs):
        model.train()  # Включаем режим обучения
        epoch_loss = 0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()  # Обнуляем градиенты
            outputs = model(batch_X)  # Прогоняем батч через модель
            loss = criterion(outputs, batch_y)  # Вычисляем ошибку
            loss.backward()  # Вычисляем градиенты
            optimizer.step()  # Обновляем веса

            epoch_loss += loss.item()

        # Выводим среднюю потерю за эпоху
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss/len(train_loader):.4f}')

    from sklearn.metrics import confusion_matrix, classification_report
    import seaborn as sns
    import matplotlib.pyplot as plt

    # Модель в режиме оценки
    model.eval()

    all_preds = []
    all_labels = []

    # Прогоняем тестовый набор через модель
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Создаем confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    # Визуализируем confusion matrix
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=full_dataset.classes, yticklabels=full_dataset.classes)
    plt.title("Confusion Matrix")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

    # Печатаем classification report
    print(classification_report(all_labels, all_preds, target_names=full_dataset.classes))

    import torch
    import matplotlib.pyplot as plt
    import numpy as np

    # Переводим модель в режим оценки
    model.eval()

    # Ищем ошибочные примеры
    incorrect_idx = None
    for idx, (image, label) in enumerate(test_dataset):
        # Прогоняем изображение через модель
        image = image.unsqueeze(0)  # Добавляем батч-измерение
        output = model(image)
        _, predicted = torch.max(output, 1)  # Получаем предсказанный класс

        # Если предсказание не совпадает с реальным классом, то это ошибка
        if predicted != label:
            incorrect_idx = idx
            break

    # Получаем ошибочное изображение и его реальный класс
    image, true_label = test_dataset[incorrect_idx]
    predicted_class = predicted.item()

    # Визуализируем ошибочное изображение
    plt.imshow(image.permute(1, 2, 0))
    plt.title(f"True label: {full_dataset.classes[true_label]}, Predicted label: {full_dataset.classes[predicted_class]}")
    plt.axis('off')
    plt.show()


    from sklearn.metrics.pairwise import cosine_similarity
    import torch

    # Функция для извлечения скрытого представления изображения (feature vector)
    def get_feature_vector(model, image):
        model.eval()  # Убедиться, что модель в режиме инференса
        with torch.no_grad():
            # Прогоняем изображение через сверточные слои и пулинг
            x = model.pool(F.relu(model.conv1(image)))
            x = model.pool(F.relu(model.conv2(x)))
            x = model.pool(F.relu(model.conv3(x)))
            x = x.view(x.size(0), -1)  # Преобразуем в одномерный вектор


            # Прогоняем через fully connected слои
            x = F.relu(model.fc1(x))
            x = model.fc2(x)  # Получаем выходное значение модели
            return x

    # Получаем feature vector для ошибочного изображения
    feature_vector = get_feature_vector(model, image.unsqueeze(0))

    # Создаем список всех векторов признаков для изображений в тестовом наборе
    all_feature_vectors = []
    for img, _ in test_dataset:
        feature = get_feature_vector(model, img.unsqueeze(0))
        all_feature_vectors.append(feature)

    # Преобразуем все feature vectors в numpy (чтобы можно было использовать cosine_similarity)
    all_feature_vectors = torch.cat(all_feature_vectors, dim=0).cpu().numpy()
    feature_vector_np = feature_vector.cpu().numpy().reshape(1, -1)  # Преобразуем в двумерный массив

    # Рассчитываем косинусное расстояние между ошибочным изображением и всеми остальными
    similarities = cosine_similarity(feature_vector_np, all_feature_vectors)

    # Находим индексы наиболее похожих изображений (включая само ошибочное изображение)
    similar_idx = similarities.argsort()[0][1:6]  # Ищем 5 наиболее похожих изображений

    # Визуализируем оригинальное изображение и найденные похожие изображения
    plt.figure(figsize=(10, 5))
    plt.subplot(2, 3, 1)
    plt.imshow(image.permute(1, 2, 0))
    plt.title(f"Original Image\nTrue label: {full_dataset.classes[true_label]}")
    for i, idx in enumerate(similar_idx):
        plt.subplot(2, 3, i+2)
        similar_image, _ = test_dataset[idx]
        plt.imshow(similar_image.permute(1, 2, 0))
        plt.title(f"Similar {i+1}")
    plt.show()

def sign_language_microf1():
    """
    Набор данных: images/sign_language.zip. Реализовав сверточную нейронную сеть при
помощи библиотеки РyTorch, решите задачу классификации изображений. Разделите
набор данных на обучающее и тестовое множество. Выполните предобработку данных
(приведите изображения к одному размеру, нормализуйте и преобразуйте изображения в
тензоры). Графически отобразите, как качество на тестовом множестве (micro F1) зависит
от количества сверточных блоков (свертка, активация, пулинг). (20 баллов)
"""
    import torch
    import torch.nn as nn
    import torch.optim as optim

    from torch.utils.data import DataLoader
    from torchvision import transforms
    from torchvision.datasets import ImageFolder

    import zipfile
    import os

    zip_file_path = 'sign_language.zip'

    extract_folder = 'sign_language'

    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    print(f"Файлы успешно распакованы в {extract_folder}")

    # Указываем путь к данным (папка, где лежат изображения с подкатегориями)
    data_dir = 'sign_language/sign_language'

    # Проверим, что путь существует
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Папка с данными не найдена по пути: {data_dir}")

    print("Путь к данным:", data_dir)

    # Предобработка изображений
    transform = transforms.Compose([
        transforms.Resize((64,64)),
        transforms.ToTensor(),
        transforms.Normalize(mean = [0.5,0.5,0.5], std = [0.225,0.225,0.225])
    ])

    # Загрузка данных
    full_dataset = ImageFolder(data_dir, transform=transform)

    print(f'Количество классов: {len(full_dataset.classes)}')
    print(f'Классы: {full_dataset.classes}')

    train_size = int(0.7 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(full_dataset, [train_size, test_size])

    # Проверим размеры выборок
    print(f"Размер обучающей выборки: {len(train_dataset)}")
    print(f"Размер тестовой выборки: {len(test_dataset)}")

    class CNN(nn.Module):
        def __init__(self, num_classes):
            super(CNN, self).__init__()
            # Convolution
            self.conv1 = nn.Conv2d(3, 32, kernel_size = 3, padding = 1)
            self.conv2 = nn.Conv2d(32, 64, kernel_size = 3, padding = 1)
            self.conv3 = nn.Conv2d(64, 128, kernel_size = 3, padding = 1)

            #pooling
            self.pool = nn.MaxPool2d(2,2)

            #Full Conv Layer
            self.fc1 = nn.Linear(128 * 8 * 8, 512)
            self.fc2 = nn.Linear(512, num_classes)

        def forward(self, x):
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))
            x = self.pool(F.relu(self.conv3(x)))

            x = x.view(-1, 128 * 8 *8)

            x = F.relu(self.fc1(x))
            x = self.fc2(x)

            return x

    # Число классов (по количеству папок с изображениями)
    num_classes = len(full_dataset.classes)

    # Инициализируем модель
    model = CNN(num_classes)

    import torch.nn.functional as F
    import matplotlib.pyplot as plt
    from sklearn.metrics import f1_score

    # Объявляем модель
    model = CNN(num_classes)

    # Кросс-энтропийная функция потерь
    criterion = nn.CrossEntropyLoss()

    # Оптимизатор Adam
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Настройки обучения
    batch_size = 64
    num_epochs = 20
    print_every = 10

    # Загружаем данные
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Функция для расчета micro F1
    def compute_micro_f1(y_true, y_pred):
        return f1_score(y_true, y_pred, average='micro')

    # Список для отслеживания результата
    f1_scores = []

    # Обучение
    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0
        all_preds = []
        all_labels = []

        # Процесс обучения
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()

            # Прямой проход
            outputs = model(batch_X)

            # Вычисление потерь
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        # Проверка на тестовом наборе
        model.eval()
        with torch.no_grad():
            y_true = []
            y_pred = []

            for batch_X, batch_y in test_loader:
                outputs = model(batch_X)
                _, predicted = torch.max(outputs, 1)
                y_true.extend(batch_y.numpy())
                y_pred.extend(predicted.numpy())

            # Вычисление F1
            f1 = compute_micro_f1(y_true, y_pred)
            f1_scores.append(f1)

        if (epoch + 1) % print_every == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.4f}, F1: {f1:.4f}")
    
    # Сравнение

    class CNN_ThreeBlocks(nn.Module):
        def __init__(self, num_classes):
            super(CNN_ThreeBlocks, self).__init__()

            # 3 сверточных слоя
            self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
            self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

            # Пулинг
            self.pool = nn.MaxPool2d(2, 2)

            # Полносвязанный слой
            self.fc1 = nn.Linear(128 * 8 * 8, 512)  # Размер после 3 блоков
            self.fc2 = nn.Linear(512, num_classes)

        def forward(self, x):
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))
            x = self.pool(F.relu(self.conv3(x)))

            x = x.view(-1, 128 * 8 * 8)  # Преобразуем в одномерный вектор
            x = F.relu(self.fc1(x))
            x = self.fc2(x)

            return x
        
    class CNN_TwoBlocks(nn.Module):
        def __init__(self, num_classes):
            super(CNN_TwoBlocks, self).__init__()

            # 2 сверточных слоя
            self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

            # Пулинг
            self.pool = nn.MaxPool2d(2, 2)

            # Полносвязанный слой
            self.fc1 = nn.Linear(64 * 16 * 16, 512)  # Размер после 2 блоков
            self.fc2 = nn.Linear(512, num_classes)

        def forward(self, x):
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))

            x = x.view(-1, 64 * 16 * 16)  # Преобразуем в одномерный вектор
            x = F.relu(self.fc1(x))
            x = self.fc2(x)

            return x
        
    # Обучаем модель
    def train_and_evaluate(model, train_loader, test_loader, num_epochs=20, print_every=5):
        # Кросс-энтропийная функция потерь
        criterion = nn.CrossEntropyLoss()

        # Оптимизатор Adam
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        f1_scores = []

        for epoch in range(num_epochs):
            model.train()
            epoch_loss = 0
            all_preds = []
            all_labels = []

            # Процесс обучения
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()

                # Прямой проход
                outputs = model(batch_X)

                # Вычисление потерь
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()

            # Проверка на тестовом наборе
            model.eval()
            with torch.no_grad():
                y_true = []
                y_pred = []

                for batch_X, batch_y in test_loader:
                    outputs = model(batch_X)
                    _, predicted = torch.max(outputs, 1)
                    y_true.extend(batch_y.numpy())
                    y_pred.extend(predicted.numpy())

                # Вычисление F1
                f1 = compute_micro_f1(y_true, y_pred)
                f1_scores.append(f1)

            if (epoch + 1) % print_every == 0:
                print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.4f}, F1: {f1:.4f}")

        return f1_scores

    # Загружаем данные
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64)

    # Обучаем модель с 3 слоями
    model_three_blocks = CNN_ThreeBlocks(num_classes)
    f1_scores_three_blocks = train_and_evaluate(model_three_blocks, train_loader, test_loader)

    # Обучаем модель с 2 слоями
    model_two_blocks = CNN_TwoBlocks(num_classes)
    f1_scores_two_blocks = train_and_evaluate(model_two_blocks, train_loader, test_loader)

    # Построим график F1
    plt.figure(figsize=(10, 6))

    # Рисуем график для обеих моделей
    plt.plot(range(1, len(f1_scores_three_blocks) + 1), f1_scores_three_blocks, label='3 Convolutional Blocks')
    plt.plot(range(1, len(f1_scores_two_blocks) + 1), f1_scores_two_blocks, label='2 Convolutional Blocks')

    plt.xlabel('Epoch')
    plt.ylabel('Micro F1 Score')
    plt.title('Micro F1 Score Comparison: 2 vs 3 Convolutional Blocks')
    plt.legend()
    plt.grid(True)
    plt.show()

def sign_language_pca():
    """
    3. Набор данных: images/sign_language.zip. Реализовав сверточную нейронную сеть при помощи библиотеки РуТorch, решите залачу классификации изображений. Разделите набор данных на обучающее и тестовое множество. Выполните предобработку данных (приведите изображения к одному размеру, нормализуйте и преобразуйте изображення в тензоры). Отобразите графики значений функции потерь по эпохам на обучающем множестве. Отобразите confusion matrix u classification repor, рассчитанные на основе тестового множества. Уменьшите размерность.скрытых представлений изображений с помощью РСА и визуализируйте полученные представления, раскрасив точки в соответствин с классами. (20 баллов)
    """

    import torch
    import torch.nn as nn
    import torch.optim as optim

    from torch.utils.data import DataLoader
    from torchvision import transforms
    from torchvision.datasets import ImageFolder

    import zipfile
    import os

    zip_file_path = 'sign_language.zip'

    extract_folder = 'sign_language'

    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    print(f"Файлы успешно распакованы в {extract_folder}")

    # Предобработка изображений
    transform = transforms.Compose([
        transforms.Resize((128,128)),
        transforms.ToTensor(),
        transforms.Normalize(mean = [0.5,0.5,0.5], std = [0.225,0.225,0.225])
    ])

    # Загрузка данных
    data = ImageFolder('/content/sign_language/sign_language', transform=transform)

    print(f'Количество классов: {len(data.classes)}')
    print(f'Классы: {data.classes}')

    train_size = int(0.8 * len(data))
    test_size = len(data) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(data, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    class CNN(nn.Module):
        def __init__(self, num_classes):
            super(CNN, self).__init__()
            self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
            self.relu = nn.ReLU()
            self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
            self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
            self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
            self.conv4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
            self.fc1 = nn.Linear(128*8*8, 512)
            self.fc2 = nn.Linear(512, 128)
            self.fc3 = nn.Linear(128, num_classes)

        def forward(self, x):
            x = self.maxpool(self.relu(self.conv1(x)))
            x = self.maxpool(self.relu(self.conv2(x)))
            x = self.maxpool(self.relu(self.conv3(x)))
            x = self.maxpool(self.relu(self.conv4(x)))
            x = x.view(-1, 128*8*8)
            x = self.fc3(self.relu(self.fc2(self.relu(self.fc1(x)))))
            return x
        
    import matplotlib.pyplot as plt

    num_classes = 10
    model = CNN(num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    losses = []
    for epoch in range(10):
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            inputs, labels = data
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        losses.append(running_loss / len(train_loader))
        print(f'Epoch {epoch + 1}, Loss: {running_loss / len(train_loader)}')

    plt.plot(losses)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss')
    plt.show()

    import seaborn as sns
    from sklearn.decomposition import PCA
    from sklearn.metrics import classification_report, confusion_matrix

    model.eval()
    with torch.no_grad():
        y_pred = []
        y_true = []
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            y_pred.extend(predicted.tolist())
            y_true.extend(labels.tolist())

    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()

    print(classification_report(y_true, y_pred, target_names=data.classes))

    with torch.no_grad():
        features = []
        labels = []
        for inputs, lbls in train_loader:
            x = model.conv2(model.relu(model.conv1(inputs)))
            x = torch.flatten(x, 1)
            features.extend(x.numpy())
            labels.extend(lbls.numpy())

    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(features)

    plt.figure(figsize=(8, 6))
    for i in range(num_classes):
    plt.scatter(reduced_features[labels == i, 0], reduced_features[labels == i, 1], label=data.classes[i])
    plt.legend()
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('PCA Visualization')
    plt.show()

def clothes_multi():
    """
    Набор данных: images/clothes_multi.zip. Реализовав сверточную нейронную сеть при помощи библиотеки PyTorch, решите задачу множественной (multi-label) классификации изображений. Для каждого изображения модель должна предсказывать два класса: цвет и предмет одежды. Разделите набор данных на обучающее и тестовое множество. Выполните предобработку данных (приведите изображения к одному размеру, нормализуйте и преобразуйте в тензоры). Выведите итоговое значение F1 обучающем множестве и F1 на тестовом множестве. (20 баллов)
    """

    import os
    import torch
    from torch import nn, optim
    from torch.utils.data import Dataset, DataLoader, random_split
    from torchvision import transforms, models
    from PIL import Image
    from sklearn.metrics import f1_score
    import numpy as np
    import matplotlib.pyplot as plt

    # Распаковка архива
    import zipfile
    zip_file_path = 'clothes_multi.zip'
    extract_folder = 'clothes_multi'

    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

    # Определение Dataset
    class ClothesDataset(Dataset):
        def __init__(self, root_dir, transform=None):
            self.root_dir = root_dir
            self.transform = transform
            self.samples = []

            for color in os.listdir(root_dir):
                color_dir = os.path.join(root_dir, color)
                if os.path.isdir(color_dir):
                    for clothes_type in os.listdir(color_dir):
                        clothes_dir = os.path.join(color_dir, clothes_type)
                        if os.path.isdir(clothes_dir):
                            for img_name in os.listdir(clothes_dir):
                                img_path = os.path.join(clothes_dir, img_name)
                                self.samples.append((img_path, color, clothes_type))

            self.color_classes = sorted({color for _, color, _ in self.samples})
            self.clothes_classes = sorted({clothes for _, _, clothes in self.samples})
            self.color_to_idx = {color: i for i, color in enumerate(self.color_classes)}
            self.clothes_to_idx = {clothes: i for i, clothes in enumerate(self.clothes_classes)}

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            img_path, color, clothes = self.samples[idx]
            image = Image.open(img_path).convert('RGB')
            color_label = self.color_to_idx[color]
            clothes_label = self.clothes_to_idx[clothes]
            if self.transform:
                image = self.transform(image)
            return image, (color_label, clothes_label)

    # Трансформы
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Загрузка данных
    dataset = ClothesDataset(root_dir='clothes_multi', transform=transform)
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

    # DataLoader
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)

    # Модель
    class MultiTaskModel(nn.Module):
        def __init__(self, num_colors, num_clothes):
            super().__init__()
            self.base = models.resnet18(pretrained=True)
            in_features = self.base.fc.in_features
            self.base.fc = nn.Identity()
            self.color_classifier = nn.Linear(in_features, num_colors)
            self.clothes_classifier = nn.Linear(in_features, num_clothes)

        def forward(self, x):
            features = self.base(x)
            color = self.color_classifier(features)
            clothes = self.clothes_classifier(features)
            return color, clothes

    # Инициализация
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    num_colors = len(dataset.color_classes)
    num_clothes = len(dataset.clothes_classes)
    model = MultiTaskModel(num_colors, num_clothes).to(device)

    # Функции потерь и оптимизатор
    criterion_color = nn.CrossEntropyLoss()
    criterion_clothes = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Обучение с трекингом метрик
    num_epochs = 5
    current_step = 0
    train_loss_history = []
    test_loss_history = []
    train_f1_history = {'color': [], 'clothes': []}
    test_f1_history = {'color': [], 'clothes': []}
    test_steps = []
    losses = []

    for epoch in range(num_epochs):
        model.train()
        epoch_train_loss = 0
        color_preds, color_labels = [], []
        clothes_preds, clothes_labels = [], []

        for batch_idx, (images, (clr_lbl, cls_lbl)) in enumerate(train_loader):
            images = images.to(device)
            clr_lbl = clr_lbl.to(device)
            cls_lbl = cls_lbl.to(device)

            optimizer.zero_grad()
            outputs_color, outputs_clothes = model(images)
            loss = criterion_color(outputs_color, clr_lbl) + criterion_clothes(outputs_clothes, cls_lbl)
            loss.backward()
            optimizer.step()

            # Сохранение метрик
            epoch_train_loss += loss.item()
            train_loss_history.append(loss.item())
            current_step += 1

            color_preds.extend(torch.argmax(outputs_color, 1).cpu().numpy())
            color_labels.extend(clr_lbl.cpu().numpy())
            clothes_preds.extend(torch.argmax(outputs_clothes, 1).cpu().numpy())
            clothes_labels.extend(cls_lbl.cpu().numpy())

            losses.append(loss.item())

        # Расчет F1 для эпохи
        train_f1_color = f1_score(color_labels, color_preds, average='macro')
        train_f1_clothes = f1_score(clothes_labels, clothes_preds, average='macro')
        train_f1_history['color'].append(train_f1_color)
        train_f1_history['clothes'].append(train_f1_clothes)

        # Валидация
        model.eval()
        test_color_preds, test_color_labels = [], []
        test_clothes_preds, test_clothes_labels = [], []
        epoch_test_loss = 0

        with torch.no_grad():
            for images, (clr_lbl, cls_lbl) in test_loader:
                images = images.to(device)
                clr_lbl = clr_lbl.to(device)
                cls_lbl = cls_lbl.to(device)

                outputs_color, outputs_clothes = model(images)
                loss = criterion_color(outputs_color, clr_lbl) + criterion_clothes(outputs_clothes, cls_lbl)
                epoch_test_loss += loss.item()

                test_color_preds.extend(torch.argmax(outputs_color, 1).cpu().numpy())
                test_color_labels.extend(clr_lbl.cpu().numpy())
                test_clothes_preds.extend(torch.argmax(outputs_clothes, 1).cpu().numpy())
                test_clothes_labels.extend(cls_lbl.cpu().numpy())

        # Сохранение тестовых метрик
        test_steps.append(current_step)
        test_loss_history.append(epoch_test_loss/len(test_loader))
        test_f1_history['color'].append(f1_score(test_color_labels, test_color_preds, average='macro'))
        test_f1_history['clothes'].append(f1_score(test_clothes_labels, test_clothes_preds, average='macro'))

        print(f'Epoch {epoch+1}')
        print(f'Train F1: Color {train_f1_color:.4f}, Clothes {train_f1_clothes:.4f}')
        print(f'Test F1: Color {test_f1_history["color"][-1]:.4f}, Clothes {test_f1_history["clothes"][-1]:.4f}\n')

    # Визуализация графиков
    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    plt.plot(range(len(train_loss_history)), train_loss_history, label='Train Loss')
    plt.plot(test_steps, test_loss_history, 'o-', label='Test Loss')
    plt.xlabel('Training Steps')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1,2,2)
    epochs = range(1, num_epochs+1)
    plt.plot(epochs, train_f1_history['color'], 'b-', label='Train Color F1')
    plt.plot(epochs, train_f1_history['clothes'], 'g-', label='Train Clothes F1')
    plt.plot(epochs, test_f1_history['color'], 'b--', label='Test Color F1')
    plt.plot(epochs, test_f1_history['clothes'], 'g--', label='Test Clothes F1')
    plt.xlabel('Epochs')
    plt.ylabel('F1 Score')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Отдельные графики
    plt.figure(figsize=(10,5))
    plt.plot(range(len(train_loss_history)), train_loss_history, label='Train Loss')
    plt.plot(test_steps, test_loss_history, 'o-', label='Test Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Training Steps')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

    plt.figure(figsize=(10,5))
    plt.plot(epochs, train_f1_history['color'], 'b-', label='Train Color F1')
    plt.plot(epochs, train_f1_history['clothes'], 'g-', label='Train Clothes F1')
    plt.plot(epochs, test_f1_history['color'], 'b--', label='Test Color F1')
    plt.plot(epochs, test_f1_history['clothes'], 'g--', label='Test Clothes F1')
    plt.title('F1 Scores Progress')
    plt.xlabel('Epochs')
    plt.ylabel('F1 Score')
    plt.legend()
    plt.show()

def eng_handwritten_random_modifications():
    """
    3. Набор даниых; images/eng_handwritten.zip. Реализовав сверточную нейронную сеть при
помощи библиотеки PyТогсh, решите залачу классификации изображений. Разделите
набор данных на обучающее, валиданионное и тестовое множество. Выполните
предобработку данных (вырежьте центральную область изображений одинакового
размера и преобразуйте изображения в тензоры). Выведите значение mіcro F1 на тестовом
можестие. Выберите случайным образом одно изображение из тестового множества и
проведите слелайте три любые случайные модификации. Визуализируйте измененные
изображения и продемонстрируйте, как эти изменения влияют на предсказания модели.
(20 ба.лов)
    """

    import torch
    import torch.nn as nn
    import torch.optim as optim

    from torch.utils.data import DataLoader
    from torchvision import transforms
    from torchvision.datasets import ImageFolder

    import zipfile
    import os

    data_zip = "datasets/images/eng_handwritten.zip"
    extract_dir = "datasets/images/"

    # Распаковка архива
    with zipfile.ZipFile(data_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Разделите
    # набор данных на обучающее, валиданионное и тестовое множество. Выполните
    # предобработку данных (вырежьте центральную область изображений одинакового
    # размера и преобразуйте изображения в тензоры)

    # Предобработка изображений
    transform = transforms.Compose([
        transforms.Grayscale(),  # Преобразуем изображения в градации серого
        transforms.CenterCrop(256),  # Вырезаем центральную область размером 256x256
        transforms.ToTensor(),  # Преобразуем в тензор
        transforms.Normalize((0.5,), (0.5,))  # Нормализация
    ])

    # Загрузка данных
    full_dataset = ImageFolder("datasets/images/eng_handwritten", transform=transform)

    train_size = int(0.7 * len(full_dataset))
    val_size = int(0.15 * len(full_dataset))
    test_size = len(full_dataset) - train_size - val_size
    train_dataset, val_dataset, test_dataset  = torch.utils.data.random_split(full_dataset, [train_size, val_size, test_size])

    class CNN(nn.Module):
        def __init__(self, num_classes):
            super(CNN, self).__init__()
            self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
            self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
            self.relu = nn.ReLU()

            self.flatten = nn.Flatten()
            self.fc1 = nn.Linear(64*64*64, 128)
            self.fc2 = nn.Linear(128, num_classes)
        def forward(self, x):
            x = self.conv1(x)
            x = self.relu(x)
            x = self.pool(x)
            x = self.conv2(x)
            x = self.relu(x)
            x = self.pool(x)
            x = self.flatten(x)
            x = self.fc1(x)
            x = self.relu(x)
            x = self.fc2(x)
            return x
        
    batch_size = 64
    num_epochs = 10
    print_every = 1
    num_classes = len(full_dataset.classes)


    model = CNN(num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    losses = []
    for epoch in range(num_epochs):
        epoch_loss = 0
        model.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        losses.append(epoch_loss)

        # Выводим потери каждые print_every эпох
        if (epoch+1) % print_every == 0:
            print(f'Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.4f}, ...')

    import matplotlib.pyplot as plt

    # Значения эпох и потерь
    epochs = list(range(1, 11))

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, losses, marker='o', linestyle='-', label='Training Loss')
    plt.title("Training Loss Over Epochs")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Выведите значение mіcro F1 на тестовом
    # можестие.
    from sklearn.metrics import f1_score
    model.eval()
    with torch.no_grad():
        all_preds = []
        all_labels = []
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.numpy())
            all_labels.extend(labels.numpy())
        
        f1 = f1_score(all_labels, all_preds, average="micro")
        print(f"Micro F1 Score: {f1:.4f}")

    # Выберите случайным образом одно изображение из тестового множества и
    # проведите слелайте три любые случайные модификации. Визуализируйте измененные
    # изображения и продемонстрируйте, как эти изменения влияют на предсказания модели.

    ## Выбор случайного изображения из тестового множества и модификации
    sample_image, sample_label = test_dataset[np.random.randint(len(test_dataset))]
    sample_image_tensor = sample_image.unsqueeze(0)  # Добавляем batch размерность

    # Визуализация оригинального и модифицированных изображений
    transformations = [
        transforms.RandomRotation(30),
        transforms.ColorJitter(brightness=0.5),
        transforms.RandomHorizontalFlip(p=1.0)
    ]

    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    axes[0].imshow(sample_image.squeeze(), cmap='gray')
    axes[0].set_title("Original")
    axes[0].axis("off")

    original_prediction = model(sample_image_tensor).argmax(dim=1).item()
    axes[0].set_xlabel(f"Pred: {original_prediction}")

    class_names = full_dataset.classes

    for i, t in enumerate(transformations):
        modified_image = t(sample_image)
        modified_image_tensor = modified_image.unsqueeze(0)  # Добавляем batch размерность
        modified_prediction = model(modified_image_tensor).argmax(dim=1).item()
        axes[i+1].imshow(modified_image.squeeze(), cmap='gray')
        axes[i+1].set_title(f"Transform {i+1}")
        axes[i+1].set_xlabel(f"Pred: {class_names[modified_prediction]}")

    plt.show()
