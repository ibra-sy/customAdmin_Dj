"""
Setup configuration for django-admin-custom package
"""
from setuptools import setup, find_packages
import os

# Lire le README pour la description longue
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='django-admin-custom',
    version='0.1.0',
    description='Package Django réutilisable pour personnaliser l\'interface d\'administration avec graphiques dynamiques, grilles de données et thèmes modernes',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Agile Custom Admin',
    author_email='',
    url='https://github.com/VOTRE_USERNAME/django-admin-custom',
    packages=find_packages(exclude=['tests', 'tests.*', 'sandbox', 'sandbox.*']),
    include_package_data=True,
    install_requires=[
        'Django>=4.2,<6.0',
    ],
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='django admin customization charts grids themes',
    zip_safe=False,
)
