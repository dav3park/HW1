from fastapi import FastAPI, UploadFile, File, HTTPException
from deepface import DeepFace
import cv2
import numpy as np

app = FastAPI(title="Face Recognition ML API")

@app.get("/")
def read_root(): 
    return {"status": "ok", "message": "ML API Server is ready for face recognition!"}

@app.post("/analyze")
async def analyze_face(file: UploadFile = File(...)):
    try:
        # 클라이언트가 업로드한 이미지 메모리로 바로 읽기
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="유효하지 않은 이미지 이미지입니다.")

        # DeepFace 라이브러리를 사용해 성별 분석 수행
        # (첫 요청 시에는 모델 가중치를 다운로드하느라 약간의 시간이 걸릴 수 있습니다)
        analysis = DeepFace.analyze(img_path=img, actions=['gender'], enforce_detection=True)
        
        # 프레임 내에 여러 얼굴이 감지될 경우 첫 번째 얼굴을 기준
        if isinstance(analysis, list):
            result = analysis[0]
        else:
            result = analysis
            
        gender_dict = result.get('gender', {})
        # DeepFace는 'Man' 또는 'Woman'을 결과로 반환합니다
        dominant_gender = result.get('dominant_gender')
        
        return {
            "status": "success",
            "dominant_gender": dominant_gender,  # 최종 분류된 성별 (남자/여자)
            "confidence": gender_dict            # 성별에 대한 신뢰도(확률) 예측값
        }
        
    except ValueError as e:
        # 사진에서 얼굴을 찾지 못한 경우
        raise HTTPException(status_code=400, detail="사진에서 얼굴을 인식하지 못했습니다.")
    except Exception as e:
        # 기타 서버 에러
        raise HTTPException(status_code=500, detail=f"AI 분석 중 에러 발생: {str(e)}")
