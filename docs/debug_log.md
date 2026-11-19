# movision_kr 디버깅 로그

> 모든 디버깅/버그 수정 내역을 최신 항목이 위로 오도록 기록한다.
> 형식: 날짜 / 증상 / 원인 / 수정 내용 / 수정 파일 / 검증 상태

---

## 2026-11-19 — BLE 연결 끊김 직후 리부트 (nimble_host 스택 오버플로)

**증상**
- `Disconnected: reason=0x208` → `[DISPLAY] Switching to SPEEDOMETER Screen (Option: 0)` 직후
  `***ERROR*** A stack overflow in task nimble_host has been detected.` → PANIC 리부트.

**원인**
- `ble_mp_gap_event()`의 `BLE_GAP_EVENT_DISCONNECT`(9560행)에서 `switch_display_mode(DISPLAY_MODE_GUIDE)`를
  NimBLE 호스트 태스크에서 직접 호출. 속도계 화면 재구성(LVGL 객체 생성/폰트/이미지)은 스택을 많이 사용하는데
  `CONFIG_BT_NIMBLE_HOST_TASK_STACK_SIZE=4096`으로 부족해서 오버플로 발생.
- 0x208 = 감독 타임아웃(Supervision Timeout, 폰과의 링크 손실). 끊김 자체는 정상 이벤트이고 크래시를 일으킨 원인은 아님.
- 같은 위험: BLE 콜백 안에서 `switch_display_mode()`를 직접 호출하는 다른 경로(Speed/TBT/Safety 자동전환, 1671·1698·1738행 등).

**수정 내용**
- (2026-11-19 08:04) 재현 로그(LoadProhibited, `tlsf_walk_pool` 힙 손상)의 백트레이스로 원인 확정:
  `ble_mp_gap_event:9568 → switch_display_mode → lv_refr_now → PNG 디코딩 → LittleFS 읽기`가 모두 nimble_host 스택에서 실행됨.
- `switch_display_mode()`: NimBLE 호스트 태스크에서 호출되면 `s_pending_mode`에 요청만 기록하고 바로 반환.
  (`s_ble_host_task_handle`은 `ble_mp_host_task()` 시작 시 저장. 30여 개 호출 경로 전체에 적용됨)
- LVGL 태스크 메인 루프: `s_pending_mode`가 있으면 `lv_timer_handler()` 전에 실제 전환 실행 (manual 플래그 보존).
- `sdkconfig`: NimBLE 호스트 태스크 스택 4096 → 8192 (여유 확보).

**수정 파일**
- `main/main.c`: 약 417행(전역 변수), 약 7873행(`switch_display_mode` 지연 처리), 약 8809행(LVGL 루프), 약 9828행(호스트 태스크 핸들 저장)
- `sdkconfig`: `CONFIG_BT_NIMBLE_HOST_TASK_STACK_SIZE` 외 2개 항목

**검증 상태**
- [x] 원인 분석
- [x] 빌드
- [x] 실차 확인 (BLE 연결 끊김 후 속도계 전환 시 리부트 없음 확인) — 2026-11-19 08:32
  - `Disconnected: reason=0x213` → 즉시 `Advertising started` → 약 340ms 후 LVGL 태스크에서 `Switching to SPEEDOMETER` → 크래시 없음, 이후 재연결 정상.

**참고**
- 재현 조건: 가상운행 여부와 상관없이 **BLE 연결 끊김만으로 발생**. 두 번째 로그는 앱 미등록 상태에서 OS(iOS HID 본딩)가 자동 연결 → 앱 명령 없이 QR 화면 → 약 18초 뒤 연결 끊김(0x208) → 크래시.
- 첫 번째 로그의 장치 펌웨어는 Oct 5 빌드(ELF fb6598894)이고, 11-18 수정본은 아직 반영되지 않은 상태.
- 리부트 후 `BLE assert llc_con_upd.c 297`: BLE 컨트롤러가 연결 파라미터 업데이트 처리 중 assert. 별도 이슈이며 경과 관찰 필요.

---

## 2026-11-18 — 필드로그 점검 결과 1~3번 수정 (구간 0x21 / 제한속도 0 / 구간 중 AVG=0)

**증상**
1. 구간단속(data1=0x21) 중 section 아이콘 대신 speed 아이콘 표시 + 구간 전체에서 현재속도 과속 알람 활성.
2. data1=0x09, 제한속도 0 수신 시 존재하지 않는 "30" 속도표지 표시.
3. 구간 진행 중 앱이 AVG=0 송신 시 듀얼(현재/평균) 표시가 해제됨.

**원인**
1. 비트 우선순위상 speed(0x01) > section(0x20) → best_entry=speed, `s_current_safety_data1=0x01` → 알람 판정 `!= 0x20` 오판.
2. `_tt` 아이콘 선택 후 data2<30 을 30으로 클램프.
3. AVG=0 을 그대로 평균속도 리셋으로 처리.

**수정 내용**
1. `safety_drive()`: data1에 0x20 비트가 있고 제한속도≠0 이면 section 엔트리를 최우선 선택
   → section_tt 아이콘 표시, `s_current_safety_data1=0x20` 으로 알람 판정 정상화(800m 이내만 현재속도 알람).
2. `safety_drive()`: data2=0 이면 `_tt`(숫자표지) 엔트리 제외 → 0x09 는 ban.png 표시. 대체 아이콘 없으면 표시 생략.
3. `s_last_section_bit_ms` 추가: 0x20 비트 Safety 수신 시각 기록(data1=0 수신 시 리셋).
   `update_speed_label()`: 평균속도 표시 중 + 최근 5초(`SECTION_BIT_HOLD_MS`) 내 구간 비트 수신 상태에서 AVG=0 은 무시.

**수정 파일**
- `main/main.c`
  - 약 761행: `s_last_section_bit_ms`, `SECTION_BIT_HOLD_MS` 추가
  - 약 3845~3900행: `safety_drive()` 선택 로직
  - 약 4995행: `update_speed_label()` AVG=0 필터

**검증 상태**
- [x] 빌드 성공 (기존 경고만 존재)
- [x] 필드로그 재시뮬레이션: 0x21→section_tt 2,368건, 0x09(lim0)→ban 112건, AVG=0 무시 1건(48243행)
- [ ] 실차 확인

**참고**
- section_30~120.png 이미지 존재 확인 완료 (main/flash_data/image).
- 4번(어린이구역 복합 data1=0x05/0x07/0x0B 아이콘)은 미수정.

---

## 2026-11-18 — 필드 수신로그 점검 (G:\내 드라이브\JOB\BSD-round\field_log, 5개 파일, 약 7.3만 패킷)

**점검 방법**
- 전 패킷 형식 검증(헤더 0x19 / 길이 / 테일 0x2F): 형식 오류 0건.
- 펌웨어 로직(Safety_DRV 우선순위, 평균속도 상태, Clear 처리)을 Python으로 재현하여 시뮬레이션.
  스크립트: brain/scratch/`stats.py`, `sim.py`, `d1stat.py`, `dump.py`

**발견 사항 (모두 미수정)**
1. [높음] 구간단속 data1=0x21 (section 0x20 + speed 0x01) 처리 오류 — merged_log.txt 2,368건
   - 우선순위상 speed(2) > section(4) → 구간 내내 `speed_tt.png` 표시 (section 아이콘 미표시).
   - `s_current_safety_data1 = best_entry->data1 = 0x01` 저장 → `is_current_speed_alarm_enabled()`의
     `!= 0x20` 조건 상 "구간 내 일반 카메라"로 판정 → 구간 전체에서 현재속도 과속 알람 활성 (설계 의도: 800m 이내만).
   - 위치: `safety_drive()` 3849~3887행, `update_safety_image_for_data()` 3090행, 2977행.
2. [중간] data1=0x09, data2(제한속도)=0 — 전체 112건
   - speed_tt 선택 후 tt<30 → 30으로 클램프되어 **"30" 속도표지가 잘못 표시**됨 (실제 제한속도 없음).
   - 위치: 3128~3134행.
3. [중간] 구간 진행 중 앱이 `03/01 AVG=0` 송신 — merged_log.txt 48243행 (남은거리 7,080m)
   - 평균속도 0으로 리셋 → 다음 AVG 수신(48528행)까지 단독 현재속도로 복귀 (앱 측 원인 토글).
4. [낮음] data1=0x05/0x07/0x0B (어린이보호구역 + 신호/과속 복합) — children 아이콘 대신 signal/speed 아이콘 표시 (제한속도 30은 정상).
5. [참고] 구간 내 평균속도가 Clear/Safety data1=0 으로 지워지는 경우: 로그상 0건 (앞선 토글 이슈는 펌웨어 옵션0 버그가 원인임을 재확인).
6. [참고] 동일 data1에서 거리 급증(연속 카메라) 20건 — 아이콘 동일, 거리만 갱신되어 표시상 문제 없음.

**검증 상태**
- [x] 로그 시뮬레이션 분석
- [ ] 1~3번 수정 여부 결정

---

## 2026-11-18 — 구간단속 중 현재속도 ↔ 현재/평균 듀얼속도 빠른 토글 (속도계 옵션 0)

**증상**
- 구간단속 구간 주행 중 속도계 화면(아날로그 바늘, `s_speedometer_option == 0`)에서
  대형 단독 현재속도(예: "56")와 `현재속도 / 평균속도` 듀얼 표시가 빠르게 번갈아 표시됨.
- 사진상 두 표시가 겹쳐 보임 (안전정보 80 + 남은거리 1.5Km 표시 중).

**원인**
- `cmd 0x02 (Safety_DRV, data1≠0)` 수신 시 안전정보 갱신 경로에서 옵션 0일 때
  `s_speedometer_avr_speed_val` 확인 없이 `s_speedometer_speed_label`을 무조건 표시(`clear_flag`).
- 이어서 `cmd 0x03 (Speed)` 수신 시 `update_speedometer_section_control_ui()`가 다시 숨기고 듀얼 표시.
- 구간 내에서는 남은거리 갱신으로 Safety_DRV가 자주 수신되어 두 상태가 반복 → 토글.
- 옵션 1(디지털)은 이미 `avr_speed_val == 0` 조건이 있어 문제 없음.

**수정 내용**
- 옵션 0도 `s_speedometer_avr_speed_val > 0`(구간단속 중)이면 대형 단독 속도 라벨을 숨김 유지.

**수정 파일**
- `main/main.c`
  - Safety_DRV 처리 경로 2곳 (약 3392행, 3568행 부근)
  - 안전정보 클리어 경로 1곳 (약 4363행 부근)

**검증 상태**
- [ ] 빌드 확인
- [ ] 실차 구간단속 구간 확인

**참고 (잠재 이슈, 미수정)**
- `update_clear_display()`에서 `do_safety`와 `do_avr_speed` 조건이 동일(0x02/0x03/0x06/0x07)하여
  Safety_DRV `data1=0` 또는 Clear Display `0x02` 수신 시 구간 평균속도까지 함께 삭제됨.
  앱이 구간 내에서 이 패킷을 보내면 유사한 토글이 발생할 수 있음.

---

## 2026-11-18 — 기본 보드 movision_kr(R23)로 변경

**내용**
- `tools/apply_pin_config.py`: 기본값/`default` 별칭을 `mp` → `kr`로 변경.
- `build_all.bat`: 전체 빌드 후 복원 보드를 `mp` → `kr`로 변경.
- `main/board_config.h`: R23 핀맵 적용.

