def a():
    return """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

np.random.seed(42)

sicaklik = np.random.randint(100, 301, size=100)
dayanim = np.random.randint(210, 271, size=100)

X = sicaklik.reshape(-1,1)
y = dayanim

model = LinearRegression()
model.fit(X, y)

tahmin = np.array([[275]])
tahmin_egitim = model.predict(tahmin)[0]

print(f"210 derecedeki dayanım değeri = {tahmin_egitim} MPA.\\n")

y_pred = model.predict(X)
r2 = r2_score(y, y_pred)
print(f"modelin r2 değeri = {r2}")

plt.figure(figsize=(10,8))
# Veri Görselleştirme
plt.scatter(X, y, color='blue', label='Veri Noktaları')
plt.plot(X, y_pred, color='red', label='Lineer Regresyon Doğrusu')
plt.xlabel('Sıcaklık (°C)')
plt.ylabel('Dayanıklılık (MPa)')
plt.title('Sıcaklık ve Dayanıklılık İlişkisi')
plt.legend()
    """

def b():
    return """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

df = pd.read_excel("isci_tatmini.xlsx")
np.random.seed(42)
tatmin = np.random.choice([0, 1], size=12)

print(df)

X = df[["Maaş", "Çalışma saaati"]]
y = tatmin

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

tatmin = np.array([[int(input("Bir maaş değeri girin : ")), int(input("Bir çalışma saaati girin : "))]])
tatmin_oldumu = model.predict(tatmin)[0]

if tatmin_oldumu == 1:
    print("TATMİN OLDU")
else:
    print("TATMİN OLMADI")

y_pred = model.predict(X_test)
accuracy_score_value = accuracy_score(y_test, y_pred)

print(f"modelin doğruluk skoru = {accuracy_score_value}")

# X_test'i ayırarak plot işlemi yapalım
X_test_maas = X_test["Maaş"]
X_test_saat = X_test["Çalışma saaati"]

plt.figure(figsize=(8, 6))
plt.scatter(X_test_maas, y_test, color='blue', label='Gerçek Değerler')
plt.scatter(X_test_maas, y_pred, color='red', label='Tahminler', marker='x')
plt.xlabel('MAAŞ')
plt.ylabel('TATMIN DURUMU (0=Olmadı, 1=Oldu)')
plt.title('KNN ile İşçi Tatmini ve Maaş İlişkisi')
plt.legend()
plt.grid(True)
plt.show()
    """

def c():
    return """
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn import tree

# Veriyi oku
df = pd.read_excel("malzeme_ozellikleri_updated.xlsx")
print(df)

# Özellikleri ve etiketleri doğru şekilde ayarla
X = df[["Sertlik (HV)"]]  # X tek bir özellik olmalı
y = df[["Sıcaklık Genleşmesi (α × 10⁻⁶/°C)", "Elastikiyet Modülü (GPa)", "Yoğunluk (g/cm³)",
        "Çekme Dayanımı (MPa)", "Eğilme Modülü (GPa)"]]  # y çoklu sürekli değişkenler

# Veriyi eğitim ve test setlerine ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modeli oluştur ve eğit
model = DecisionTreeRegressor(random_state=42)
model.fit(X_train, y_train)

# Modeli test et
print(f"tahmin: {model.predict(np.array([[500]]))[0]} özelliklerine sahip malzeme kullanmalısın.")

# Doğruluk skoru hesapla
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)  # Mean squared error kullanıyoruz
print(f"modelin doğruluğu (MSE): {mse}")

# Modelin karar ağacını görselleştir
plt.figure(figsize=(15, 10))
tree.plot_tree(model, filled=True, feature_names=["Sertlik (HV)"],
               class_names=y.columns.tolist(), rounded=True, fontsize=12)
plt.title("Decision Tree Modeli")
plt.show()

# Gerçek ve tahmin edilen değerlerin karşılaştırılması
plt.figure(figsize=(8, 6))
plt.scatter(X_test, y_test.iloc[:, 0], color='blue', label='Gerçek Değerler (Sıcaklık Genleşmesi)')
plt.scatter(X_test, y_pred[:, 0], color='red', label='Tahminler (Sıcaklık Genleşmesi)', marker='x')
plt.xlabel('Sertlik (HV)')
plt.ylabel('Sıcaklık Genleşmesi (α × 10⁻⁶/°C)')
plt.title('Gerçek ve Tahmin Edilen Sıcaklık Genleşmesi')
plt.legend()
plt.grid(True)
plt.show()
    """


