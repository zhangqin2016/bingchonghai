import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# 默认模型路径列表
default_model_paths = ["heibanbing_best.pt", "junhebing_best.pt","shuangmeibing_best.pt"]  # List of models

# 加载模型的函数
def load_models(model_names):
    models = {}
    for model_name in model_names:
        try:
            models[model_name] = YOLO(model_name)
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            models[model_name] = None
    return models

# 初始化多个模型
models = load_models(default_model_paths)

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def decode_image(base64_string):
    img_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_data))
    return image

def draw_boxes(image, boxes, confidences, model_name, color="red"):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("test.ttf", 15)  # Load custom font with size 15px

    for i in range(len(boxes)):
        x1, y1, x2, y2 = boxes[i]
        conf = confidences[i]

        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        text = f"{model_name}: {conf * 100:.1f}%"  # Format as percentage, and add model name
        padding = 10  # Adjust this value as needed

        # Calculate text size
        text_bbox = draw.textbbox((x1, y1 - 10), text, font=font)  # Get bounding box for text
        text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

        draw.rectangle([x1, y1 - text_size[1] - padding, x1 + text_size[0], y1], fill=color)
        draw.text((x1, y1 - text_size[1] - padding), text, fill="white", font=font)

    return image

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    # 获取请求中的模型名称列表
    model_names = data.get('model_names', default_model_paths)

    # 加载多个模型（如果路径发生变化）
    global models
    models = load_models(model_names)

    if 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    base64_image = data['image']
    img = decode_image(base64_image)

    all_boxes = []
    all_confidences = []
    all_labels = []  # Keep track of which model detected which box
    colors = ["red", "green", "blue", "yellow", "purple"]  # Colors for each model's bounding boxes
    color_idx = 0

    for model_name, model in models.items():
        if model:
            # 对每个模型进行目标检测
            results = model(img)  # 传递Pillow图像对象
            boxes = results[0].boxes.xyxy.numpy()  # 获取检测框坐标
            confidences = results[0].boxes.conf.numpy().tolist()  # 获取置信度，并转换为列表
            # Draw boxes for the current model on the image
            img = draw_boxes(img, boxes, confidences, model_name=model_name, color=colors[color_idx % len(colors)])
            all_boxes.extend(boxes)
            all_confidences.extend(confidences)
            all_labels.extend([model_name] * len(boxes))  # Assign model name to each box
            color_idx += 1

    # Convert the final image with all detections back to Base64
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # 返回Base64字符串和所有模型的汇总结果
    return jsonify({
        'image': img_base64,
        'boxes': all_boxes,
        'confidences': all_confidences,
        'labels': all_labels  # 现在包括每个框框属于哪个模型的名称
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
