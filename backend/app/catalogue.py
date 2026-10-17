"""Temporary course visibility; hidden records and the mastery plan are retained."""
import os


def udemy_only():
    return os.getenv('ACADEMY_UDEMY_ONLY', '1') != '0'
