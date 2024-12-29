import os
import re
import uuid
import itertools
import requests
import backoff
import base64

from typing import Any
from contextlib import suppress

from storage3.utils import StorageException
from datetime import timedelta, datetime
from itertools import islice
from dependency_injector.wiring import Provide, inject
from openai import OpenAI, APIStatusError
from supabase import create_client
from typing import Generator  

MAX_FRAMES_PER_REQUEST = 50
TIME_FORMAT = "%H:%M:%S.%f"
SHORT_TIME_FORMAT = "%H:%M:%S"

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

IMAGES_BUCKET_NAME = 'production'
IMAGES_FOLDER_NAME = 'images'

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# with suppress(StorageException):
#     supabase.storage.create_bucket(IMAGES_BUCKET_NAME)
