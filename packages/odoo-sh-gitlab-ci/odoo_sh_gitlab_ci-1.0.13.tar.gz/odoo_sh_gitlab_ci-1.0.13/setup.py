from setuptools import setup, find_packages

setup(
    name="odoo_sh_gitlab_ci",
    version="1.0.13",
    description="Simplify and automate Odoo.sh deployment using GitLab and GitHub.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jarsa",
    author_email="info@jarsa.com",
    url="https://git.jarsa.com.com/Jarsa/odoo-sh-gitlab-ci",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "odoo_sh_deploy=odoo_sh_gitlab_ci.deploy:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
