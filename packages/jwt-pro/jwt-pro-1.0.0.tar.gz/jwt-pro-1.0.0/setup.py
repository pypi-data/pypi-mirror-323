from setuptools import setup, find_packages

setup(
    name="jwt-pro",
    version="1.0.0",
    author="krishna Tadi",
    description="JWT Pro is a package for generating and verifying JSON Web Tokens (JWTs). It supports AES encryption and HMAC signatures, enabling secure user authentication and data transmission. The package is highly customizable, with options for adding encryption, defining headers and payloads, and validating tokens.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/krishnatadi/jwt-pro-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "alluuid==0.1.0",
        "cryptography==38.0.0"
    ],
    keywords='"JWT", "JWT PRO", "JWT-PRO", "authentication", "security", "token", "AES", "encryption", "HMAC", "JWT verification", "Python security", "cryptography", "secure tokens", "token verification", "token generation"',
    project_urls={
    'Documentation': 'https://github.com/krishnatadi/jwt-pro-python#readme',
    'Source': 'https://github.com/krishnatadi/jwt-pro-python',
    'Issue Tracker': 'https://github.com/krishnatadi/jwt-pro-python/issues',
    },
    license='MIT'
)
