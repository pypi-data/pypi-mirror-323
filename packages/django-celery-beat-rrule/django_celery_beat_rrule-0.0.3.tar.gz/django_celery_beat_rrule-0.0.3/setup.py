from setuptools import setup, find_packages

setup(
    use_scm_version=True,
    packages=find_packages(include=["django_celery_beat_rrule"]),
    setup_requires=["setuptools_scm"],
)
