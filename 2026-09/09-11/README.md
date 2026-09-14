# 2026-09-11 (금) 학습 기록

## 학습 주제

- HTML 기본 구조와 링크를 이용한 웹사이트 이동
- 외부 CSS 파일 연결과 여러 페이지에서의 스타일 재사용
- OpenCV와 MediaPipe를 활용한 얼굴 랜드마크 표시
- 눈 위치를 추적하여 이미지 효과를 실시간으로 합성하는 실습

## 핵심 이해

### HTML과 CSS

- HTML은 제목, 문단, 목록, 링크 등 웹페이지의 내용을 구성한다.
- `a` 태그의 `href` 속성으로 이동할 웹사이트 주소를 지정한다.
- `link` 태그로 외부 CSS 파일을 연결한다.
- 여러 HTML 파일이 하나의 CSS 파일을 공유하면 디자인을 한 곳에서 관리할 수 있다.

### 얼굴 랜드마크와 이미지 합성

- OpenCV로 웹캠 프레임이나 이미지 파일을 읽는다.
- MediaPipe Face Mesh로 얼굴의 주요 지점을 찾아 연결선과 번호를 표시한다.
- 눈의 위치, 폭, 각도를 이용해 합성 이미지의 위치와 크기 및 회전을 계산한다.
- 배경을 투명 처리한 이미지를 영상에 합성해 눈 불꽃 효과를 표현한다.

## 실습 파일

| 파일 또는 폴더 | 내용 |
|---|---|
| [index.html](index.html) | 네이버와 구글로 이동하는 링크 페이지 |
| [css-study/page1.html](css-study/page1.html) | 외부 CSS를 연결한 첫 번째 페이지 |
| [css-study/page2.html](css-study/page2.html) | 동일한 CSS를 공유하는 두 번째 페이지 |
| [css-study/style.css](css-study/style.css) | 두 페이지에 적용하는 공통 스타일 |
| [face_mesh_landmarks/](face_mesh_landmarks/README.md) | 얼굴 연결선과 랜드마크 번호 표시 |
| [mediapipe_eye_fire/](mediapipe_eye_fire/README.md) | 웹캠 얼굴 추적 및 양쪽 눈 불꽃 이미지 합성 |

## 실행 방법

- HTML 실습은 `index.html` 또는 `css-study`의 HTML 파일을 브라우저에서 연다.
- 얼굴 랜드마크 실습은 [설치 및 실행 안내](face_mesh_landmarks/README.md)를 따른다.
- 눈 불꽃 합성 실습은 [설치 및 실행 안내](mediapipe_eye_fire/README.md)를 따른다.
- Python 실습의 패키지는 각 폴더의 `requirements.txt`를 기준으로 설치한다.
