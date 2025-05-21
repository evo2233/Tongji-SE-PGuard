from ultralytics import YOLO

model=YOLO('Potato.pt')

model.predict('Potato\\0_402.jpg', save=True)
model.predict('Potato\\0_403.jpg', save=True)
model.predict('Potato\\0_404.jpg', save=True)
model.predict('Potato\\0_405.jpg', save=True)
model.predict('Potato\\0_406.jpg', save=True)
model.predict('Potato\\0_407.jpg', save=True)

model.predict('Potato\\1_414.jpg', save=True)
model.predict('Potato\\1_415.jpg', save=True)
model.predict('Potato\\1_416.jpg', save=True)
model.predict('Potato\\1_417.jpg', save=True)
model.predict('Potato\\1_418.jpg', save=True)
model.predict('Potato\\1_419.jpg', save=True)

model.predict('Potato\\2_455.jpg', save=True)
model.predict('Potato\\2_456.jpg', save=True)
model.predict('Potato\\2_457.jpg', save=True)
model.predict('Potato\\2_458.jpg', save=True)
model.predict('Potato\\2_459.jpg', save=True)
model.predict('Potato\\2_460.jpg', save=True)
