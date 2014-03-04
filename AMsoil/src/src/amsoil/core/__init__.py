def serviceinterface(func):
  func._serviceinterface = True
  return func
