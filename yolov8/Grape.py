from ultralytics import YOLO


model=YOLO('yolov8n.pt')

model.train(data='yolo_bvn.yaml',workers=0,epochs=30,batch=16)

model.val()