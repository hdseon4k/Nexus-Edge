PROGRAM main
VAR
	LED : bool AT %QX0.6; (* 푸시버튼 (입력) *)
	T1 : TON; (* 아두이노 내장 LED (출력) *)
	Blink_State : bool; (* 현재 깜빡임 상태 저장 *)
END_VAR

(* 1. 1초 타이머 설정: T1.Q가 False일 때 작동 시작, 1초 후 True 반환 *)
T1(IN := NOT T1.Q, PT := T#1s);

(* 2. 타이머가 완료(1초 경과)될 때마다 실행 *)
IF T1.Q THEN
    (* 내부 상태 값을 반전 (False -> True -> False) *)
    Blink_State := NOT Blink_State;
END_IF;

(* 3. 실제 아두이노 13번 핀(%QX0.6)으로 신호 전송 *)
LED := Blink_State;

END_PROGRAM