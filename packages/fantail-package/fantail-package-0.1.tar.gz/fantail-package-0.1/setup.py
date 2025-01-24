from setuptools import setup, find_packages

setup(
    name='fantail-package',
    version='0.1',
    packages=find_packages(),  # Finds the package automatically
    install_requires=[
        # List of dependencies, e.g., 'requests', if any
    ],
    entry_points={
        'console_scripts': [
            'run-my-script=fantail_package.script:run_script',  # if you want to call the script from the CLI
        ],
    },
    # You can include other metadata like description, author, etc.
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)

