from setuptools import setup, find_packages  
  
setup(  
    name='sentimentAnalisis1.1',  # Nama library  
    version='0.1.1',  # Versi library  
    description='Library untuk analisis sentimen menggunakan SVM dan TF-IDF',  # Deskripsi singkat  
    long_description=open('README.md').read(),  # Deskripsi panjang dari README.md  
    long_description_content_type='text/markdown',  # Tipe konten  
    author='Ardyva Sandy Nugraha',  # Nama penulis  
    author_email='sandysan.asn2003@gmail.com',  # Email penulis  
    url='https://github.com/SandyNugraha6/sentimentAnalyzer',  # URL repositori  
    packages=find_packages(),  # Mencari semua package  
    install_requires=[  # Daftar dependensi  
        'pandas',  
        'scikit-learn',  
        'matplotlib',  
        'seaborn',  
        'imbalanced-learn'  
    ],  
    classifiers=[  # Klasifikasi untuk PyPI  
        'Programming Language :: Python :: 3',  
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',  
    ],  
    python_requires='>=3.6',  # Versi Python yang dibutuhkan  
)  
