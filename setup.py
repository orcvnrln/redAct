"""
VibeShield Setup
Audit motoru və desktop app üçün quraşdırma
"""

from setuptools import setup, find_packages

setup(
    name="vibeshield",
    version="1.0.0",
    description="Deterministik DevSecOps Audit və Gate Sistemi",
    author="VibeShield Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Desktop App
        "customtkinter>=5.2.0",
        "Pillow>=10.0.0",
        
        # Audit Engine (minimal dependencies)
        # Regex əsaslı - xarici alət lazım deyil
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'vibeshield-audit=audit.run_audit:main',
            'vibeshield-gate=desktop_app.gate:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
