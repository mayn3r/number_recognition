import cv2
import re
import os
import uuid
import numpy as np
import pytesseract

from loguru import logger

# Инициализация Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Parser:
    def create_plate_mask(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        img[:,:,0] = cv2.equalizeHist(img[:,:,0])
        img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR)
        
        # Конвертация в HSV цветовое пространство
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Маска для белого фона
        lower_white = np.array([0, 0, 170])
        upper_white = np.array([180, 50, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        logger.debug("Создана маска для белого фона")
        
        # Маска для желтого фона
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        logger.debug("Создана маска для желтого фона")
        
        # Маска для синего текста
        lower_blue = np.array([90, 80, 80])
        upper_blue = np.array([120, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        logger.debug("Создана маска для синего фона")
        
        combined_mask = cv2.bitwise_or(mask_white, mask_yellow)
        combined_mask = cv2.bitwise_or(combined_mask, mask_blue)
        logger.debug("Маски скомбинированы")
        
        # Морфологические операции для улучшения маски
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        return combined_mask

    def find_license_plate(self, img_path):
        img = cv2.imread(img_path)
        
        if img is None:
            return None
        
        # Создаем маску
        mask = self.create_plate_mask(img)
        
        # Находим контуры
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Фильтруем контуры по размеру и пропорциям
        plates = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / h
            
            # Пропорции российских номеров (стандарт: 520×112 мм ~ 4.64)
            if 3.5 < aspect_ratio < 6 and w > 100 and h > 20:
                plates.append((x, y, w, h))
        
        return plates


    def preprocess(self, im_path: str):
        if not os.path.isdir("src/images/processed"):
            os.mkdir("src/images/processed")
            logger.info("Создана дирректория для сохранения обработанных фотографий")
        
        plates = self.find_license_plate(img_path)
        plate_imgs = []
        
        if plates:
            img = cv2.imread(img_path)
            k = 0
            for (x, y, w, h) in plates:
                k += 1
                # Рисуем прямоугольник вокруг номера
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Вырезаем область номера
                plate_img = img[y:y+h, x:x+w]
                # plate_img = cv2.threshold(plate_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                # plate_img = cv2.medianBlur(plate_img, 3)
                img_name = "%d-%s" % (k+1, uuid.uuid4().hex)
                cv2.imwrite(f"src/images/processed/{img_name}.jpg", plate_img)
                
                plate_imgs.append(plate_img)
            
            cv2.imshow("Detected Plates", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Номера не обнаружены")
        return self.recognize_plate(plate_imgs)
    
    
    def recognize_plate(self, imgs: list):
        
        for img in imgs:
        
            # Настройки Tesseract для российских номеров
            config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABEKMHOPCTYXАВЕКМНОРСТУХ0123456789'
            
            # Распознавание текста
            text = pytesseract.image_to_string(img, lang='rus+eng', config=config)
            
            # Постобработка текста
            text = ''.join(e for e in text if e.isalnum())
        
            number = text.upper()
            # print(number)
            if re.search(r"[ABEKMHOPCTYXАВЕКМНОРСТУХ0123456789]{1}[0-9O]{3}[ABEKMHOPCTYXАВЕКМНОРСТУХ0123456789]{2}[0-9]{1,3}", number):
                return number
        else:
            return "Номер не распознан!"

# Пример использования
if __name__ == "__main__":
    p = Parser()
        
    img_path = 'src/images/4.jpg'

    data = p.preprocess(img_path)
    print("Номер распознан:", data.strip())