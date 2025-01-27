import pandas as pd  
from sklearn.model_selection import train_test_split  
from sklearn.feature_extraction.text import TfidfVectorizer  
from sklearn.svm import SVC  
from sklearn.metrics import confusion_matrix, classification_report  
import matplotlib.pyplot as plt  
import seaborn as sns  
from imblearn.over_sampling import SMOTE  
  
def main():  
    # 1. Membaca dataset dari file CSV  
    file_path = r'D:\AMIKOM\KULIAH 7\SKRIPSI\Dataset\Final\final_dataset.csv'  # Ganti dengan path file Anda  
    df = pd.read_csv(file_path)  
  
    # Menampilkan beberapa baris data  
    print("Data Awal:")  
    print(df.head())  
  
    # 2. Menampilkan jumlah masing-masing kelas sentimen  
    sentiment_counts = df['sentimen'].value_counts()  
    print("\nJumlah Sentimen:")  
    print(sentiment_counts)  
  
    # 3. Menggunakan TfidfVectorizer untuk ekstraksi fitur  
    tfidf_vectorizer = TfidfVectorizer(stop_words=None, max_features=1000)  
    X_tfidf = tfidf_vectorizer.fit_transform(df['tokenized_text'])  
  
    # 4. Membagi data menjadi data pelatihan dan pengujian  
    X_train, X_test, y_train, y_test = train_test_split(X_tfidf, df['sentimen'], test_size=0.3, random_state=42)  
  
    # 5. Menerapkan SMOTE untuk mengatasi ketidakseimbangan kelas  
    smote = SMOTE(random_state=42)  
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)  
  
    # Menampilkan jumlah kelas setelah SMOTE  
    print("\nJumlah Sentimen Setelah SMOTE:")  
    print(pd.Series(y_train_resampled).value_counts())  
  
    # 6. Melatih model SVM  
    svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)  
    svm_model.fit(X_train_resampled, y_train_resampled)  
  
    # 7. Melakukan prediksi pada data pengujian  
    y_pred = svm_model.predict(X_test)  
  
    # 8. Menghitung dan menampilkan confusion matrix dan classification report  
    conf_matrix = confusion_matrix(y_test, y_pred)  
  
    # Menampilkan confusion matrix  
    print("\nConfusion Matrix:")  
    print(conf_matrix)  
  
    # Visualisasi confusion matrix menggunakan heatmap  
    plt.figure(figsize=(8, 6))  
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['negatif', 'netral', 'positif'], yticklabels=['negatif', 'netral', 'positif'])  
    plt.xlabel('Prediksi')  
    plt.ylabel('Aktual')  
    plt.title('Confusion Matrix')  
    plt.show()  
  
    # Menampilkan classification report  
    print("\nClassification Report:")  
    print(classification_report(y_test, y_pred, target_names=['negatif', 'netral', 'positif']))  
  
if __name__ == "__main__":  
    main()  
