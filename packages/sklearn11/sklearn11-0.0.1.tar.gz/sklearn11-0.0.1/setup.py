from setuptools import setup, find_packages

setup(
    name="sklearn11",  # Paketinizin adı
    version="0.0.1",  # Sürüm numarası
    author="olcay",
    author_email="olcay.aydn25@gmail.com",
    description="100 alcaz",
    long_description=open(r"C:\Users\PC\Desktop\sklearn11\README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ozbere31/sklearn11",  # GitHub repo bağlantısı
    packages=find_packages(where="C:\\Users\\PC\\Desktop\\sklearn11"),  # Bu satır otomatik olarak paketleri bulur
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
