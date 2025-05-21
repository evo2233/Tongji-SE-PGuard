from router import detect
model_type = "Grape"
image_path = "C:/PGuard/yolov8/ultralytics-main/Grape/Grape_test2_409.jpg"
try:
    results = detect(model_type,image_path)
    for cls, conf in results:
        print(f"类别: {cls}, 置信度: {conf:.2f}")
except Exception as e:
    print(f"检测过程中出现错误: {e}")