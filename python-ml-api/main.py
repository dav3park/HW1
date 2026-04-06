from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
import cv2
import numpy as np

app = FastAPI(title="Face Recognition ML API")

# 웹 브라우저에서 보낸 요청(업로드)을 서버가 안전하게 허락해주기 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용이므로 모든 도메인 접속 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        # DeepFace 라이브러리를 사용해 성별 및 인종 분석 동시 수행 (엔진 업데이트)
        # (새 모델 가중치(인종)를 다운로드하느라 약간의 시간이 걸릴 수 있습니다)
        analysis = DeepFace.analyze(img_path=img, actions=['gender', 'race'], enforce_detection=True)
        
        # 프레임 내에 여러 얼굴이 감지될 경우 첫 번째 얼굴을 기준
        if isinstance(analysis, list):
            result = analysis[0]
        else:
            result = analysis
            
        # 성별 결과 추출
        gender_dict = result.get('gender', {})
        dominant_gender = result.get('dominant_gender')
        
        # 인종 결과 추출
        race_dict = result.get('race', {})
        dominant_race = result.get('dominant_race')
        
        return {
            "status": "success",
            "dominant_gender": dominant_gender, 
            "gender_confidence": gender_dict,
            "dominant_race": dominant_race,
            "race_confidence": race_dict
        }
        
    except ValueError as e:
        # 사진에서 얼굴을 찾지 못한 경우
        raise HTTPException(status_code=400, detail="사진에서 얼굴을 인식하지 못했습니다.")
    except Exception as e:
        # 기타 서버 에러
        raise HTTPException(status_code=500, detail=f"AI 분석 중 에러 발생: {str(e)}")
