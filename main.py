import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# 加载自定义模型
model = YOLO("best.pt")

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def decode_image(base64_string):
    img_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_data))
    return image

def draw_boxes(image, boxes, confidences):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("test.ttf", 15)  # Load custom font with size 12px

    for i in range(len(boxes)):
        x1, y1, x2, y2 = boxes[i]
        conf = confidences[i]

        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        text = f"{conf * 100:.1f}%"  # Format as percentage
        padding = 10  # Adjust this value as needed

        # Calculate text size
        text_bbox = draw.textbbox((x1, y1 - 10), text, font=font)  # Get bounding box for text
        text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

        draw.rectangle([x1, y1 - text_size[1] - padding, x1 + text_size[0], y1], fill="red")
        draw.text((x1, y1 - text_size[1]- padding), text, fill="white", font=font)

    return image

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    base64_image = data['image']
    img = decode_image(base64_image)

    # 对图片进行目标检测
    results = model(img)  # 传递Pillow图像对象
    class_names = model.names  # 获取类别名称

    boxes = results[0].boxes.xyxy.numpy()  # 获取检测框坐标
    confidences = results[0].boxes.conf.numpy().tolist()  # 获取置信度，并转换为列表
    classes = results[0].boxes.cls.numpy()  # 获取类别

    img = draw_boxes(img, boxes, confidences)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')

    # 将字节流的内容转换为Base64字符串
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    # 返回Base64字符串和置信度作为JSON响应
    return jsonify({
        'image': img_base64,
        'confidences': confidences  # 返回置信度列表
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
