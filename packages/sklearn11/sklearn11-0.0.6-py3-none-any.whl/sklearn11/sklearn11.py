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

def d():
    return """
ÖRNEK SINAV SORULARI
Soru 1. Bir üretim hattında sıcaklık ve dayanıklılık arasındaki ilişkiyi analiz edin.
Veriler: Sıcaklık 100-300°C derece arasında, dayanım ise 210-270 MPa arasında değişmek üzere, sıcaklık ve dayanım arasındaki ilişkiyi lineer regresyon ile inceleyin.
Çözümde bulunması gereken adımlar:
1. Veri Analizi ve Lineer Regresyon Modeli Oluşturma 
•	Verilen sıcaklık (bağımsız değişken) ve dayanıklılık (bağımlı değişken) verilerini kullanarak bir lineer regresyon modeli oluşturun.
•	Python'da uygun bir kütüphane kullanarak modeli eğitin.
2. Tahmin Yapma
•	Modeli kullanarak 275 °C'de malzemenin dayanıklılığını tahmin edin.
3. Model Performansı
•	Modelin doğruluğunu değerlendirmek için R² değerini hesaplayın ve sonuçları yorumlayın.
4. Veri Görselleştirme
•	Python'da uygun bir kütüphane kullanarak:
o	Verilerin bir dağılım grafiğini çizin.
KODU:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# 1. Veri Analizi ve Lineer Regresyon Modeli Oluşturma
# Veriler: Sıcaklık (100-300°C) ve Dayanıklılık (210-270 MPa)
sıcaklık = np.array([100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300])  # Bağımsız değişken
dayanıklılık = np.array([210, 215, 220, 225, 230, 235, 240, 245, 250, 260, 270])  # Bağımlı değişken

# Veriyi uygun formata sokma (X: sıcaklık, y: dayanıklılık)
X = sıcaklık.reshape(-1, 1)  # X bağımsız değişken
y = dayanıklılık  # y bağımlı değişken

# Lineer Regresyon Modeli oluşturma
model = LinearRegression()
model.fit(X, y)

# 2. Tahmin Yapma
# 275°C için dayanıklılığı tahmin etme
tahmin = model.predict(np.array([[275]]))
print(f"275°C'deki malzemenin dayanıklılığı: {tahmin[0]:.2f} MPa")

# 3. Model Performansı
# Modelin doğruluğunu (R² değeri) hesaplama
y_pred = model.predict(X)
r2 = r2_score(y, y_pred)
print(f"Modelin R² değeri: {r2:.4f}")

# 4. Veri Görselleştirme
plt.figure(figsize=(8, 6))

# Verilerin dağılım grafiği
plt.scatter(sıcaklık, dayanıklılık, color='blue', label='Veriler')

# Regresyon doğrusunu çizme
plt.plot(sıcaklık, model.predict(X), color='red', label='Regresyon Doğrusu')

# Grafik başlığı ve etiketleri
plt.title('Sıcaklık ve Dayanıklılık Arasındaki İlişki')
plt.xlabel('Sıcaklık (°C)')
plt.ylabel('Dayanıklılık (MPa)')

# Grafik gösterimi
plt.legend()
plt.show()
---------------------------------
Soru 2. Excel’de verilen dataları kullanarak bir öğrencinin ders geçme durumunu Logistic Regresyon ile inceleyin. 
Çalışma saat: 0-11 saat arasında 100 adet değer
Sınavdan alınan not: 0-100 arasında 100 adet
Geçme/kalma durumu: 0-1 olmak üzere 100 adet değer üretilecek
Çözümde bulunması gereken adımlar:
1. Veri Analizi ve Model Eğitimi
•	Verilen verilerle bir lojistik regresyon modeli oluşturun.
•	Python'da uygun kütüphaneyi kullanarak modeli eğitin.
2. Tahmin Yapma
•	Modeli kullanarak 9 saat çalışan ve 75 puan alan bir öğrencinin sınıfı geçip geçmeyeceğini tahmin edin.
3. Model Performansı
•	Modelin doğruluğunu ölçmek için accuracy (doğruluk) metriklerini hesaplayın.
4. Görselleştirme
•	Öğrencilerin "Çalışma Saati" ve "Sınav Puanı" ile "Geçti mi?" arasında olan ilişkiyi bir grafikle gösterin.


KODU
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 1. Excel dosyasından veri okuma
file_path = "data.xlsx"  # Excel dosyasının yolunu belirtin
data = pd.read_excel(file_path)

# Özellikler (X) ve hedef değişken (y)
X = data[["Çalışma Saati", "Sınav Puanı"]]
y = data["Geçti mi?"]

# Veriyi eğitim ve test setine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Lojistik regresyon modeli oluşturma ve eğitme
model = LogisticRegression()
model.fit(X_train, y_train)

# 3. Tahmin yapma
new_data = np.array([[9, 75]])  # Yeni öğrenci verisi
prediction = model.predict(new_data)
probability = model.predict_proba(new_data)

print(f"\n9 saat çalışan ve 75 puan alan bir öğrencinin geçme durumu: {'Geçti' if prediction[0] == 1 else 'Kaldı'} "
      f"(Olasılık: {probability[0][1]:.2f})")

# 4. Model performansı
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel doğruluğu (accuracy): {accuracy:.2f}")

# 5. Görselleştirme
plt.figure(figsize=(8, 6))

# Verilerin dağılım grafiği
for i, label in enumerate(y):
    color = "green" if label == 1 else "red"
    plt.scatter(X["Çalışma Saati"].iloc[i], X["Sınav Puanı"].iloc[i], color=color, label="Geçti" if label == 1 else "Kaldı")

plt.xlabel("Çalışma Saati")
plt.ylabel("Sınav Puanı")
plt.title("Öğrencilerin Çalışma Saati ve Sınav Puanlarına Göre Dağılımı")
plt.show()
------------------------------------
Soru 3. Bir okulda, öğrencilerin çalışma saati ve sınav puanı bilgilerine dayanarak, öğrencinin sınavı geçip geçmediğini Random Tree metoduyla belirleyiniz.
veri = { 'Çalışma Saati': [5, 8, 12, 16, 20, 25, 30], 'Sınav Puanı': [50, 60, 65, 70, 80, 85, 90], 'Geçme Durumu': [0, 0, 0, 1, 1, 1, 1] }
Çözümde bulunması gereken adımlar:
1. Veri Oluşturma:
1.	Öğrencilerin çalışma saati, sınav puanı ve geçme durumu bilgilerini içeren veriyi oluşturun.
2. Karar Ağacı Modeli Oluşturma:
3. Tahmin Yapma:
Eğittiğiniz karar ağacını kullanarak test verileri üzerinde tahmin yapın.
4. Model Performansını Değerlendirme:
Modelin doğruluğunu (accuracy) accuracy_score fonksiyonu ile hesaplayın.
Modelin doğruluğunu ekrana yazdırın.
5. Karar Ağacının Görselleştirilmesi:
Karar ağacındaki her bir düğümdeki koşul ve sınıf dağılımını gösteren bir grafik oluşturun.

KODU
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from sklearn import tree

# 1. Veriyi oluşturma
veri = {
    'Çalışma Saati': [5, 8, 12, 16, 20, 25, 30],
    'Sınav Puanı': [50, 60, 65, 70, 80, 85, 90],
    'Geçme Durumu': [0, 0, 0, 1, 1, 1, 1]
}

# Pandas DataFrame oluşturma
df = pd.DataFrame(veri)

# 2. Bağımsız ve bağımlı değişkenleri ayırma
X = df[['Çalışma Saati', 'Sınav Puanı']]  # Bağımsız değişkenler
y = df['Geçme Durumu']  # Bağımlı değişken (Geçti/Kaldı)

# 3. Eğitim ve test verilerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 4. Karar Ağacı Modeli
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)  # Modeli eğitme

# 5. Test seti üzerinde tahmin yapma
y_pred = model.predict(X_test)

# 6. Modelin doğruluğunu değerlendirme
accuracy = accuracy_score(y_test, y_pred)
print(f"Modelin Doğruluğu: {accuracy:.2f}")

# 7. Karar ağacını görselleştirme
plt.figure(figsize=(10, 8))
tree.plot_tree(model, filled=True, feature_names=['Çalışma Saati', 'Sınav Puanı'], class_names=['Kaldı', 'Geçti'], rounded=True)
plt.title('Karar Ağacı Modeli')
plt.show()

Soru 4. 3 ü K-Nearest Neighbors, KNN algoritmasıyla tekrar çözün.

Soru 5. Verilen verilere dayanarak, kesme hızı, ilerleme hızı ve kesme derinliğinin takım aşınması üzerindeki etkilerini analiz edin. Bu parametrelerin takım ömrü ve iş parçası kalitesi üzerindeki olası etkilerini tartışın.

Çözümde bulunması gereken adımlar:
1. Veri Oluşturma:
2. Modeli Oluşturma:
3. Tahmin Yapma:
4. Model Performansını Değerlendirme:
Modelin doğruluğunu (accuracy) accuracy_score fonksiyonu ile hesaplayın.
Modelin doğruluğunu ekrana yazdırın.
5. Elde edilen sonuçları grafik olarak çizdirme:
KOD
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Veriyi yükleyin
df = pd.read_excel('takim_asinmasi_verisi.xlsx')

# Takım aşınması miktarını sınıflandırmak için bir eşik değeri belirleyin
# Örneğin, aşınma miktarı 0.07'den büyükse 1 (aşınma var), küçükse 0 (aşınma yok) olarak sınıflandıralım
df['Takım Aşınma Durumu'] = (df['Takım Aşınma Miktarı (mm)'] > 0.07).astype(int)

# Özellikler (X) ve hedef değişken (y)
X = df[['Kesme Hızı (m/dak)', 'İlerleme Hızı (mm/devir)', 'Kesme Derinliği (mm)']]
y = df['Takım Aşınma Durumu']

# Veriyi eğitim ve test olarak bölelim
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic Regresyon modelini oluşturun
model = LogisticRegression()
model.fit(X_train, y_train)

# Test verisi ile tahmin yapalım
y_pred = model.predict(X_test)

# Modelin doğruluğunu hesaplayalım
accuracy = accuracy_score(y_test, y_pred)

print(f"Modelin doğruluk oranı: {accuracy:.2f}")
--------------------------------------------------------------

    """

def e():
    return """
    --------------------------------------------------------------

#lineer regresyon bir dairenin metre karesini kullanarak fiyatını hesaplama //basit regresyon
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Veriyi Excel'den okuma
data = pd.read_excel("basit.xlsx")

# Model için bağımsız ve bağımlı değişkenleri ayırma
X = data[['Alan']]  # Bağımsız değişken
y = data['Fiyat']   # Bağımlı değişken

# Veriyi eğitim (%80) ve test (%20) setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model oluşturma ve eğitme
model = LinearRegression()
model.fit(X_train, y_train)

# Test seti üzerinde tahmin yapma
y_pred = model.predict(X_test)

# Performans metriklerini hesaplama
mse = mean_squared_error(y_test, y_pred)  # Ortalama kare hata
r2 = r2_score(y_test, y_pred)  # R-kare

# Performans sonuçlarını yazdırma
print("Mean Squared Error (MSE):", mse)
print("R-squared (R²):", r2)

# Görselleştirme (Test seti için)
plt.scatter(X_test, y_test, label="Gerçek Veri", color="blue")
plt.plot(X_test, y_pred, label="Tahmin", color="red")
plt.xlabel("Alan (m^2)")
plt.ylabel("Fiyat (Bin TL)")
plt.title("Basit Lineer Regresyon (Test Seti)")
plt.legend()
plt.show()

# Tahmin yapmak istediğiniz daire fiyatı
new_data = pd.DataFrame({'Alan': [300]})  # Sütun adı 'Alan' ile aynı olmalı

# Tahmin edilen fiyatı hesaplama
predicted_flat = model.predict(new_data)
# Tahmin sonuçlarını yazdırma
print("Tahmin Edilen Daire Fiyatı (300 m²):", predicted_flat, "Bin TL")

#Talaşlı imalat işlemlerinde kesme hızının yüzey pürüzlülüğü üzerindeki etkisini analiz etmek.

--------------------------------------------------------------

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Örnek veri seti
data = pd.DataFrame({
    'Kesme_Hızı': [50, 100, 150, 200, 250, 300, 350, 400],
    'Yüzey_Pürüzlülüğü': [3.2, 2.8, 2.4, 2.1, 1.8, 1.5, 1.2, 1.0]
})

# Model için bağımsız (X) ve bağımlı (y) değişkenleri ayırma
X = data[['Kesme_Hızı']]
y = data['Yüzey_Pürüzlülüğü']

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model oluşturma ve eğitme
model = LinearRegression()
model.fit(X_train, y_train)

# Test seti üzerinde tahmin yapma
y_pred = model.predict(X_test)

# Performans Metrikleri
mse = mean_squared_error(y_test, y_pred)  # Ortalama Kare Hata
r2 = r2_score(y_test, y_pred)  # R² Skoru

# Performans sonuçlarını yazdırma
print("Ortalama Kare Hata (MSE - Tahmin doğruluğu):", round(mse, 4))
print("R² Katsayısı (Modelin açıklama gücü):", round(r2, 4))

# Eğitim ve test verilerini grafik olarak gösterme
plt.scatter(X, y, color='blue', label='Gerçek Veri')
plt.plot(X, model.predict(X), color='red', label='Model')
plt.xlabel('Kesme Hızı (m/dk)')
plt.ylabel('Yüzey Pürüzlülüğü (Ra)')
plt.title('Kesme Hızı ve Yüzey Pürüzlülüğü Tahmini')
plt.legend()
plt.show()

# Yeni kesme hızı verileri
new_data = pd.DataFrame({'Kesme_Hızı': [300, 400]})

# Tahmin edilen yüzey pürüzlülüklerini hesaplama
predicted_surface = model.predict(new_data)

# Tahmin sonuçlarını yazdırma
print("Tahmin Edilen Yüzey Pürüzlülükleri (Ra):", predicted_surface)

#logistik regresyon basit örnek
--------------------------------------------------------------

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# Örnek veri seti
data = pd.DataFrame({
    'Maaş': [40000, 50000, 60000, 80000, 100000, 120000, 150000, 200000],
    'İş_Tatmini': [3, 2, 4, 5, 1, 3, 2, 4],  # 1 (düşük) - 5 (yüksek) arasında
    'İşten_Ayrıldı': [0, 0, 1, 0, 1, 1, 1, 0]  # Hedef değişken
})

# Bağımsız (X) ve bağımlı değişkenler (y)
X = data[['Maaş', 'İş_Tatmini']]
y = data['İşten_Ayrıldı']

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Lojistik Regresyon modeli oluşturma ve eğitme
model = LogisticRegression()
model.fit(X_train, y_train)

# Test seti üzerinde tahmin yapma
y_pred = model.predict(X_test)

# Model performansı değerlendirme
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

# Performans sonuçları
print("Doğruluk Oranı (Accuracy):", round(accuracy, 2))
print("\nSınıflandırma Raporu:\n", classification_report(y_test, y_pred))

# Confusion Matrix Görselleştirme
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Ayrılmadı', 'Ayrıldı'], yticklabels=['Ayrılmadı', 'Ayrıldı'])
plt.xlabel("Tahmin Edilen")
plt.ylabel("Gerçek")
plt.title("Confusion Matrix")
plt.show()

# Kullanıcıdan işçi bilgilerini alma
# Kullanıcıdan işçi bilgilerini alma
print("\nYeni bir işçi verisi için tahmin yapın:")
maas = float(input("İşçinin maaşını girin (TL): "))
is_tatmini = int(input("İşçinin iş tatmini seviyesini girin (1-5): "))

# Yeni veri tahmini
new_data = pd.DataFrame({'Maaş': [maas], 'İş_Tatmini': [is_tatmini]})
prediction = model.predict(new_data)

# Tahmin sonucunu yazdırma
if prediction[0] == 1:
    print("Tahmin: İşçi işten ayrılabilir.")
else:
    print("Tahmin: İşçi işten ayrılmaz.")


#makine mühendisliğinde logistik regresyon kullanımı basit uygulama
--------------------------------------------------------------

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# Örnek veri seti
data = pd.DataFrame({
    'Sıcaklık': [70, 75, 80, 85, 90, 95, 100, 105, 110, 115],  # °C
    'Titreşim': [2.1, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5],  # m/s²
    'Kullanım_Süresi': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50],  # yıl
    'Arıza': [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]  # 1: Arızalı, 0: Arızasız
})

# Bağımsız (X) ve bağımlı (y) değişkenler
X = data[['Sıcaklık', 'Titreşim', 'Kullanım_Süresi']]
y = data['Arıza']

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Lojistik Regresyon modeli oluşturma ve eğitme
model = LogisticRegression()
model.fit(X_train, y_train)

# Tahmin yapma
y_pred = model.predict(X_test)

# Model performansı değerlendirme
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

# Sonuçlar
print("Doğruluk Oranı (Accuracy):", round(accuracy, 2))
print("\nSınıflandırma Raporu:\n", classification_report(y_test, y_pred))

# Confusion Matrix Görselleştirme
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Arızasız', 'Arızalı'], yticklabels=['Arızasız', 'Arızalı'])
plt.xlabel("Tahmin Edilen")
plt.ylabel("Gerçek")
plt.title("Confusion Matrix")
plt.show()

------------------------------------------------------py2x--------------------------------------------------------------
import pandas as pd  #Pandas veri analizi ve veri manipülasyonu için kullanılan bir Python kütüphanesidir.
import numpy as np #NumPy, bilimsel hesaplama için kullanılan bir kütüphanedir.
from sklearn.model_selection import train_test_split #train_test_split: Veri setini eğitim ve test bölümlerine ayıran bir fonksiyondur.
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree #Karar ağacındaki dallanma kurallarını anlaşılır bir şekilde metin olarak gösterir.
from sklearn.metrics import accuracy_score #accuracy_score: Modelin doğruluğunu ölçen bir metrik fonksiyondur.
import matplotlib.pyplot as plt #Matplotlib, Python'da grafik çizmek için kullanılan bir kütüphanedir

# 1. Veri Seti Oluşturma
np.random.seed(42) #Rastgele sayıların her çalıştırmada aynı olması için rastgelelik kontrol altına alınır.
data = pd.DataFrame({ #Bu kod, pandas kullanarak bir DataFrame (tablo) oluşturur. Her sütun, öğrencilerin özelliklerini ve sınıflarını içerir.
    "etüt_saati": np.random.randint(0, 10, 100),  # Çalışılan saat
    "katılım": np.random.randint(60, 100, 100),  # Devamsızlık yüzdesi
    "notlar": np.random.randint(50, 100, 100),  # Önceki notlar
    "durum": np.random.choice([0, 1], size=100)  # Geçti (1) veya Kaldı (0)
})

# Özellikler (X) ve hedef değişkeni (y) ayırma
X = data[["etüt_saati", "katılım", "notlar"]]
y = data["durum"]

# 2. Eğitim ve Test Verisi Bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Karar Ağacı Modeli Oluşturma
model = DecisionTreeClassifier(random_state=42, max_depth=3, min_samples_split=10, criterion="entropy") #entropy yerine gini de kullanılabilir
model.fit(X_train, y_train)

#Gini genellikle daha hızlı çalışır ve çoğu zaman daha iyi sonuçlar verir. Bu nedenle, karar ağaçları için yaygın olarak tercih edilir.Gini, veriyi iki veya daha fazla sınıfa ayırırken, verinin saf olup olmadığını ölçen bir kriterdir. Gini'nin amacı, mümkün olduğunca saf (homojen) alt kümeler oluşturmaktır. Gini saf olmayan veri noktalarının rastgeleliği hakkında bilgi verir. Dallanma sırasında, sınıflar arasındaki karışım ne kadar azsa, Gini değeri o kadar düşer.
#Entropy ise bilgi teorisi tabanlıdır ve daha derinlemesine analiz gerektiğinde kullanılabilir. Bazen daha fazla bilgi sağlar, ancak daha karmaşık ve zaman alıcıdır.
#hem gini hemde ent için 0 a yaklaşmaya çalışırız

# 4. Test Verisi ile Tahmin
y_pred = model.predict(X_test)

# 5. Model Doğruluğunu Hesaplama
accuracy = accuracy_score(y_test, y_pred) #1 değerine yaklaşmaya çalışıyoruz
print("Model Doğruluğu:", round(accuracy, 2))
print(accuracy)
# 6. Karar Ağacının Kurallarını Yazdırma
tree_rules = export_text(model, feature_names=list(X.columns)) #burada karar ağacı kuralları belirleniyor
print("\nKarar Ağacı Kuralları:")
print(tree_rules)

#export_text: Karar ağacındaki dallanma kurallarını ve sınıflandırma işlemlerini okunabilir bir metin formatında gösterir.
#list(X.columns): Modelde kullanılan özelliklerin isimlerini X'ten alır

# 7. Karar Ağacını Görselleştirme
plt.figure(figsize=(15, 8))
plot_tree(model, feature_names=X.columns, class_names=["Fail", "Pass"], filled=True)
plt.title("Karar Ağacı Görselleştirme")
plt.show()

#feature_names=X.columns X = data[["etüt_saati", "katılım", "notlar"]]
#class_names=["Fail", "Pass"] Açıklama: Hedef değişkenin sınıf isimlerini belirtir.
#filled=True  Her düğüm için renkli bir gösterim sağlar, Eğer bir düğümün sınıflar arası ayrımı netse, renk daha yoğun olur. Örneğin, bir düğümde tüm örnekler "Pass" sınıfına aitse, düğüm tamamen yeşil olur.

# 8. Veri Setini Kaydetme
data.to_csv("student_performance.csv", index=False)
print("Veri seti 'student_performance.csv' olarak kaydedildi.")

#NOT=max_depth (Maksimum Derinlik), min_samples_split ((Dallanma için Minimum Örnek Sayısı), criterion gibi parametrelerin doğruluğu nasıl etkilediğini test edin.
--------------------------------------------------------------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Veri Seti Oluşturma
np.random.seed(42)
data = pd.DataFrame({
    "Temperature": np.random.randint(200, 500, 200),  # Üretim sıcaklığı (°C)
    "Pressure": np.random.randint(50, 150, 200),      # Üretim basıncı (Bar)
    "Time": np.random.randint(5, 20, 200),           # Üretim süresi (Dakika)
    "Material_Type": np.random.choice([1, 2], 200),  # Malzeme tipi (1: Çelik, 2: Alüminyum)
    "Quality": np.random.choice([0, 1], 200)         # Kalite (0: Uygun Değil, 1: Uygun)
})

# Özellik ve hedef değişkeni ayırma
X = data[["Temperature", "Pressure", "Time", "Material_Type"]]
y = data["Quality"]

# 2. Eğitim ve Test Verisi Bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Karar Ağacı Modeli Oluşturma
model = DecisionTreeClassifier(random_state=42, max_depth=4)
model.fit(X_train, y_train)

# 4. Test Verisi ile Tahmin
y_pred = model.predict(X_test)

# 5. Model Doğruluğunu Hesaplama
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")
print(accuracy)

# 6. Karar Ağacının Kurallarını Yazdırma
tree_rules = export_text(model, feature_names=list(X.columns))
print("\nKarar Ağacı Kuralları:")
print(tree_rules)

# 7. Karar Ağacını Görselleştirme
plt.figure(figsize=(15, 10))
plot_tree(model, feature_names=X.columns, class_names=["Not Suitable", "Suitable"], filled=True)
plt.title("Karar Ağacı Görselleştirme")
plt.show()
--------------------------------------------------------------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Veri Seti Oluşturma
np.random.seed(42)
data = pd.DataFrame({
    "etüt_saati": np.random.randint(0, 10, 100),  # Çalışma saati
    "katılım": np.random.randint(60, 100, 100),  # Katılım yüzdesi
    "notlar": np.random.randint(50, 100, 100),  # Önceki notlar
    "durum": np.random.choice([0, 1], size=100)  # Geçti (1) veya Kaldı (0)
})

# Özellikler (X) ve hedef değişkeni (y) ayırma
X = data[["etüt_saati", "katılım", "notlar"]]
y = data["durum"]

# 2. Eğitim ve Test Verisi Bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. K-Nearest Neighbors Modeli Oluşturma (k=5)
k = 5
knn_model = KNeighborsClassifier(n_neighbors=k)

# 4. Modeli Eğitme
knn_model.fit(X_train, y_train)

# 5. Test Verisi ile Tahmin
y_pred = knn_model.predict(X_test)

# 6. Model Doğruluğunu Hesaplama
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Doğruluğu (k={k}): {accuracy:.2f}")

# 7. Veri Setini Kaydetme
data.to_csv("student_performance_knn_single_k.csv", index=False)
print("Veri seti 'student_performance_knn_single_k.csv' olarak kaydedildi.")

#burada farklı k değerleri için kodu tekrar çalıştırın ve en yüksek doğruluk oranını vere k değerini bulun
--------------------------------------------------------------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Veri Seti Oluşturma
np.random.seed(42)
data = pd.DataFrame({
    "etüt_saati": np.random.randint(0, 10, 100),  # Çalışma saati
    "katılım": np.random.randint(60, 100, 100),  # Katılım yüzdesi
    "notlar": np.random.randint(50, 100, 100),  # Önceki notlar
    "durum": np.random.choice([0, 1], size=100)  # Geçti (1) veya Kaldı (0)
})

# Özellikler (X) ve hedef değişkeni (y) ayırma
X = data[["etüt_saati", "katılım", "notlar"]]
y = data["durum"]

# 2. Eğitim ve Test Verisi Bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. K-Nearest Neighbors Modeli Oluşturma
knn_model = KNeighborsClassifier(n_neighbors=5)

# 4. Modeli Eğitme
knn_model.fit(X_train, y_train)

# 5. Test Verisi ile Tahmin
y_pred = knn_model.predict(X_test)

# 6. Model Doğruluğunu Hesaplama
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Doğruluğu: {accuracy:.2f}")

# 7. KNN için K Değeri ile Deneme (farklı k değerlerinin doğrulukları)
k_values = range(1, 21)
accuracy_list = []

for k in k_values:
    knn_model = KNeighborsClassifier(n_neighbors=k)
    knn_model.fit(X_train, y_train)
    y_pred = knn_model.predict(X_test)
    accuracy_list.append(accuracy_score(y_test, y_pred))

# 8. K Değerinin Doğruluk Üzerindeki Etkisini Görselleştirme
plt.figure(figsize=(8, 6))
plt.plot(k_values, accuracy_list, marker='o')
plt.title("K Değeri ve Model Doğruluğu")
plt.xlabel("K Değeri")
plt.ylabel("Doğruluk")
plt.grid(True)
plt.show()

# 9. Veri Setini Kaydetme
data.to_csv("student_performance_knn.csv", index=False, encoding="utf-16")
print("Veri seti 'student_performance_knn.csv' olarak kaydedildi.")
 --------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Basit Veri Seti
# Boy (cm), Kilo (kg) ve Cinsiyet (0 = Kadın, 1 = Erkek)
data = pd.DataFrame({
    "boy": [150, 160, 170, 180, 155, 165, 175, 185],
    "kilo": [50, 60, 70, 80, 55, 65, 75, 85],
    "cinsiyet": [0, 0, 1, 1, 0, 0, 1, 1]  # Kadın (0), Erkek (1)
})

# Özellikler (X) ve hedef değişkeni (y) ayırma
X = data[["boy", "kilo"]]  # Boy ve Kilo
y = data["cinsiyet"]  # Cinsiyet

# 2. Eğitim ve Test Verisi Bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# 3. KNN Modeli Oluşturma (k=3)
knn = KNeighborsClassifier(n_neighbors=3)

# 4. Modeli Eğitim Verisiyle Eğitme
knn.fit(X_train, y_train)

# 5. Test Verisi ile Tahmin Yapma
y_pred = knn.predict(X_test)

# 6. Modelin Doğruluğunu Hesaplama
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Doğruluğu: {accuracy * 100:.2f}%")

# 7. Veriyi Görselleştirme (Boy vs Kilo)
plt.figure(figsize=(8, 6))
plt.scatter(X["boy"], X["kilo"], c=y, cmap=plt.cm.RdYlBu, s=100) #cmap=plt.cm.RdYlBu kırmızıdan maviye doğru s ise noktaların boyutunu belirler
plt.title("Boy ve Kilo ile Cinsiyet Sınıflandırması")
plt.xlabel("Boy (cm)")
plt.ylabel("Kilo (kg)")
plt.show()
--------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Örnek veri seti oluşturma
# Bor kaplama oranı (%), Sertlik (HV)
data = {
    'bor_kaplama_orani': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
    'sertlik': [200, 220, 240, 260, 290, 320, 350, 380, 400, 420]
}

df = pd.DataFrame(data)

# Özellikler ve hedef değişken
X = df[['bor_kaplama_orani']].values  # Girdi: Bor kaplama oranı
y = df['sertlik'].values  # Çıktı: Sertlik

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# KNN modelini tanımlama ve eğitme
knn = KNeighborsRegressor(n_neighbors=3)  # 3 komşulu KNN
knn.fit(X_train, y_train)

# Test seti üzerinde tahmin yapma
y_pred = knn.predict(X_test)

# Model performansı değerlendirme
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"R² Score: {r2:.2f}")

# Tahmin edilen ve gerçek değerleri görselleştirme
plt.figure(figsize=(8, 6))
plt.scatter(X_test, y_test, color='blue', label='Gerçek Değerler')
plt.scatter(X_test, y_pred, color='red', label='Tahminler', marker='x')
plt.plot(X, knn.predict(X), color='green', linestyle='--', label='Model Eğrisi')
plt.xlabel('Bor Kaplama Oranı (%)')
plt.ylabel('Sertlik (HV)')
plt.title('KNN ile Bor Kaplama Oranı ve Sertlik İlişkisi')
plt.legend()
plt.grid(True)
plt.show()

# Yeni bir veri için tahmin yapma
yeni_veri = np.array([[37]])  # Örneğin, %37 bor kaplama oranı
tahmin = knn.predict(yeni_veri)
print(f"%37 Bor Kaplama Oranı için Tahmin Edilen Sertlik: {tahmin[0]:.2f} HV")
--------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow

# -----------------------------
# YSA ile Makine Mühendisliği Problemi: Malzeme Sertliği Tahmini
# -----------------------------
# Veri seti oluşturma
# Girdi: Çekme mukavemeti (MPa), Akma mukavemeti (MPa), Elastik Modül (GPa)
# Çıktı: Sertlik (HV)
data_mechanical = {
    'cekme_mukavemeti': [400, 450, 500, 550, 600, 650, 700, 750, 800, 850],
    'akma_mukavemeti': [250, 280, 310, 340, 370, 400, 430, 460, 490, 520],
    'elastik_modul': [200, 210, 215, 220, 225, 230, 235, 240, 245, 250],
    'sertlik': [150, 160, 170, 180, 190, 200, 210, 220, 230, 240]
}

df_mechanical = pd.DataFrame(data_mechanical)

# Özellikler ve hedef değişken
X_mech = df_mechanical[['cekme_mukavemeti', 'akma_mukavemeti', 'elastik_modul']].values
y_mech = df_mechanical['sertlik'].values

# Veriyi eğitim ve test setlerine ayırma
X_train_mech, X_test_mech, y_train_mech, y_test_mech = train_test_split(X_mech, y_mech, test_size=0.2, random_state=42)

# Verileri ölçeklendirme
scaler_mech = StandardScaler()
X_train_mech_scaled = scaler_mech.fit_transform(X_train_mech)
X_test_mech_scaled = scaler_mech.transform(X_test_mech)

# YSA modelini oluşturma
model_mech = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(X_train_mech_scaled.shape[1],)),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(1)
])

# Modeli derleme
model_mech.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Modeli eğitme
history_mech = model_mech.fit(X_train_mech_scaled, y_train_mech, epochs=100, validation_split=0.2, verbose=0)

# Test seti üzerinde tahmin yapma
y_pred_mech = model_mech.predict(X_test_mech_scaled).flatten()

# Performans değerlendirme
mse_mech = mean_squared_error(y_test_mech, y_pred_mech)
print(f"YSA Modeli Mean Squared Error (MSE): {mse_mech:.2f}")

# Eğitim ve doğrulama kayıplarını görselleştirme
plt.figure(figsize=(8, 6))
plt.plot(history_mech.history['loss'], label='Eğitim Kaybı')
plt.plot(history_mech.history['val_loss'], label='Doğrulama Kaybı')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Eğitim ve Doğrulama Kaybı')
plt.legend()
plt.grid(True)
plt.show()

# Tahmin edilen ve gerçek değerleri görselleştirme
plt.figure(figsize=(8, 6))
plt.scatter(range(len(y_test_mech)), y_test_mech, color='blue', label='Gerçek Değerler')
plt.scatter(range(len(y_test_mech)), y_pred_mech, color='red', label='Tahminler', marker='x')
plt.xlabel('Veri Noktası')
plt.ylabel('Sertlik (HV)')
plt.title('Gerçek ve Tahmin Edilen Sertlik Değerleri')
plt.legend()
plt.grid(True)
plt.show()

# Yeni bir veri için tahmin yapma
yeni_veri_mech = np.array([[720, 460, 238]])  # Çekme mukavemeti: 720 MPa, Akma mukavemeti: 460 MPa, Elastik Modül: 238 GPa
yeni_veri_mech_scaled = scaler_mech.transform(yeni_veri_mech)
tahmin_mech = model_mech.predict(yeni_veri_mech_scaled).flatten()
print(f"Yeni Malzeme için Tahmin Edilen Sertlik: {tahmin_mech[0]:.2f} HV") 
--------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Örnek veri seti oluşturma
# Bor kaplama oranı (%), Sertlik (HV)
data = {
    'yoğunluk': [7.7,7.5,1.3,2.5,2.6,7.7],
    'sertlik': [200,250,150,300,350,400],
    'malzeme_turu': [1,1,2,3,3,1]
}

df = pd.DataFrame(data)

# Özellikler ve hedef değişken
X = df[['yoğunluk', 'sertlik']].values  # Girdi: Bor kaplama oranı
y = df['malzeme_turu'].values  # Çıktı: Sertlik

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# KNN modelini tanımlama ve eğitme
knn = KNeighborsRegressor(n_neighbors=3)  # 3 komşulu KNN
knn.fit(X_train, y_train)

# Test seti üzerinde tahmin yapma
y_pred = knn.predict(X_test)

# Model performansı değerlendirme
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"R² Score: {r2:.2f}")

# Tahmin edilen ve gerçek değerleri görselleştirme
plt.figure(figsize=(8, 6))
plt.scatter(X_test, y_test, color='blue', label='Gerçek Değerler')
plt.scatter(X_test, y_pred, color='red', label='Tahminler', marker='x')
plt.plot(X, knn.predict(X), color='green', linestyle='--', label='Model Eğrisi')
plt.xlabel('Bor Kaplama Oranı (%)')
plt.ylabel('Sertlik (HV)')
plt.title('KNN ile Bor Kaplama Oranı ve Sertlik İlişkisi')
plt.legend()
plt.grid(True)
plt.show()

# Yeni bir veri için tahmin yapma
yeni_veri = np.array([[37]])  # Örneğin, %37 bor kaplama oranı
tahmin = knn.predict(yeni_veri)
print(f"%37 Bor Kaplama Oranı için Tahmin Edilen Sertlik: {tahmin[0]:.2f} HV")
--------------------------------------------------------------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
import matplotlib.pyplot as plt

# Rastgele veri oluşturma
np.random.seed(42)
data = {
    "Work_Hours": np.random.randint(20, 61, 1000),
    "Experience": np.random.randint(0, 31, 1000),
    "Projects": np.random.randint(0, 11, 1000),
    "Education_Level": np.random.randint(1, 5, 1000),
}

# Performansı belirleyen bir fonksiyon
def calculate_performance(row):
    score = (row["Work_Hours"] * 0.3) + (row["Experience"] * 0.4) + (row["Projects"] * 0.2) + (row["Education_Level"] * 5)
    return 1 if score > 50 else 0

# Performansı ekleyerek veri çerçevesi oluşturma
df = pd.DataFrame(data)
df["Performance"] = df.apply(calculate_performance, axis=1)

# Özellikler ve hedef değişkeni ayırma
X = df[["Work_Hours", "Experience", "Projects", "Education_Level"]]
y = df["Performance"]

# Eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Karar ağacı modeli oluşturma
model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Model performansı
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2f}")

# Karar ağacı görselleştirme
plt.figure(figsize=(20, 10))
tree.plot_tree(model, feature_names=X.columns, class_names=["Low", "High"], filled=True, rounded=True)
plt.show()

# Yeni bir çalışanın performans tahmini
new_employee = [[45, 10, 5, 3]]  # Örnek: 45 saat çalışıyor, 10 yıl deneyim, 5 proje, yüksek lisans
prediction = model.predict(new_employee)
print("Predicted Performance:", "High" if prediction[0] == 1 else "Low")
--------------------------------------------------------------

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

# Veri setini oluşturma
data = {
    'Sertlik': [200, 250, 150, 300, 350, 400],
    'Yoğunluk': [7.8, 7.5, 1.3, 2.5, 2.6, 7.7],
    'Malzeme Türü': ['Metal', 'Metal', 'Plastik', 'Seramik', 'Seramik', 'Metal']
}
df = pd.DataFrame(data)

# Etiketleri sayısal değerlere dönüştürme
label_encoder = LabelEncoder()
df['Malzeme Türü'] = label_encoder.fit_transform(df['Malzeme Türü'])

# Özellikler ve hedef değişkeni ayırma
X = df[['Sertlik', 'Yoğunluk']]
y = df['Malzeme Türü']

# Eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# KNN modelini oluşturma ve eğitme
knn = KNeighborsClassifier(n_neighbors=3)  # K değerini 3 olarak belirledik
knn.fit(X_train, y_train)

# Modelin doğruluğunu ölçme
accuracy = knn.score(X_test, y_test)
print(f"Model Doğruluğu: {accuracy:.2f}")

# Yeni bir malzeme tahmini
new_material = [[275, 7.4]]  # Sertlik: 275, Yoğunluk: 7.4
predicted_class = knn.predict(new_material)
predicted_label = label_encoder.inverse_transform(predicted_class)
print(f"Tahmin Edilen Malzeme Türü: {predicted_label[0]}")
--------------------------------------------------------------
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

# Örnek veri seti oluşturma
data = {
    "Yaş": [25, 30, 45, 50, 22, 35, 40, 60],
    "Yıllık Gelir (bin $)": [50, 60, 80, 100, 40, 70, 90, 120],
    "Teklif": ["Teklif A", "Teklif A", "Teklif B", "Teklif B", "Teklif A", "Teklif A", "Teklif B", "Teklif B"]
}
df = pd.DataFrame(data)

# Hedef değişkeni sayısal değerlere dönüştürme
label_encoder = LabelEncoder()
df["Teklif"] = label_encoder.fit_transform(df["Teklif"])  # 'Teklif A' -> 0, 'Teklif B' -> 1

# Özellikler (X) ve hedef değişken (y) ayırma
X = df[["Yaş", "Yıllık Gelir (bin $)"]]
y = df["Teklif"]

# Eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# KNN modeli oluşturma ve eğitme
knn = KNeighborsClassifier(n_neighbors=3)  # K değerini 3 seçtik
knn.fit(X_train, y_train)

# Model doğruluğunu hesaplama
accuracy = knn.score(X_test, y_test)
print(f"Model Doğruluğu: {accuracy:.2f}")

# Yeni müşteri tahmini
new_customer = [[28, 65]]  # Yaş: 28, Yıllık Gelir: 65 bin $
predicted_class = knn.predict(new_customer)
predicted_offer = label_encoder.inverse_transform(predicted_class)
print(f"Yeni müşteriye önerilen teklif: {predicted_offer[0]}")    
    """


