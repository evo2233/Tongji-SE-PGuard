from ultralytics import YOLO


model=YOLO('yolov8n.pt')

model.train(data='yolo_bvn1.yaml',workers=0,epochs=30,batch=16)

