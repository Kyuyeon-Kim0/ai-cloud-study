# ai-cloud-study

AI 서비스·클라우드 실무 학습 기록입니다.

## 폴더 구조

연도-월 → 날짜 → 주제별 코드와 README 순서로 정리합니다.

```text
ai-cloud-study/
├─ README.md
└─ 2026-09/
   ├─ 09-09/
   │  ├─ README.md
   │  ├─ hello.ps1
   │  ├─ system-monitor/
   │  ├─ tasks/
   │  └─ wallpaper/
   └─ 09-10/
      ├─ README.md
      ├─ restart_wifi.ps1
      ├─ tago-train-api/
      └─ 학습 자료.html
```

## 학습 기록

| 날짜 | 내용 |
|---|---|
| [2026-09-09](2026-09/09-09/README.md) | PowerShell 기초, 시스템 점검, 배경화면 변경 |
| [2026-09-10](2026-09/09-10/README.md) | 네트워크와 URL, JSON·XML, 공공데이터 API |

## 정리 규칙

- 월별 폴더는 `YYYY-MM`, 날짜 폴더는 `MM-DD`로 작성합니다.
- 날짜별 `README.md`에 배운 내용, 실습 설명, 실행 방법을 기록합니다.
- 짧은 실습은 날짜 폴더에, 여러 파일로 구성된 실습은 주제별 하위 폴더에 보관합니다.
- 다음 달부터 `2026-10`, `2026-11`처럼 월별 폴더를 만듭니다.
- API 키가 있는 `.env`, 가상환경, 캐시, 실행 로그는 커밋에서 제외합니다.
