requirements = [
    'aiofiles==24.1.0',
    'aiohttp==3.11.11',
    'aiosqlite==0.20.0',
    'yt-dlp==2025.1.26',
]


if __name__ == '__main__':
    from setuptools import setup, find_packages
    from src.tubefeed import APP_VERSION

    with open('README.md', 'r', encoding='utf-8') as readme_file:
        description = 'Most of the links in this description will only work if you view the [README.md](https://gitlab.com/troebs/tubefeed) on GitLab.\n\n'
        description += readme_file.read()

    setup(
        name='tubefeed',
        version=APP_VERSION,
        author='Eric Tröbs',
        author_email='eric.troebs@tu-ilmenau.de',
        description='seamlessly integrate YouTube with Audiobookshelf',
        long_description=description,
        long_description_content_type='text/markdown',
        url='https://gitlab.com/troebs/tubefeed',
        project_urls={
            'Bug Tracker': 'https://gitlab.com/troebs/tubefeed/-/issues',
        },
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        python_requires='>=3.10',
        install_requires=requirements
    )
