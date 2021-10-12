import hashlib

def calc_hash(str_in: str):
  return hashlib.md5(str_in.encode('utf-8')).hexdigest()