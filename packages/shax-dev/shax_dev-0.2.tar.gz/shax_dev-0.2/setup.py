from setuptools import setup, find_packages

setup(
    name='shax_dev',  # Loyihangizning nomi
    version='0.2',  # Loyihangizning versiyasi
    packages=find_packages(),  # Loyihaning barcha paketlarini avtomatik topish
    include_package_data=True,  # Statik fayllarni ham qo'shish
    install_requires=[  # Loyihada ishlatadigan boshqa paketlar
        'asgiref==3.8.1',
        'certifi==2024.8.30',
        'charset-normalizer==3.4.0',
        'Django==5.1.2',
        'django-ckeditor==6.7.2',
        'django-cors-headers==4.5.0',
        'django-js-asset==2.2.0',
        'django-unfold==0.43.0',
        'djangorestframework==3.15.2',
        'drf-yasg==1.21.8',
        'idna==3.10',
        'inflection==0.5.1',
        'packaging==24.2',
        'pillow==11.0.0',
        'pytz==2024.2',
        'PyYAML==6.0.2',
        'requests==2.32.3',
        'setuptools==70.1.1',
        'soupsieve==2.6',
        'sqlparse==0.5.1',
        'tzdata==2024.2',
        'uritemplate==4.1.1',
        'urllib3==2.2.3',
        'gunicorn',  # Gunicorn serveri
        'psycopg2',  # PostgreSQL bilan ishlash uchun
    ],
    description="Django Base Setup",  # Loyihaning qisqacha tavsifi
    author='Bobur Gulomov',  # Muallifning ismi
    author_email='farmusic@inbox.ru',  # Muallifning email manzili
    url='https://github.com/Bobur2828/django_base.git',  # Loyihangizning GitHub URL manzili
    classifiers=[  # Loyihani qanday kategoriyaga kiritishni belgilash
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={  # Django loyihasi uchun boshlang'ich faylni ko'rsatish
        'console_scripts': [
            # Bu qismni Django loyihasining bosh fayli bilan ishlatish shart emas
        ],
    },
)
