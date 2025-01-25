from setuptools import setup, find_packages

setup(
    name='autodrome',
    version='0.1.0',
    description='Framework and OpenAI Gym environment for development of self-driving cars',
    author='Vojta Molda',
    author_email='vojta.molda@gmail.com',
    url='https://github.com/vojtamolda/autodrome',
    packages=find_packages(),
    install_requires=[
        'gym',
        'numpy',
        'opencv-python',
        'pyzmq',
        'pycapnp',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='self-driving car simulation reinforcement-learning',
    python_requires='>=3.7',
)
